"""Build ModelSpec from Python classes (dataclasses MVP)."""

from __future__ import annotations

import dataclasses
import inspect
from typing import Any

from typing_extensions import is_typeddict

from velarium.annotations import annotation_to_typespec, type_to_typespec
from velarium.ir import ModelConfig, ModelMetadata, ModelSpec, TypeSpec
from velarium.normalize import normalize_typespec
from velarium.typing_resolve import get_resolved_hints, module_globals_for_class


def _module_globals(cls: type) -> dict[str, Any]:
    """Backward-compatible alias for :func:`module_globals_for_class`."""
    return module_globals_for_class(cls)


def modelspec_from_dataclass(cls: type, *, include_extras: bool = True) -> ModelSpec:
    """Extract ModelSpec from a dataclass type."""
    if not dataclasses.is_dataclass(cls):
        raise TypeError(f"{cls!r} is not a dataclass")

    globalns = module_globals_for_class(cls)
    hints = get_resolved_hints(cls, include_extras=include_extras)

    fields: dict[str, TypeSpec] = {}
    for f in dataclasses.fields(cls):
        if not f.init:
            continue
        raw = hints.get(f.name, f.type if hasattr(f, "type") else Any)
        ts = annotation_to_typespec(raw, globalns=globalns)
        ts = normalize_typespec(ts)
        if f.default is not dataclasses.MISSING:
            ts = TypeSpec(
                kind=ts.kind,
                args=ts.args,
                optional=ts.optional,
                nullable=ts.nullable,
                default=f.default,
                name=ts.name,
                qualname=ts.qualname,
                module=ts.module,
            )
        fields[f.name] = ts

    src_file = None
    line_number = None
    try:
        src_file = inspect.getsourcefile(cls)
        lines, start = inspect.getsourcelines(cls)
        line_number = start
    except (OSError, TypeError):
        pass

    meta = ModelMetadata(
        source_module=cls.__module__,
        source_file=src_file,
        line_number=line_number,
        generated_by="velarium",
        version=None,
    )
    params = getattr(cls, "__dataclass_params__", None)
    frozen = bool(getattr(params, "frozen", False)) if params is not None else False
    cfg = ModelConfig(frozen=frozen, extra="forbid")

    return ModelSpec(name=cls.__name__, fields=fields, config=cfg, metadata=meta)


def modelspec_from_typed_dict(cls: type, *, include_extras: bool = True) -> ModelSpec:
    """Extract ModelSpec from typing.TypedDict (required / optional keys per PEP 589)."""
    if not is_typeddict(cls):
        raise TypeError(f"{cls!r} is not a TypedDict")

    hints = get_resolved_hints(cls, include_extras=include_extras)
    opt_keys = getattr(cls, "__optional_keys__", None)

    fields: dict[str, TypeSpec] = {}
    for name, typ in getattr(cls, "__annotations__", {}).items():
        raw = hints.get(name, typ)
        ts = annotation_to_typespec(raw, globalns=module_globals_for_class(cls))
        ts = normalize_typespec(ts)
        if opt_keys is not None and name in opt_keys:
            ts = TypeSpec(
                kind=ts.kind,
                args=ts.args,
                optional=True,
                nullable=ts.nullable,
                default=ts.default,
                name=ts.name,
                qualname=ts.qualname,
                module=ts.module,
            )
            ts = normalize_typespec(ts)
        fields[name] = ts

    meta = ModelMetadata(source_module=cls.__module__, generated_by="velarium")
    return ModelSpec(name=cls.__name__, fields=fields, config=None, metadata=meta)


def typespec_from_object(obj: Any) -> TypeSpec:
    """Convenience: typing object or type -> TypeSpec."""
    return normalize_typespec(type_to_typespec(obj, optional=False))
