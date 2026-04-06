"""JSON serialization for ModelSpec IR (deterministic, round-trippable)."""

from __future__ import annotations

import json
import os
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

# Monotonic integer: bump when the top-level ModelSpec JSON shape changes incompatibly.
MODEL_SPEC_FORMAT_VERSION = 1

_DEFAULT_MAX_DEPTH = 256


def _validate_format_version(d: dict[str, Any]) -> None:
    raw = d.get("format_version", 1)
    if raw is None:
        raw = 1
    # JSON ``number`` deserializes to ``int`` or ``float``; reject ``bool`` (``bool`` is a
    # subclass of ``int`` in Python, so ``isinstance(True, int)`` is misleading).
    if type(raw) is not int:
        raise ValueError(
            f"ModelSpec JSON format_version must be int, got {type(raw).__name__}"
        )
    if raw < 1:
        raise ValueError(f"ModelSpec JSON format_version must be >= 1, got {raw}")
    if raw > MODEL_SPEC_FORMAT_VERSION:
        raise ValueError(
            f"Unsupported ModelSpec JSON format_version {raw}; "
            f"this velarium supports up to {MODEL_SPEC_FORMAT_VERSION}"
        )


def _max_depth_from_env() -> int:
    raw = os.environ.get("VELARIUM_JSON_MAX_DEPTH")
    if raw is None or not raw.strip():
        return _DEFAULT_MAX_DEPTH
    try:
        v = int(raw.strip())
    except ValueError:
        return _DEFAULT_MAX_DEPTH
    return max(1, v)


def json_input_byte_limit() -> int | None:
    """Return ``VELARIUM_JSON_MAX_BYTES`` if set to a positive integer, else ``None`` (no limit)."""
    raw = os.environ.get("VELARIUM_JSON_MAX_BYTES")
    if raw is None or not raw.strip():
        return None
    try:
        v = int(raw.strip())
    except ValueError:
        return None
    return v if v > 0 else None


def _check_utf8_byte_limit(s: str) -> None:
    limit = json_input_byte_limit()
    if limit is None:
        return
    n = len(s.encode("utf-8"))
    if n > limit:
        raise ValueError(
            f"ModelSpec JSON exceeds maximum size ({n} bytes > {limit} bytes); "
            "adjust VELARIUM_JSON_MAX_BYTES or unset it to disable the cap"
        )


def _typespec_from_dict(
    d: dict[str, Any],
    *,
    depth: int,
    max_depth: int,
) -> TypeSpec:
    if depth > max_depth:
        raise ValueError(
            f"TypeSpec nesting exceeds maximum depth ({max_depth}); "
            "set VELARIUM_JSON_MAX_DEPTH to increase"
        )
    args = d.get("args")
    if args is not None:
        next_depth = depth + 1
        args = [
            _typespec_from_dict(x, depth=next_depth, max_depth=max_depth)
            if isinstance(x, dict)
            else x
            for x in args
        ]
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


def typespec_from_dict(
    d: dict[str, Any],
    *,
    depth: int = 0,
    max_depth: int | None = None,
) -> TypeSpec:
    md = max_depth if max_depth is not None else _max_depth_from_env()
    return _typespec_from_dict(d, depth=depth, max_depth=md)


def model_spec_to_dict(m: ModelSpec) -> dict[str, Any]:
    out: dict[str, Any] = {
        "format_version": MODEL_SPEC_FORMAT_VERSION,
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


def model_spec_from_dict(
    d: dict[str, Any], *, max_depth: int | None = None
) -> ModelSpec:
    _validate_format_version(d)
    md = max_depth if max_depth is not None else _max_depth_from_env()
    fields_raw = d.get("fields") or {}
    fields = {
        k: _typespec_from_dict(v, depth=0, max_depth=md) for k, v in fields_raw.items()
    }
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


def field_spec_from_dict(
    d: dict[str, Any], *, max_depth: int | None = None
) -> FieldSpec:
    md = max_depth if max_depth is not None else _max_depth_from_env()
    return FieldSpec(
        name=d["name"],
        type=_typespec_from_dict(d["type"], depth=0, max_depth=md),
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
    _check_utf8_byte_limit(s)
    return model_spec_from_dict(json.loads(s))
