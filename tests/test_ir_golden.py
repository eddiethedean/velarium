"""Golden JSON IR fixtures — regression guard for intentional IR changes."""

from __future__ import annotations

import json
from pathlib import Path

from velotype.ir import ModelMetadata, ModelSpec, TypeKind, TypeSpec
from velotype.json_codec import dumps_model_spec, loads_model_spec

_FIXTURES = Path(__file__).resolve().parent / "fixtures" / "ir_golden"


def test_minimal_model_json_roundtrip_matches_fixture() -> None:
    text = (_FIXTURES / "minimal_model.json").read_text(encoding="utf-8")
    m = loads_model_spec(text)
    assert m.name == "Golden"
    assert m.fields["x"].kind == TypeKind.INT
    out = dumps_model_spec(m, indent=2)
    assert json.loads(out) == json.loads(text)


def test_minimal_model_rebuild_matches_dump() -> None:
    m = ModelSpec(
        name="Golden",
        fields={"x": TypeSpec(kind=TypeKind.INT)},
        metadata=ModelMetadata(generated_by="golden-test"),
    )
    text = (_FIXTURES / "minimal_model.json").read_text(encoding="utf-8")
    assert json.loads(dumps_model_spec(m, indent=2)) == json.loads(text)


def test_complex_model_json_roundtrip_matches_fixture() -> None:
    text = (_FIXTURES / "complex_model.json").read_text(encoding="utf-8")
    m = loads_model_spec(text)
    assert m.name == "Complex"
    assert m.fields["tag"].kind == TypeKind.UNION
    assert m.fields["var"].kind == TypeKind.TYPE_VAR and m.fields["var"].name == "T"
    assert m.config is not None
    out = dumps_model_spec(m, indent=2)
    assert json.loads(out) == json.loads(text)
