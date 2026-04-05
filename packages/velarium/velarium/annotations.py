"""Map Python typing objects to TypeSpec (Phase 0.2 coverage)."""

from __future__ import annotations

import datetime
import typing
from collections.abc import Callable as CallableABC
from enum import Enum
from types import UnionType
from typing import (
    Any,
    ClassVar,
    Final,
    ForwardRef,
    Protocol,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

from typing_extensions import Annotated, NotRequired, Required

from velarium.ir import TypeKind, TypeSpec
from velarium.normalize import normalize_typespec, optional_to_union
from velarium.typing_resolve import evaluate_forward_ref


def _none() -> TypeSpec:
    return TypeSpec(kind=TypeKind.NONE)


def _merge_optional(
    ts: TypeSpec,
    *,
    optional: bool,
) -> TypeSpec:
    out = TypeSpec(
        kind=ts.kind,
        args=ts.args,
        optional=optional or ts.optional,
        nullable=ts.nullable,
        default=ts.default,
        name=ts.name,
        qualname=ts.qualname,
        module=ts.module,
    )
    return optional_to_union(out) if out.optional else out


def type_to_typespec(
    t: Any,
    *,
    optional: bool = False,
    globalns: dict[str, Any] | None = None,
    localns: dict[str, Any] | None = None,
) -> TypeSpec:
    """Convert a runtime typing object or builtin type to TypeSpec."""
    if t is type(None) or t is None:
        return _merge_optional(_none(), optional=optional)

    if t is Any or t is typing.Any:
        return _merge_optional(TypeSpec(kind=TypeKind.ANY), optional=optional)

    origin = get_origin(t)
    args = get_args(t)

    if origin is Annotated and args:
        return type_to_typespec(
            args[0], optional=optional, globalns=globalns, localns=localns
        )

    if origin is Final and args:
        return type_to_typespec(
            args[0], optional=optional, globalns=globalns, localns=localns
        )

    if origin is ClassVar and args:
        return type_to_typespec(
            args[0], optional=optional, globalns=globalns, localns=localns
        )

    if origin is NotRequired and args:
        inner = type_to_typespec(
            args[0], optional=False, globalns=globalns, localns=localns
        )
        return _merge_optional(inner, optional=True)

    if origin is Required and args:
        return type_to_typespec(
            args[0], optional=optional, globalns=globalns, localns=localns
        )

    if isinstance(t, ForwardRef):
        if globalns is None:
            return _merge_optional(TypeSpec(kind=TypeKind.ANY), optional=optional)
        try:
            ev = evaluate_forward_ref(t, globalns, localns)
            return type_to_typespec(
                ev, optional=optional, globalns=globalns, localns=localns
            )
        except Exception:
            return _merge_optional(TypeSpec(kind=TypeKind.ANY), optional=optional)

    if isinstance(t, str):
        if globalns is None:
            return _merge_optional(TypeSpec(kind=TypeKind.ANY), optional=optional)
        try:
            fr = ForwardRef(t, module=globalns.get("__name__"))
            ev = evaluate_forward_ref(fr, globalns, localns)
            return type_to_typespec(
                ev, optional=optional, globalns=globalns, localns=localns
            )
        except Exception:
            return _merge_optional(TypeSpec(kind=TypeKind.ANY), optional=optional)

    if origin is typing.Literal:
        parts: list[TypeSpec] = []
        for a in args:
            parts.append(TypeSpec(kind=TypeKind.LITERAL, default=a))
        if len(parts) == 1:
            u = parts[0]
        else:
            u = TypeSpec(kind=TypeKind.UNION, args=parts)
        return _merge_optional(normalize_typespec(u), optional=optional)

    if origin is UnionType or origin is Union:
        parts = [
            type_to_typespec(a, optional=False, globalns=globalns, localns=localns)
            for a in args
        ]
        has_none = any(p.kind == TypeKind.NONE for p in parts)
        u = TypeSpec(kind=TypeKind.UNION, args=parts)
        u = normalize_typespec(u)
        opt = optional or has_none
        if has_none:
            u.optional = True
        return _merge_optional(u, optional=opt)

    if origin is list or origin is typing.List:
        inner = (
            type_to_typespec(
                args[0], optional=False, globalns=globalns, localns=localns
            )
            if args
            else TypeSpec(kind=TypeKind.ANY)
        )
        return _merge_optional(
            TypeSpec(kind=TypeKind.LIST, args=[inner]), optional=optional
        )

    if origin is dict or origin is typing.Dict:
        k = (
            type_to_typespec(
                args[0], optional=False, globalns=globalns, localns=localns
            )
            if len(args) > 0
            else TypeSpec(kind=TypeKind.ANY)
        )
        v = (
            type_to_typespec(
                args[1], optional=False, globalns=globalns, localns=localns
            )
            if len(args) > 1
            else TypeSpec(kind=TypeKind.ANY)
        )
        return _merge_optional(
            TypeSpec(kind=TypeKind.DICT, args=[k, v]), optional=optional
        )

    if origin is set or origin is typing.Set:
        inner = (
            type_to_typespec(
                args[0], optional=False, globalns=globalns, localns=localns
            )
            if args
            else TypeSpec(kind=TypeKind.ANY)
        )
        return _merge_optional(
            TypeSpec(kind=TypeKind.SET, args=[inner]), optional=optional
        )

    if origin is tuple or origin is typing.Tuple:
        if not args:
            inner = TypeSpec(kind=TypeKind.ANY)
            return _merge_optional(
                TypeSpec(kind=TypeKind.TUPLE, args=[inner]), optional=optional
            )
        if len(args) == 2 and args[1] is Ellipsis:
            inner = type_to_typespec(
                args[0], optional=False, globalns=globalns, localns=localns
            )
            return _merge_optional(
                TypeSpec(kind=TypeKind.TUPLE, args=[inner]), optional=optional
            )
        inners = [
            type_to_typespec(a, optional=False, globalns=globalns, localns=localns)
            for a in args
        ]
        return _merge_optional(
            TypeSpec(kind=TypeKind.TUPLE, args=inners), optional=optional
        )

    if origin is typing.Callable or origin is CallableABC:
        if args:
            param_args, ret = args[0], args[1]
            # Callable[[T, U], R] exposes the parameter list as a concrete list, not list[T].
            if isinstance(param_args, list):
                plist = get_args(param_args)
                plist_ts = TypeSpec(
                    kind=TypeKind.LIST,
                    args=[
                        type_to_typespec(
                            p, optional=False, globalns=globalns, localns=localns
                        )
                        for p in plist
                    ],
                )
            else:
                plist_ts = type_to_typespec(
                    param_args, optional=False, globalns=globalns, localns=localns
                )
            ret_ts = type_to_typespec(
                ret, optional=False, globalns=globalns, localns=localns
            )
            return _merge_optional(
                TypeSpec(kind=TypeKind.CALLABLE, args=[plist_ts, ret_ts]),
                optional=optional,
            )
        return _merge_optional(
            TypeSpec(kind=TypeKind.CALLABLE, args=None), optional=optional
        )

    # ParamSpec / TypeVarTuple before TypeVar: on Python 3.10, TypeVarTuple can be
    # isinstance(..., TypeVar) but has no __bound__ (see test_param_spec_and_typevar_tuple).
    if type(t).__name__ == "ParamSpec":
        return _merge_optional(
            TypeSpec(kind=TypeKind.PARAM_SPEC, name=getattr(t, "__name__", None)),
            optional=optional,
        )

    if type(t).__name__ == "TypeVarTuple":
        return _merge_optional(
            TypeSpec(kind=TypeKind.TYPE_VAR_TUPLE, name=getattr(t, "__name__", None)),
            optional=optional,
        )

    if isinstance(t, TypeVar):
        bound_args: list[TypeSpec] | None = None
        if t.__bound__ is not None:
            bound_args = [
                type_to_typespec(
                    t.__bound__, optional=False, globalns=globalns, localns=localns
                )
            ]
        return _merge_optional(
            TypeSpec(
                kind=TypeKind.TYPE_VAR,
                args=bound_args,
                name=getattr(t, "__name__", None),
            ),
            optional=optional,
        )

    if origin is not None:
        if args:
            inner_args = [
                type_to_typespec(a, optional=False, globalns=globalns, localns=localns)
                for a in args
            ]
            return _merge_optional(
                TypeSpec(kind=TypeKind.GENERIC, args=inner_args), optional=optional
            )
        return _merge_optional(
            TypeSpec(kind=TypeKind.GENERIC, args=[]), optional=optional
        )

    if isinstance(t, type):
        if t in (list, dict, set):
            return _merge_optional(TypeSpec(kind=TypeKind.ANY), optional=optional)
        if t is CallableABC:
            return _merge_optional(
                TypeSpec(kind=TypeKind.CALLABLE, args=None), optional=optional
            )
        if t is int:
            return _merge_optional(TypeSpec(kind=TypeKind.INT), optional=optional)
        if t is float:
            return _merge_optional(TypeSpec(kind=TypeKind.FLOAT), optional=optional)
        if t is bool:
            return _merge_optional(TypeSpec(kind=TypeKind.BOOL), optional=optional)
        if t is str:
            return _merge_optional(TypeSpec(kind=TypeKind.STR), optional=optional)
        if t is bytes:
            return _merge_optional(TypeSpec(kind=TypeKind.BYTES), optional=optional)
        if t is datetime.datetime:
            return _merge_optional(TypeSpec(kind=TypeKind.DATETIME), optional=optional)
        if t is datetime.date:
            return _merge_optional(TypeSpec(kind=TypeKind.DATE), optional=optional)
        if t is datetime.time:
            return _merge_optional(TypeSpec(kind=TypeKind.TIME), optional=optional)
        if issubclass(t, Enum):
            members = [TypeSpec(kind=TypeKind.LITERAL, default=m.value) for m in t]
            u = (
                TypeSpec(kind=TypeKind.ENUM, args=members)
                if members
                else TypeSpec(kind=TypeKind.ANY)
            )
            return _merge_optional(u, optional=optional)
        if t is not Protocol and issubclass(t, Protocol):
            return _merge_optional(
                TypeSpec(
                    kind=TypeKind.PROTOCOL,
                    qualname=t.__qualname__,
                    module=t.__module__,
                ),
                optional=optional,
            )
        return _merge_optional(
            TypeSpec(
                kind=TypeKind.NOMINAL,
                qualname=t.__qualname__,
                module=t.__module__,
            ),
            optional=optional,
        )

    return _merge_optional(TypeSpec(kind=TypeKind.ANY), optional=optional)


def annotation_to_typespec(
    annotation: Any,
    *,
    globalns: dict[str, Any] | None = None,
    localns: dict[str, Any] | None = None,
) -> TypeSpec:
    """Resolve string annotations and return TypeSpec."""
    if isinstance(annotation, str):
        if globalns is None:
            return TypeSpec(kind=TypeKind.ANY)
        try:
            fr = ForwardRef(annotation, module=globalns.get("__name__"))
            ev = evaluate_forward_ref(fr, globalns, localns)
            return normalize_typespec(
                type_to_typespec(ev, optional=False, globalns=globalns, localns=localns)
            )
        except Exception:
            try:
                anno = eval(annotation, globalns, globalns)  # noqa: S307
                return normalize_typespec(
                    type_to_typespec(
                        anno, optional=False, globalns=globalns, localns=localns
                    )
                )
            except Exception:
                return TypeSpec(kind=TypeKind.ANY)
    return normalize_typespec(
        type_to_typespec(annotation, optional=False, globalns=globalns, localns=localns)
    )
