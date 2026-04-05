"""Build ModelSpec from Python classes (dataclasses MVP)."""

from __future__ import annotations

import dataclasses
import inspect
import sys
from typing import Any, get_type_hints

from typing_extensions import is_typeddict

from velarium.annotations import annotation_to_typespec, type_to_typespec
from velarium.ir import ModelConfig, ModelMetadata, ModelSpec, TypeSpec
from velarium.normalize import normalize_typespec


def _module_globals(cls: type) -> dict[str, Any]:
    mod = sys.modules.get(cls.__module__)
    if mod is None:
        return dict(vars(cls))
    g = dict(vars(mod))
    g.setdefault(cls.__name__, cls)
    return g


def modelspec_from_dataclass(cls: type, *, include_extras: bool = False) -> ModelSpec:
    """Extract ModelSpec from a dataclass type."""
    if not dataclasses.is_dataclass(cls):
        raise TypeError(f"{cls!r} is not a dataclass")

    globalns = _module_globals(cls)
    try:
        hints = get_type_hints(
            cls, globalns=globalns, localns=None, include_extras=include_extras
        )
    except Exception:
        hints = {}

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


def modelspec_from_typed_dict(cls: type) -> ModelSpec:
    """Extract ModelSpec from typing.TypedDict (total fields only for MVP)."""
    if not is_typeddict(cls):
        raise TypeError(f"{cls!r} is not a TypedDict")

    globalns = _module_globals(cls)
    try:
        hints = get_type_hints(cls, globalns=globalns)
    except Exception:
        hints = {}

    fields: dict[str, TypeSpec] = {}
    for name, typ in getattr(cls, "__annotations__", {}).items():
        ts = annotation_to_typespec(hints.get(name, typ), globalns=globalns)
        fields[name] = normalize_typespec(ts)

    meta = ModelMetadata(source_module=cls.__module__, generated_by="velarium")
    return ModelSpec(name=cls.__name__, fields=fields, config=None, metadata=meta)


def typespec_from_object(obj: Any) -> TypeSpec:
    """Convenience: typing object or type -> TypeSpec."""
    return normalize_typespec(type_to_typespec(obj, optional=False))
