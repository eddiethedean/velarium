"""Integration tests: builders → IR → JSON → loads → normalize invariants."""

from __future__ import annotations

import json
import textwrap

import pytest

from tests.td_fixtures import TDNotRequiredOnly, TDRequiredInTotalFalse

from velotype.ir import ModelConfig, ModelMetadata, ModelSpec, TypeKind, TypeSpec
from velotype.json_codec import dumps_model_spec, loads_model_spec
from velotype.modelspec_build import modelspec_from_dataclass, modelspec_from_typed_dict
from velotype.normalize import normalize_typespec
from velotype.stubgen import generate_pyi


def test_pep563_dataclass_resolves_annotations_via_exec() -> None:
    """Builders use get_type_hints; string annotations must resolve under PEP 563."""
    ns: dict[str, object] = {}
    exec(
        textwrap.dedent(
            """
            from __future__ import annotations
            from dataclasses import dataclass

            @dataclass
            class Pep563Model:
                count: int
                name: str
            """
        ),
        ns,
        ns,
    )
    Pep563Model = ns["Pep563Model"]
    spec = modelspec_from_dataclass(Pep563Model)
    assert spec.fields["count"].kind == TypeKind.INT
    assert spec.fields["name"].kind == TypeKind.STR


def test_typed_dict_required_and_optional_keys() -> None:
    spec = modelspec_from_typed_dict(TDRequiredInTotalFalse)
    assert spec.fields["must"].optional is False
    assert spec.fields["must"].kind == TypeKind.INT
    assert spec.fields["loose"].optional is True


def test_typed_dict_not_required_marks_field_optional() -> None:
    spec = modelspec_from_typed_dict(TDNotRequiredOnly)
    assert spec.fields["a"].optional is False
    assert spec.fields["b"].optional is True


def test_nested_literal_preserves_values() -> None:
    """Nested Literal forms flatten to literals / unions in IR."""
    from typing import Literal

    from velotype.annotations import type_to_typespec

    ts = type_to_typespec(Literal[Literal[1, 2]], optional=False)
    assert ts.kind in (TypeKind.LITERAL, TypeKind.UNION)


def test_model_spec_json_roundtrip_preserves_config_metadata() -> None:
    m = ModelSpec(
        name="R",
        fields={"n": TypeSpec(kind=TypeKind.INT)},
        config=ModelConfig(frozen=True, extra="allow"),
        metadata=ModelMetadata(
            source_module="sm",
            generated_by="integration-test",
            version="0",
        ),
    )
    s = dumps_model_spec(m, indent=None)
    m2 = loads_model_spec(s)
    assert m2.name == m.name
    assert m2.config is not None and m2.config.frozen and m2.config.extra == "allow"
    assert m2.metadata is not None and m2.metadata.source_module == "sm"


def test_dumps_model_spec_is_deterministic() -> None:
    m = ModelSpec(
        name="D",
        fields={
            "z": TypeSpec(kind=TypeKind.STR),
            "a": TypeSpec(kind=TypeKind.INT),
        },
    )
    t1 = dumps_model_spec(m, indent=None)
    t2 = dumps_model_spec(m, indent=None)
    assert t1 == t2
    d1 = json.loads(t1)
    d2 = json.loads(t2)
    assert d1 == d2


def test_normalize_typespec_idempotent_on_union() -> None:
    u = TypeSpec(
        kind=TypeKind.UNION,
        args=[
            TypeSpec(kind=TypeKind.INT),
            TypeSpec(kind=TypeKind.INT),
            TypeSpec(kind=TypeKind.STR),
        ],
    )
    once = normalize_typespec(u)
    twice = normalize_typespec(once)
    assert once == twice


@pytest.mark.parametrize(
    "kind",
    [
        TypeKind.INT,
        TypeKind.NOMINAL,
        TypeKind.PROTOCOL,
        TypeKind.PARAM_SPEC,
    ],
)
def test_typespec_metadata_json_roundtrip(kind: TypeKind) -> None:
    ts = TypeSpec(
        kind=kind,
        name="n",
        qualname="pkg.T",
        module="pkg",
    )
    from velotype.json_codec import typespec_from_dict, typespec_to_dict

    ts2 = typespec_from_dict(typespec_to_dict(ts))
    assert ts2.kind == ts.kind
    assert ts2.name == ts.name
    assert ts2.qualname == ts.qualname
    assert ts2.module == ts.module


def test_generate_pyi_accepts_mixed_field_kinds() -> None:
    spec = ModelSpec(
        name="Mixed",
        fields={
            "plain": TypeSpec(kind=TypeKind.INT),
            "nom": TypeSpec(
                kind=TypeKind.NOMINAL,
                qualname="Other",
                module="other",
            ),
        },
    )
    text = generate_pyi(spec)
    assert "class Mixed" in text
    assert "plain" in text and "nom" in text
