"""JSON serialization for ModelSpec IR (deterministic, round-trippable)."""

from __future__ import annotations

import json
from enum import Enum
from typing import Any

from velarium.ir import (
    FieldSpec,
    ModelConfig,
    ModelMetadata,
    ModelSpec,
    TypeKind,
    TypeSpec,
)


def _typespec_from_dict(d: dict[str, Any]) -> TypeSpec:
    args = d.get("args")
    if args is not None:
        args = [_typespec_from_dict(x) if isinstance(x, dict) else x for x in args]
    return TypeSpec(
        kind=TypeKind(d["kind"]),
        args=args,
        optional=d.get("optional", False),
        nullable=d.get("nullable", False),
        default=d.get("default", None),
        name=d.get("name"),
        qualname=d.get("qualname"),
        module=d.get("module"),
    )


def _json_default_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    try:
        json.dumps(value)
    except TypeError:
        return {"_velarium_repr": repr(value)}
    return value


def typespec_dedupe_key(ts: TypeSpec) -> str:
    """Stable string for structural equality of ``TypeSpec`` (union dedupe, caching).

    Matches the historical ``json.dumps(typespec_to_dict(ts), sort_keys=True)`` behavior
    with JSON serialization defaults for non-JSON-native field defaults.
    """
    return json.dumps(
        typespec_to_dict(ts),
        sort_keys=True,
        default=_json_default_value,
    )


def typespec_to_dict(ts: TypeSpec) -> dict[str, Any]:
    out: dict[str, Any] = {"kind": ts.kind.value}
    if ts.args is not None:
        out["args"] = [typespec_to_dict(a) for a in ts.args]
    if ts.optional:
        out["optional"] = True
    if ts.nullable:
        out["nullable"] = True
    if ts.default is not None:
        out["default"] = _json_default_value(ts.default)
    if ts.name is not None:
        out["name"] = ts.name
    if ts.qualname is not None:
        out["qualname"] = ts.qualname
    if ts.module is not None:
        out["module"] = ts.module
    return out


def typespec_from_dict(d: dict[str, Any]) -> TypeSpec:
    return _typespec_from_dict(d)


def model_spec_to_dict(m: ModelSpec) -> dict[str, Any]:
    out: dict[str, Any] = {
        "name": m.name,
        "fields": {k: typespec_to_dict(v) for k, v in m.fields.items()},
    }
    if m.config is not None:
        c = m.config
        out["config"] = {
            "frozen": c.frozen,
            "extra": c.extra,
            "validate_assignment": c.validate_assignment,
            "from_attributes": c.from_attributes,
            "strict": c.strict,
        }
    if m.metadata is not None:
        md = m.metadata
        out["metadata"] = {
            "source_module": md.source_module,
            "source_file": md.source_file,
            "line_number": md.line_number,
            "generated_by": md.generated_by,
            "version": md.version,
        }
    return out


def model_spec_from_dict(d: dict[str, Any]) -> ModelSpec:
    fields_raw = d.get("fields") or {}
    fields = {k: typespec_from_dict(v) for k, v in fields_raw.items()}
    config = None
    if "config" in d and d["config"] is not None:
        c = d["config"]
        config = ModelConfig(
            frozen=c.get("frozen", False),
            extra=c.get("extra", "forbid"),
            validate_assignment=c.get("validate_assignment", True),
            from_attributes=c.get("from_attributes", True),
            strict=c.get("strict", False),
        )
    metadata = None
    if "metadata" in d and d["metadata"] is not None:
        md = d["metadata"]
        metadata = ModelMetadata(
            source_module=md.get("source_module"),
            source_file=md.get("source_file"),
            line_number=md.get("line_number"),
            generated_by=md.get("generated_by", "velarium"),
            version=md.get("version"),
        )
    return ModelSpec(
        name=d["name"],
        fields=fields,
        config=config,
        metadata=metadata,
    )


def field_spec_to_dict(f: FieldSpec) -> dict[str, Any]:
    out: dict[str, Any] = {
        "name": f.name,
        "type": typespec_to_dict(f.type),
        "required": f.required,
        "default": f.default,
        "alias": f.alias,
        "description": f.description,
        "deprecated": f.deprecated,
    }
    return {
        k: v
        for k, v in out.items()
        if v is not None or k in ("name", "type", "required")
    }


def field_spec_from_dict(d: dict[str, Any]) -> FieldSpec:
    return FieldSpec(
        name=d["name"],
        type=typespec_from_dict(d["type"]),
        required=d["required"],
        default=d.get("default"),
        alias=d.get("alias"),
        description=d.get("description"),
        deprecated=d.get("deprecated", False),
    )


def dumps_model_spec(m: ModelSpec, *, indent: int | None = 2) -> str:
    """Serialize ModelSpec to JSON with stable key ordering."""
    return json.dumps(
        model_spec_to_dict(m),
        indent=indent,
        sort_keys=True,
        default=_json_default_value,
    )


def loads_model_spec(s: str) -> ModelSpec:
    return model_spec_from_dict(json.loads(s))
