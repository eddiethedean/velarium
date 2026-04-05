"""Build ModelSpec from Pydantic v2 ``BaseModel`` (optional dependency)."""

from __future__ import annotations

from typing import Any, Literal

from velarium.annotations import annotation_to_typespec
from velarium.ir import ModelConfig, ModelSpec, TypeSpec
from velarium.model_metadata import metadata_for_class
from velarium.normalize import normalize_typespec
from velarium.typing_resolve import get_resolved_hints, module_globals_for_class


def _model_config_from_pydantic(cls: type[Any]) -> ModelConfig:
    raw = getattr(cls, "model_config", None)
    frozen = False
    extra: Literal["allow", "forbid", "ignore"] = "forbid"
    if raw is None:
        return ModelConfig(frozen=frozen, extra=extra)
    if isinstance(raw, dict):
        frozen = bool(raw.get("frozen", False))
        ev = raw.get("extra", "forbid")
    else:
        frozen = bool(getattr(raw, "frozen", False))
        ev = getattr(raw, "extra", "forbid")
    if ev in ("allow", "forbid", "ignore"):
        extra = ev
    return ModelConfig(frozen=frozen, extra=extra)


def modelspec_from_pydantic_model(
    cls: type[Any],
    *,
    include_extras: bool = True,
) -> ModelSpec:
    """Extract ModelSpec from a Pydantic v2 ``BaseModel`` subclass.

    Requires ``pip install velarium[pydantic]`` (or ``pydantic`` in the environment).

    **Policy:** ``TypeSpec`` comes from resolved **annotations** (same as dataclass builders).
    **Static defaults** are copied onto ``TypeSpec.default`` when present; **default_factory**
    is not evaluated and leaves no default in IR. **Field constraints** (``Field(ge=…)``, etc.)
    are not represented in IR (lossy).
    """
    try:
        from pydantic import BaseModel
    except ImportError as e:  # pragma: no cover — exercised when pydantic absent
        raise ImportError(
            "modelspec_from_pydantic_model requires pydantic; install velarium[pydantic]"
        ) from e

    if not isinstance(cls, type) or not issubclass(cls, BaseModel):
        raise TypeError(f"{cls!r} is not a Pydantic v2 BaseModel subclass")

    from pydantic_core import PydanticUndefined

    globalns = module_globals_for_class(cls)
    hints = get_resolved_hints(cls, include_extras=include_extras)

    fields: dict[str, TypeSpec] = {}
    for name, finfo in cls.model_fields.items():
        raw = hints.get(name, finfo.annotation)
        ts = annotation_to_typespec(raw, globalns=globalns)
        ts = normalize_typespec(ts)
        has_factory = getattr(finfo, "default_factory", None) is not None
        if not has_factory and finfo.default is not PydanticUndefined:
            ts = TypeSpec(
                kind=ts.kind,
                args=ts.args,
                optional=ts.optional,
                nullable=ts.nullable,
                default=finfo.default,
                name=ts.name,
                qualname=ts.qualname,
                module=ts.module,
            )
        fields[name] = ts

    cfg = _model_config_from_pydantic(cls)
    meta = metadata_for_class(cls, include_source=True)
    return ModelSpec(name=cls.__name__, fields=fields, config=cfg, metadata=meta)
