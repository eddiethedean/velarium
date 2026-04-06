"""Cross-cutting invariants: normalization idempotence, JSON stability, cache keys, CLI."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fixtures.batch_pkg import RootModel
from velarium.json_codec import loads_model_spec, typespec_dedupe_key, typespec_to_dict
from velarium.normalize import normalize_typespec
from velotype.cli import app
from velotype.ir import ModelSpec, TypeKind, TypeSpec
from velotype.json_codec import (
    dumps_model_spec,
    model_spec_from_dict,
    model_spec_to_dict,
)
from velotype.normalize import normalize_union

_REPO_ROOT = Path(__file__).resolve().parent.parent
_runner = CliRunner()


def _env() -> dict[str, str]:
    p = f"{_REPO_ROOT / 'packages' / 'velotype'}:{_REPO_ROOT / 'packages' / 'velarium'}"
    tests_root = str(_REPO_ROOT / "tests")
    return {**os.environ, "PYTHONPATH": f"{p}:{tests_root}"}


def _model_spec_roundtrip(m: ModelSpec) -> ModelSpec:
    text = dumps_model_spec(m, indent=None)
    return loads_model_spec(text)


def test_model_spec_dict_json_roundtrip_preserves_structure() -> None:
    """model_spec_to_dict → json → model_spec_from_dict matches direct dumps/loads."""
    m = ModelSpec(
        name="Inv",
        fields={
            "a": TypeSpec(kind=TypeKind.INT, optional=True),
            "b": TypeSpec(
                kind=TypeKind.LIST,
                args=[
                    TypeSpec(
                        kind=TypeKind.UNION,
                        args=[
                            TypeSpec(kind=TypeKind.INT),
                            TypeSpec(kind=TypeKind.NONE),
                        ],
                    )
                ],
            ),
        },
    )
    d = model_spec_to_dict(m)
    raw = json.dumps(d, sort_keys=True)
    m2 = model_spec_from_dict(json.loads(raw))
    m3 = _model_spec_roundtrip(m)
    assert m2.name == m.name == m3.name
    assert set(m2.fields.keys()) == set(m.fields.keys())


@pytest.mark.parametrize(
    "ts",
    [
        TypeSpec(kind=TypeKind.INT),
        TypeSpec(kind=TypeKind.STR, optional=True, nullable=True),
        TypeSpec(
            kind=TypeKind.UNION,
            args=[TypeSpec(kind=TypeKind.INT), TypeSpec(kind=TypeKind.STR)],
        ),
        TypeSpec(
            kind=TypeKind.LIST,
            args=[
                TypeSpec(
                    kind=TypeKind.UNION,
                    args=[TypeSpec(kind=TypeKind.INT), TypeSpec(kind=TypeKind.INT)],
                )
            ],
        ),
        TypeSpec(
            kind=TypeKind.DICT,
            args=[
                TypeSpec(kind=TypeKind.STR),
                TypeSpec(kind=TypeKind.TUPLE, args=[TypeSpec(kind=TypeKind.INT)]),
            ],
        ),
        TypeSpec(
            kind=TypeKind.UNION,
            args=[
                TypeSpec(
                    kind=TypeKind.UNION,
                    args=[TypeSpec(kind=TypeKind.FLOAT), TypeSpec(kind=TypeKind.FLOAT)],
                ),
                TypeSpec(kind=TypeKind.STR),
            ],
        ),
    ],
    ids=["int", "opt_null", "union", "list_dup_union", "dict_tuple", "nested_union"],
)
def test_normalize_typespec_idempotent(ts: TypeSpec) -> None:
    once = normalize_typespec(ts)
    twice = normalize_typespec(once)
    assert once == twice


def test_normalize_union_idempotent() -> None:
    u = TypeSpec(
        kind=TypeKind.UNION,
        args=[TypeSpec(kind=TypeKind.INT), TypeSpec(kind=TypeKind.STR)],
    )
    a = normalize_union(u)
    b = normalize_union(a)
    assert a == b


def test_typespec_dedupe_key_stable_across_equal_trees() -> None:
    t1 = TypeSpec(
        kind=TypeKind.UNION,
        args=[TypeSpec(kind=TypeKind.INT), TypeSpec(kind=TypeKind.STR)],
    )
    t2 = TypeSpec(
        kind=TypeKind.UNION,
        args=[TypeSpec(kind=TypeKind.INT), TypeSpec(kind=TypeKind.STR)],
    )
    assert typespec_dedupe_key(t1) == typespec_dedupe_key(t2)


def test_typespec_dedupe_key_differs_for_different_kinds() -> None:
    a = TypeSpec(kind=TypeKind.INT)
    b = TypeSpec(kind=TypeKind.STR)
    assert typespec_dedupe_key(a) != typespec_dedupe_key(b)


def test_typespec_dedupe_key_matches_typespec_to_dict_json() -> None:
    """Dedupe key must stay aligned with canonical dict JSON (see json_codec.normalize_union)."""
    ts = TypeSpec(
        kind=TypeKind.UNION,
        args=[TypeSpec(kind=TypeKind.INT, name="T", module="m", qualname="m.T")],
    )
    from velarium.json_codec import _json_default_value

    d = typespec_to_dict(ts)
    direct = json.dumps(d, sort_keys=True, default=_json_default_value)
    assert typespec_dedupe_key(ts) == direct


def test_loads_model_spec_rejects_invalid_json() -> None:
    with pytest.raises(json.JSONDecodeError):
        loads_model_spec("not json")


def test_normalize_backend_whitespace_empty_falls_back_to_python(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("VELARIUM_NORMALIZE_BACKEND", "   ")
    ts = TypeSpec(kind=TypeKind.INT)
    assert normalize_typespec(ts).kind == TypeKind.INT


def test_batch_cache_stem_differs_for_merge_flag() -> None:
    import velotype.batch as batch_mod

    a = batch_mod._batch_cache_stem(
        RootModel, mode="stub", merge=False, stub_style="minimal"
    )
    b = batch_mod._batch_cache_stem(
        RootModel, mode="stub", merge=True, stub_style="minimal"
    )
    assert a is not None and b is not None
    assert a != b


def test_cli_batch_stub_cache_dir_smoke(tmp_path: Path) -> None:
    cache = tmp_path / "cache"
    out = tmp_path / "out"
    r = _runner.invoke(
        app,
        [
            "batch",
            "stub",
            "fixtures.batch_pkg",
            "--out-dir",
            str(out),
            "--cache-dir",
            str(cache),
        ],
        env=_env(),
    )
    assert r.exit_code == 0, r.stdout + (r.stderr or "")
    assert list(out.glob("*.pyi"))
    assert any(cache.glob("*.json"))


def test_cli_batch_stub_no_cache_skips_cache_writes(tmp_path: Path) -> None:
    cache = tmp_path / "cache"
    out = tmp_path / "out"
    r = _runner.invoke(
        app,
        [
            "batch",
            "stub",
            "fixtures.batch_pkg",
            "--out-dir",
            str(out),
            "--cache-dir",
            str(cache),
            "--no-cache",
        ],
        env=_env(),
    )
    assert r.exit_code == 0, r.stdout + (r.stderr or "")
    assert not list(cache.glob("*.json"))


def test_cli_batch_ir_with_cache_dir(tmp_path: Path) -> None:
    cache = tmp_path / "cache"
    out = tmp_path / "out"
    r = _runner.invoke(
        app,
        [
            "batch",
            "ir",
            "fixtures.batch_pkg",
            "--out-dir",
            str(out),
            "--cache-dir",
            str(cache),
        ],
        env=_env(),
    )
    assert r.exit_code == 0, r.stdout + (r.stderr or "")
    assert list(out.glob("*.json"))
    assert any(cache.glob("*.json"))
