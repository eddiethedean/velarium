"""Tests for velarium.modelspec_attrs (requires attrs)."""

from __future__ import annotations

import json
from typing import Annotated

import attrs
import pytest

from velarium.modelspec_attrs import modelspec_from_attrs_class
from velotype.ir import TypeKind
from velotype.json_codec import dumps_model_spec, loads_model_spec


@attrs.define
class AttrUser:
    name: str
    score: int = 0


def test_attrs_basic_and_default() -> None:
    spec = modelspec_from_attrs_class(AttrUser)
    assert spec.name == "AttrUser"
    assert spec.fields["name"].kind == TypeKind.STR
    assert spec.fields["score"].kind == TypeKind.INT
    assert spec.fields["score"].default == 0
    assert spec.config is not None


def test_attrs_rejects_plain_class() -> None:
    class Plain:
        pass

    with pytest.raises(TypeError, match="not an attrs"):
        modelspec_from_attrs_class(Plain)


def test_attrs_resolve_types_failure_is_ignored(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def boom(*_a: object, **_k: object) -> None:
        raise RuntimeError("resolve failed")

    monkeypatch.setattr(attrs, "resolve_types", boom)
    spec = modelspec_from_attrs_class(AttrUser)
    assert "name" in spec.fields


@attrs.frozen
class FrozenRecord:
    id: int
    label: str = "x"


def test_attrs_frozen_class() -> None:
    spec = modelspec_from_attrs_class(FrozenRecord)
    assert spec.name == "FrozenRecord"
    assert spec.fields["id"].kind == TypeKind.INT
    assert spec.fields["label"].default == "x"


@attrs.define
class WithFactory:
    items: list[int] = attrs.field(factory=list)


def test_attrs_field_factory_no_default_in_ir() -> None:
    """Factory-only defaults are not evaluated; IR has no static default (like Pydantic)."""
    spec = modelspec_from_attrs_class(WithFactory)
    assert spec.fields["items"].default is None
    assert spec.fields["items"].kind == TypeKind.LIST


@attrs.define
class AttrOptional:
    req: str
    maybe: int | None = None


def test_attrs_optional_union_none() -> None:
    spec = modelspec_from_attrs_class(AttrOptional)
    assert spec.fields["req"].optional is False
    assert spec.fields["maybe"].optional is True


def test_attrs_json_roundtrip() -> None:
    spec = modelspec_from_attrs_class(AttrUser)
    raw = dumps_model_spec(spec, indent=None)
    m2 = loads_model_spec(raw)
    assert m2.name == "AttrUser"
    assert m2.fields["name"].kind == TypeKind.STR
    assert json.loads(raw) == json.loads(dumps_model_spec(spec, indent=None))


def test_attrs_include_extras_false_still_builds() -> None:
    spec = modelspec_from_attrs_class(AttrUser, include_extras=False)
    assert set(spec.fields) == {"name", "score"}


def test_attrs_metadata_populated() -> None:
    spec = modelspec_from_attrs_class(AttrUser)
    assert spec.metadata is not None
    assert spec.metadata.source_module == __name__
    assert spec.metadata.generated_by == "velarium"


@attrs.define
class AttrAnnotated:
    x: Annotated[int, "meta"] = 1


def test_attrs_annotated_base_type() -> None:
    spec = modelspec_from_attrs_class(AttrAnnotated)
    assert spec.fields["x"].kind == TypeKind.INT
    assert spec.fields["x"].default == 1


@attrs.define
class AttrChild(AttrUser):
    extra: bool = False


def test_attrs_subclass_merges_fields() -> None:
    spec = modelspec_from_attrs_class(AttrChild)
    assert set(spec.fields) == {"name", "score", "extra"}
    assert spec.fields["extra"].kind == TypeKind.BOOL
