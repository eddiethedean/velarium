"""Tests for velarium.modelspec_pydantic (requires pydantic)."""

from __future__ import annotations

import json
from typing import Annotated

import pytest
from pydantic import BaseModel, ConfigDict, Field

from velarium.modelspec_pydantic import (
    _model_config_from_pydantic,
    modelspec_from_pydantic_model,
)
from velotype.ir import ModelConfig, TypeKind
from velotype.json_codec import dumps_model_spec, loads_model_spec


class User(BaseModel):
    name: str
    age: int = 0


def test_pydantic_basic_fields_and_default() -> None:
    spec = modelspec_from_pydantic_model(User)
    assert spec.name == "User"
    assert spec.fields["name"].kind == TypeKind.STR
    assert spec.fields["name"].default is None
    assert spec.fields["age"].kind == TypeKind.INT
    assert spec.fields["age"].default == 0
    assert spec.config is not None
    assert spec.config.frozen is False


def test_pydantic_frozen_and_extra_configdict() -> None:
    class M(BaseModel):
        model_config = ConfigDict(frozen=True, extra="ignore")
        x: int

    spec = modelspec_from_pydantic_model(M)
    assert spec.config is not None
    assert spec.config.frozen is True
    assert spec.config.extra == "ignore"


def test_pydantic_model_config_dict() -> None:
    class M(BaseModel):
        model_config = {"frozen": True, "extra": "allow"}

    spec = modelspec_from_pydantic_model(M)
    assert spec.config is not None and spec.config.frozen is True
    assert spec.config.extra == "allow"


def test_pydantic_default_factory_skips_default_in_ir() -> None:
    class M(BaseModel):
        items: list[int] = Field(default_factory=list)

    spec = modelspec_from_pydantic_model(M)
    assert spec.fields["items"].default is None


def test_pydantic_rejects_non_model() -> None:
    class Plain:
        pass

    with pytest.raises(TypeError, match="not a Pydantic"):
        modelspec_from_pydantic_model(Plain)


def test_pydantic_rejects_non_type() -> None:
    with pytest.raises(TypeError, match="not a Pydantic"):
        modelspec_from_pydantic_model(1)  # type: ignore[arg-type]


def test_model_config_from_pydantic_none() -> None:
    class M(BaseModel):
        x: int

    c = _model_config_from_pydantic(M)
    assert isinstance(c, ModelConfig)
    assert c.frozen is False


def test_model_config_explicit_none_mapping() -> None:
    class Plain:
        model_config = None

    c = _model_config_from_pydantic(Plain)
    assert c.frozen is False and c.extra == "forbid"


def test_model_config_invalid_extra_falls_back() -> None:
    class Cfg:
        frozen = False
        extra = "bogus"

    class Plain:
        model_config = Cfg()

    c = _model_config_from_pydantic(Plain)
    assert c.extra == "forbid"


def test_model_config_dict_unknown_extra_string() -> None:
    class Plain:
        model_config = {"frozen": False, "extra": "nope"}

    c = _model_config_from_pydantic(Plain)
    assert c.extra == "forbid"


def test_pydantic_optional_fields() -> None:
    class M(BaseModel):
        req: str
        maybe: int | None = None

    spec = modelspec_from_pydantic_model(M)
    assert spec.fields["req"].optional is False
    assert spec.fields["maybe"].optional is True
    assert spec.fields["maybe"].default is None


def test_pydantic_nested_model_field() -> None:
    class Inner(BaseModel):
        v: int

    class Outer(BaseModel):
        inner: Inner

    spec = modelspec_from_pydantic_model(Outer)
    inner_ts = spec.fields["inner"]
    assert inner_ts.kind == TypeKind.NOMINAL
    assert inner_ts.qualname is not None and inner_ts.qualname.endswith("Inner")


def test_pydantic_json_roundtrip() -> None:
    spec = modelspec_from_pydantic_model(User)
    raw = dumps_model_spec(spec, indent=None)
    m2 = loads_model_spec(raw)
    assert m2.name == "User"
    assert m2.fields["name"].kind == TypeKind.STR
    assert m2.fields["age"].default == 0
    assert m2.config is not None and m2.config.extra == "forbid"
    # Deterministic JSON
    assert json.loads(raw) == json.loads(dumps_model_spec(spec, indent=None))


def test_pydantic_include_extras_false_still_builds() -> None:
    spec = modelspec_from_pydantic_model(User, include_extras=False)
    assert set(spec.fields) == {"name", "age"}
    assert spec.fields["name"].kind == TypeKind.STR


def test_pydantic_field_explicit_default() -> None:
    class M(BaseModel):
        label: str = Field(default="default")

    spec = modelspec_from_pydantic_model(M)
    assert spec.fields["label"].default == "default"


def test_pydantic_metadata_populated() -> None:
    spec = modelspec_from_pydantic_model(User)
    assert spec.metadata is not None
    assert spec.metadata.source_module == __name__
    assert spec.metadata.generated_by == "velarium"


def test_pydantic_annotated_int_still_int() -> None:
    """Annotated metadata (e.g. Field constraints) is not IR; base type is."""

    class M(BaseModel):
        x: Annotated[int, Field(ge=0, description="n")] = 0

    spec = modelspec_from_pydantic_model(M)
    assert spec.fields["x"].kind == TypeKind.INT
    assert spec.fields["x"].default == 0


def test_pydantic_extra_forbid_default() -> None:
    class M(BaseModel):
        x: int

    spec = modelspec_from_pydantic_model(M)
    assert spec.config is not None
    assert spec.config.extra == "forbid"


def test_pydantic_subclass_inherits_fields() -> None:
    class Base(BaseModel):
        a: int

    class Child(Base):
        b: str

    spec = modelspec_from_pydantic_model(Child)
    assert set(spec.fields) == {"a", "b"}
    assert spec.fields["b"].kind == TypeKind.STR
