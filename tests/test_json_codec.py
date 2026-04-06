"""Tests for velotype.json_codec."""

from __future__ import annotations

import json
from enum import Enum

import pytest

from velotype.ir import (
    FieldSpec,
    ModelConfig,
    ModelMetadata,
    ModelSpec,
    TypeKind,
    TypeSpec,
)
from velotype.json_codec import (
    MODEL_SPEC_FORMAT_VERSION,
    dumps_model_spec,
    field_spec_from_dict,
    field_spec_to_dict,
    loads_model_spec,
    model_spec_from_dict,
    model_spec_to_dict,
    typespec_from_dict,
    typespec_to_dict,
)


class _E(Enum):
    A = 1


def test_typespec_non_dict_arg_in_args_passthrough() -> None:
    """Covers _typespec_from_dict branch when an arg is not a nested dict."""
    d = {"kind": "list", "args": ["not_a_dict"]}
    ts = typespec_from_dict(d)
    assert ts.args == ["not_a_dict"]


def test_json_default_value_non_serializable_enum_and_object() -> None:
    ts = TypeSpec(kind=TypeKind.INT, default=_E.A)
    out = typespec_to_dict(ts)
    assert out["default"] == 1

    class _ArbitraryObject:
        pass

    ts2 = TypeSpec(kind=TypeKind.INT, default=_ArbitraryObject())
    out2 = typespec_to_dict(ts2)
    assert "_velarium_repr" in out2["default"]


def test_model_spec_full_roundtrip_with_config_and_metadata() -> None:
    m = ModelSpec(
        name="M",
        fields={"x": TypeSpec(kind=TypeKind.STR)},
        config=ModelConfig(frozen=True, extra="ignore"),
        metadata=ModelMetadata(
            source_module="mod",
            source_file="/a.py",
            line_number=10,
            generated_by="test",
            version="1",
        ),
    )
    s = dumps_model_spec(m, indent=None)
    m2 = loads_model_spec(s)
    assert m2.name == "M"
    assert (
        m2.config is not None
        and m2.config.frozen is True
        and m2.config.extra == "ignore"
    )
    assert m2.metadata is not None and m2.metadata.source_file == "/a.py"


def test_model_spec_from_dict_minimal_metadata_branch() -> None:
    d = {
        "name": "X",
        "fields": {},
        "metadata": {"generated_by": "legacy"},
    }
    m = model_spec_from_dict(d)
    assert m.metadata is not None
    assert m.metadata.generated_by == "legacy"


def test_dumps_includes_format_version() -> None:
    m = ModelSpec(name="A", fields={})
    data = json.loads(dumps_model_spec(m, indent=None))
    assert data["format_version"] == MODEL_SPEC_FORMAT_VERSION == 1


def test_model_spec_to_dict_includes_format_version() -> None:
    m = ModelSpec(name="B", fields={"x": TypeSpec(kind=TypeKind.STR)})
    d = model_spec_to_dict(m)
    assert d["format_version"] == MODEL_SPEC_FORMAT_VERSION
    assert d["name"] == "B"


def test_legacy_json_without_format_version_loads_and_redump_matches_canonical() -> (
    None
):
    """Pre-0.8 snapshots omit ``format_version``; loading treats them as version 1."""
    legacy = json.dumps({"name": "Legacy", "fields": {}}, sort_keys=True)
    m = loads_model_spec(legacy)
    assert m.name == "Legacy"
    canonical = json.loads(dumps_model_spec(m, indent=None))
    assert canonical["format_version"] == 1
    assert loads_model_spec(json.dumps(canonical, sort_keys=True)) == m


def test_explicit_format_version_one_matches_omitted() -> None:
    omitted = model_spec_from_dict({"name": "X", "fields": {}})
    explicit = model_spec_from_dict({"format_version": 1, "name": "X", "fields": {}})
    assert omitted == explicit


def test_roundtrip_preserves_model_after_format_version_injection() -> None:
    """Parsed dict may omit ``format_version``; ``model_spec_from_dict`` is stable."""
    m = ModelSpec(name="Inject", fields={"n": TypeSpec(kind=TypeKind.INT)})
    data = json.loads(dumps_model_spec(m, indent=None))
    assert data.pop("format_version") == MODEL_SPEC_FORMAT_VERSION
    m2 = model_spec_from_dict(data)
    assert m2 == m


def test_model_spec_from_dict_rejects_unsupported_format_version() -> None:
    d = {
        "format_version": 999,
        "name": "X",
        "fields": {},
    }
    with pytest.raises(ValueError, match="Unsupported ModelSpec JSON format_version"):
        model_spec_from_dict(d)


def test_model_spec_from_dict_rejects_non_int_format_version() -> None:
    with pytest.raises(ValueError, match="format_version must be int"):
        model_spec_from_dict({"format_version": "1", "name": "X", "fields": {}})


def test_model_spec_from_dict_rejects_bool_format_version() -> None:
    """JSON booleans are not valid ``format_version`` (``bool`` subclasses ``int``)."""
    with pytest.raises(ValueError, match="format_version must be int"):
        model_spec_from_dict({"format_version": True, "name": "X", "fields": {}})
    with pytest.raises(ValueError, match="format_version must be int"):
        model_spec_from_dict({"format_version": False, "name": "X", "fields": {}})


def test_model_spec_from_dict_rejects_float_format_version() -> None:
    with pytest.raises(ValueError, match="format_version must be int"):
        model_spec_from_dict({"format_version": 1.0, "name": "X", "fields": {}})


def test_model_spec_from_dict_format_version_null_treated_as_one() -> None:
    m = model_spec_from_dict(
        {"format_version": None, "name": "Y", "fields": {"z": {"kind": "int"}}}
    )
    assert m.name == "Y"


def test_model_spec_from_dict_rejects_format_version_below_one() -> None:
    with pytest.raises(ValueError, match="must be >= 1"):
        model_spec_from_dict({"format_version": 0, "name": "X", "fields": {}})


def test_field_spec_roundtrip() -> None:
    f = FieldSpec(
        name="f",
        type=TypeSpec(kind=TypeKind.INT),
        required=True,
        default=3,
        alias="alias",
        description="d",
        deprecated=True,
    )
    d = field_spec_to_dict(f)
    f2 = field_spec_from_dict(d)
    assert f2.name == "f" and f2.required and f2.default == 3 and f2.alias == "alias"


def test_field_spec_to_dict_omits_none_optional_keys() -> None:
    f = FieldSpec(name="a", type=TypeSpec(kind=TypeKind.STR), required=False)
    d = field_spec_to_dict(f)
    assert "alias" not in d or d.get("alias") is None


def test_dumps_model_spec_uses_json_default_for_non_json() -> None:
    m = ModelSpec(name="M", fields={"x": TypeSpec(kind=TypeKind.INT, default=object())})
    text = dumps_model_spec(m)
    data = json.loads(text)
    assert "fields" in data


def test_typespec_optional_nullable_flags() -> None:
    ts = TypeSpec(kind=TypeKind.INT, optional=True, nullable=True)
    d = typespec_to_dict(ts)
    assert d["optional"] is True and d["nullable"] is True


def test_model_spec_from_dict_empty_fields_key() -> None:
    m = model_spec_from_dict({"name": "Z", "fields": None})
    assert m.fields == {}


def test_typespec_roundtrip_name_qualname_module() -> None:
    ts = TypeSpec(
        kind=TypeKind.NOMINAL,
        name="x",
        qualname="pkg.C",
        module="pkg.mod",
    )
    d = typespec_to_dict(ts)
    assert d["name"] == "x" and d["qualname"] == "pkg.C" and d["module"] == "pkg.mod"
    ts2 = typespec_from_dict(d)
    assert (
        ts2.name == ts.name and ts2.qualname == ts.qualname and ts2.module == ts.module
    )
