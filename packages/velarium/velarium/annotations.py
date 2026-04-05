"""Map Python typing objects to TypeSpec (MVP subset)."""

from __future__ import annotations

import datetime
import typing
from collections.abc import Callable as CallableABC
from enum import Enum
from types import UnionType
from typing import Any, ForwardRef, TypeVar, Union, get_args, get_origin

from velarium.ir import TypeKind, TypeSpec
from velarium.normalize import normalize_typespec, optional_to_union


def _none() -> TypeSpec:
    return TypeSpec(kind=TypeKind.NONE)


def _merge_optional(ts: TypeSpec, *, optional: bool) -> TypeSpec:
    out = TypeSpec(
        kind=ts.kind,
        args=ts.args,
        optional=optional or ts.optional,
        nullable=ts.nullable,
        default=ts.default,
    )
    return optional_to_union(out) if out.optional else out


def type_to_typespec(
    t: Any,
    *,
    optional: bool = False,
) -> TypeSpec:
    """Convert a runtime typing object or builtin type to TypeSpec."""
    if t is type(None) or t is None:
        return _merge_optional(_none(), optional=optional)

    if t is Any or t is typing.Any:
        return _merge_optional(TypeSpec(kind=TypeKind.ANY), optional=optional)

    if isinstance(t, ForwardRef):
        return _merge_optional(TypeSpec(kind=TypeKind.ANY), optional=optional)

    if isinstance(t, str):
        return _merge_optional(TypeSpec(kind=TypeKind.ANY), optional=optional)

    origin = get_origin(t)
    args = get_args(t)

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
        parts = [type_to_typespec(a, optional=False) for a in args]
        has_none = any(p.kind == TypeKind.NONE for p in parts)
        u = TypeSpec(kind=TypeKind.UNION, args=parts)
        u = normalize_typespec(u)
        opt = optional or has_none
        if has_none:
            u.optional = True
        return _merge_optional(u, optional=opt)

    if origin is list or origin is typing.List:
        inner = (
            type_to_typespec(args[0], optional=False)
            if args
            else TypeSpec(kind=TypeKind.ANY)
        )
        return _merge_optional(
            TypeSpec(kind=TypeKind.LIST, args=[inner]), optional=optional
        )

    if origin is dict or origin is typing.Dict:
        k = (
            type_to_typespec(args[0], optional=False)
            if len(args) > 0
            else TypeSpec(kind=TypeKind.ANY)
        )
        v = (
            type_to_typespec(args[1], optional=False)
            if len(args) > 1
            else TypeSpec(kind=TypeKind.ANY)
        )
        return _merge_optional(
            TypeSpec(kind=TypeKind.DICT, args=[k, v]), optional=optional
        )

    if origin is set or origin is typing.Set:
        inner = (
            type_to_typespec(args[0], optional=False)
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
            inner = type_to_typespec(args[0], optional=False)
            return _merge_optional(
                TypeSpec(kind=TypeKind.TUPLE, args=[inner]), optional=optional
            )
        inners = [type_to_typespec(a, optional=False) for a in args]
        return _merge_optional(
            TypeSpec(kind=TypeKind.TUPLE, args=inners), optional=optional
        )

    if origin is typing.Callable or origin is CallableABC:
        if args:
            param_args, ret = args[0], args[1]
            if (
                get_origin(param_args) is list
            ):  # pragma: no cover — rare Callable[..., T] shape; else path covers real callables
                plist = get_args(param_args)
                plist_ts = TypeSpec(
                    kind=TypeKind.LIST,
                    args=[type_to_typespec(p, optional=False) for p in plist],
                )
            else:
                plist_ts = type_to_typespec(param_args, optional=False)
            ret_ts = type_to_typespec(ret, optional=False)
            return _merge_optional(
                TypeSpec(kind=TypeKind.CALLABLE, args=[plist_ts, ret_ts]),
                optional=optional,
            )
        return _merge_optional(
            TypeSpec(kind=TypeKind.CALLABLE, args=None), optional=optional
        )

    if isinstance(t, TypeVar):
        return _merge_optional(TypeSpec(kind=TypeKind.TYPE_VAR), optional=optional)

    if origin is not None:
        if args:
            inner_args = [type_to_typespec(a, optional=False) for a in args]
            return _merge_optional(
                TypeSpec(kind=TypeKind.GENERIC, args=inner_args), optional=optional
            )
        return _merge_optional(
            TypeSpec(kind=TypeKind.GENERIC, args=[]), optional=optional
        )

    if isinstance(t, type):
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
        return _merge_optional(TypeSpec(kind=TypeKind.ANY), optional=optional)

    return _merge_optional(TypeSpec(kind=TypeKind.ANY), optional=optional)


def annotation_to_typespec(
    annotation: Any, *, globalns: dict[str, Any] | None = None
) -> TypeSpec:
    """Resolve string annotations and return TypeSpec."""
    if isinstance(annotation, str):
        if globalns is None:
            return TypeSpec(kind=TypeKind.ANY)
        try:
            anno = eval(annotation, globalns, globalns)  # noqa: S307
            return normalize_typespec(type_to_typespec(anno, optional=False))
        except Exception:
            return TypeSpec(kind=TypeKind.ANY)
    return normalize_typespec(type_to_typespec(annotation, optional=False))
