"""Tests for velotype.json_codec."""

from __future__ import annotations

import json
from enum import Enum

from velotype.ir import (
    FieldSpec,
    ModelConfig,
    ModelMetadata,
    ModelSpec,
    TypeKind,
    TypeSpec,
)
from velotype.json_codec import (
    dumps_model_spec,
    field_spec_from_dict,
    field_spec_to_dict,
    loads_model_spec,
    model_spec_from_dict,
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
    assert ts2.name == ts.name and ts2.qualname == ts.qualname and ts2.module == ts.module
