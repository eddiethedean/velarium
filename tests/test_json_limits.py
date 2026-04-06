"""Tests for optional JSON deserialization size and depth limits (Phase 0.7)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from velarium.json_codec import (
    field_spec_from_dict,
    json_input_byte_limit,
    loads_model_spec,
    model_spec_from_dict,
)
from velotype.ir import TypeKind


def _nest_list_typespec(depth: int) -> dict:
    """``list`` of ``list`` of … wrapping ``int`` (``depth`` list wrappers)."""
    inner: dict = {"kind": "int"}
    for _ in range(depth):
        inner = {"kind": "list", "args": [inner]}
    return inner


def test_loads_model_spec_rejects_oversized_utf8(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("VELARIUM_JSON_MAX_BYTES", "10")
    payload = json.dumps({"name": "X", "fields": {}}, sort_keys=True)
    assert len(payload.encode("utf-8")) > 10
    with pytest.raises(ValueError, match="exceeds maximum size"):
        loads_model_spec(payload)


def test_model_spec_from_dict_respects_max_depth(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("VELARIUM_JSON_MAX_DEPTH", "2")
    # Three nested lists → inner TypeSpec entered at depth 3 > 2
    d = {"name": "Deep", "fields": {"x": _nest_list_typespec(3)}}
    with pytest.raises(ValueError, match="maximum depth"):
        model_spec_from_dict(d)


def test_model_spec_from_dict_explicit_max_depth_kwarg() -> None:
    d = {"name": "Deep", "fields": {"x": _nest_list_typespec(4)}}
    with pytest.raises(ValueError, match="maximum depth"):
        model_spec_from_dict(d, max_depth=2)


def test_unset_byte_limit_allows_large_string(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("VELARIUM_JSON_MAX_BYTES", raising=False)
    payload = json.dumps({"name": "Big", "fields": {}}, sort_keys=True) + " " * 5000
    m = loads_model_spec(payload)
    assert m.name == "Big"


def test_max_depth_env_invalid_falls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VELARIUM_JSON_MAX_DEPTH", "not-an-int")
    d = {"name": "Ok", "fields": {"x": {"kind": "int"}}}
    m = model_spec_from_dict(d)
    assert m.fields["x"].kind.value == "int"


def test_max_bytes_env_invalid_treated_as_unlimited(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("VELARIUM_JSON_MAX_BYTES", "not-an-int")
    payload = json.dumps({"name": "X", "fields": {}}, sort_keys=True)
    loads_model_spec(payload)


def test_max_bytes_zero_means_unlimited(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VELARIUM_JSON_MAX_BYTES", "0")
    payload = json.dumps({"name": "X" + " " * 5000, "fields": {}}, sort_keys=True)
    loads_model_spec(payload)


def test_batch_cache_skips_oversized_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from velotype.batch import _load_model_spec_cache

    monkeypatch.setenv("VELARIUM_JSON_MAX_BYTES", "10")
    stem = "abc"
    path = tmp_path / f"{stem}.json"
    path.write_text("x" * 200, encoding="utf-8")
    assert _load_model_spec_cache(tmp_path, stem) is None


def test_byte_limit_counts_utf8_bytes_not_char_len(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The cap uses ``len(s.encode('utf-8'))`` (UTF-8), not Python ``len(s)`` (code points)."""
    monkeypatch.setenv("VELARIUM_JSON_MAX_BYTES", "80")
    # Build JSON with real UTF-8 in the source string (not ``json.dumps`` ASCII escapes).
    emoji = "😀" * 25
    payload = '{"fields": {}, "name": "' + emoji + '"}'
    assert len(payload.encode("utf-8")) > 80
    assert len(payload) < len(payload.encode("utf-8"))
    with pytest.raises(ValueError, match="exceeds maximum size"):
        loads_model_spec(payload)


def test_depth_exactly_at_limit_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VELARIUM_JSON_MAX_DEPTH", "3")
    d = {"name": "Ok", "fields": {"x": _nest_list_typespec(3)}}
    m = model_spec_from_dict(d)
    assert m.fields["x"].kind == TypeKind.LIST


def test_field_spec_from_dict_respects_max_depth_kwarg() -> None:
    deep = _nest_list_typespec(5)
    raw = {
        "name": "f",
        "type": deep,
        "required": True,
    }
    with pytest.raises(ValueError, match="maximum depth"):
        field_spec_from_dict(raw, max_depth=3)


def test_json_input_byte_limit_reflects_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("VELARIUM_JSON_MAX_BYTES", raising=False)
    assert json_input_byte_limit() is None
    monkeypatch.setenv("VELARIUM_JSON_MAX_BYTES", "4096")
    assert json_input_byte_limit() == 4096
    monkeypatch.setenv("VELARIUM_JSON_MAX_BYTES", "0")
    assert json_input_byte_limit() is None


@pytest.mark.parametrize("depth_env", ["", "   "])
def test_max_depth_whitespace_env_uses_default(
    monkeypatch: pytest.MonkeyPatch, depth_env: str
) -> None:
    monkeypatch.setenv("VELARIUM_JSON_MAX_DEPTH", depth_env)
    d = {"name": "Ok", "fields": {"x": {"kind": "int"}}}
    assert model_spec_from_dict(d).fields["x"].kind == TypeKind.INT


def test_negative_max_depth_env_clamped_to_at_least_one(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("VELARIUM_JSON_MAX_DEPTH", "-99")
    # max(1, -99) -> 1: leaf ``int`` under two ``list`` wrappers is at depth 2 > 1
    d = {"name": "X", "fields": {"x": _nest_list_typespec(2)}}
    with pytest.raises(ValueError, match="maximum depth"):
        model_spec_from_dict(d)


def test_batch_cache_loads_when_under_byte_limit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from velotype.batch import _load_model_spec_cache

    monkeypatch.setenv("VELARIUM_JSON_MAX_BYTES", "10000")
    stem = "stem1"
    spec = {"name": "Cached", "fields": {"a": {"kind": "str"}}}
    path = tmp_path / f"{stem}.json"
    path.write_text(json.dumps(spec, sort_keys=True), encoding="utf-8")
    loaded = _load_model_spec_cache(tmp_path, stem)
    assert loaded is not None
    assert loaded.name == "Cached"
    assert loaded.fields["a"].kind == TypeKind.STR
