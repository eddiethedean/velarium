"""Golden stub corpus: JSON ModelSpec → generate_pyi must match committed .pyi files.

Cases are every ``*.pyi`` under ``tests/fixtures/stub_corpus/`` (each needs ``<stem>.json``).
This avoids treating ``pyrightconfig.json`` or other JSON as a ModelSpec.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from velarium.json_codec import loads_model_spec
from velotype.stubgen import generate_pyi

_CORPUS = Path(__file__).resolve().parent / "fixtures" / "stub_corpus"


def _stub_corpus_case_names() -> list[str]:
    """One golden case per ``*.pyi``; each must have a matching ``<stem>.json`` ModelSpec."""
    return sorted(p.stem for p in _CORPUS.glob("*.pyi"))


@pytest.mark.parametrize("case", _stub_corpus_case_names())
def test_stub_corpus_matches_golden(case: str) -> None:
    json_path = _CORPUS / f"{case}.json"
    golden_path = _CORPUS / f"{case}.pyi"
    spec = loads_model_spec(json_path.read_text(encoding="utf-8"))
    out = generate_pyi(spec)
    assert out == golden_path.read_text(encoding="utf-8")
