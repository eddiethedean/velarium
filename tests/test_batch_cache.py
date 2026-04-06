"""Tests for velotype.batch incremental ModelSpec cache."""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

import velotype.batch as batch_mod
from fixtures.batch_pkg import RootModel
from velotype.batch import emit_batch_ir, emit_batch_stubs


def test_batch_cache_second_run_skips_modelspec_build(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cache_dir = tmp_path / "cache"
    out1 = tmp_path / "o1"
    out2 = tmp_path / "o2"
    targets = [RootModel]
    calls: list[int] = []
    orig = batch_mod.modelspec_from_dataclass

    def wrapped(cls: type) -> object:
        calls.append(1)
        return orig(cls)

    monkeypatch.setattr(batch_mod, "modelspec_from_dataclass", wrapped)

    emit_batch_stubs(targets, out1, cache_dir=cache_dir)
    assert len(calls) == 1
    emit_batch_stubs(targets, out2, cache_dir=cache_dir)
    assert len(calls) == 1


def test_batch_cache_corrupt_entry_rebuilds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cache_dir = tmp_path / "cache"
    out = tmp_path / "out"
    targets = [RootModel]
    emit_batch_stubs(targets, out, cache_dir=cache_dir)
    stems = list(cache_dir.glob("*.json"))
    assert len(stems) == 1
    stems[0].write_text("not json {{{", encoding="utf-8")

    calls: list[int] = []
    orig = batch_mod.modelspec_from_dataclass

    def wrapped(cls: type) -> object:
        calls.append(1)
        return orig(cls)

    monkeypatch.setattr(batch_mod, "modelspec_from_dataclass", wrapped)
    emit_batch_stubs(targets, tmp_path / "out2", cache_dir=cache_dir)
    assert len(calls) == 1


def test_batch_cache_save_oserror_still_emits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cache_dir = tmp_path / "cache"
    out = tmp_path / "out"
    targets = [RootModel]
    orig_wt = Path.write_text

    def guarded(self: Path, *a: object, **k: object) -> None:
        if str(cache_dir) in str(self.resolve()):
            raise OSError("cache write denied")
        return orig_wt(self, *a, **k)

    monkeypatch.setattr(Path, "write_text", guarded)
    r = emit_batch_stubs(targets, out, cache_dir=cache_dir)
    assert not r.errors
    assert r.written


def test_class_source_sha256_read_oserror(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_path = Path(inspect.getfile(RootModel)).resolve()
    real_rb = Path.read_bytes

    def rb(self: Path) -> bytes:
        if self.resolve() == target_path:
            raise OSError("simulated read failure")
        return real_rb(self)

    monkeypatch.setattr(Path, "read_bytes", rb)
    assert batch_mod._class_source_sha256(RootModel) is None


def test_emit_batch_ir_uses_cache(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cache_dir = tmp_path / "cache"
    targets = [RootModel]
    calls: list[int] = []
    orig = batch_mod.modelspec_from_dataclass

    def wrapped(cls: type) -> object:
        calls.append(1)
        return orig(cls)

    monkeypatch.setattr(batch_mod, "modelspec_from_dataclass", wrapped)
    emit_batch_ir(targets, tmp_path / "a", cache_dir=cache_dir)
    assert len(calls) == 1
    emit_batch_ir(targets, tmp_path / "b", cache_dir=cache_dir)
    assert len(calls) == 1


def test_use_cache_false_always_builds(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cache_dir = tmp_path / "cache"
    targets = [RootModel]
    calls: list[int] = []
    orig = batch_mod.modelspec_from_dataclass

    def wrapped(cls: type) -> object:
        calls.append(1)
        return orig(cls)

    monkeypatch.setattr(batch_mod, "modelspec_from_dataclass", wrapped)
    emit_batch_stubs(targets, tmp_path / "o1", cache_dir=cache_dir)
    assert len(calls) == 1
    emit_batch_stubs(targets, tmp_path / "o2", cache_dir=cache_dir, use_cache=False)
    assert len(calls) == 2


def test_stub_and_ir_cache_use_distinct_keys(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """IR vs stub mode must not share the same cache entry."""
    cache_dir = tmp_path / "cache"
    targets = [RootModel]
    calls: list[int] = []
    orig = batch_mod.modelspec_from_dataclass

    def wrapped(cls: type) -> object:
        calls.append(1)
        return orig(cls)

    monkeypatch.setattr(batch_mod, "modelspec_from_dataclass", wrapped)
    emit_batch_stubs(targets, tmp_path / "s", cache_dir=cache_dir)
    emit_batch_ir(targets, tmp_path / "i", cache_dir=cache_dir)
    assert len(calls) == 2


def test_load_cache_read_text_oserror_returns_none(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stem = "deadbeef"
    path = tmp_path / f"{stem}.json"
    path.write_text("{}", encoding="utf-8")
    real_rt = Path.read_text

    def rt(self: Path, *a: object, **k: object) -> str:
        if self.resolve() == path.resolve():
            raise OSError("read denied")
        return real_rt(self, *a, **k)

    monkeypatch.setattr(Path, "read_text", rt)
    assert batch_mod._load_model_spec_cache(tmp_path, stem) is None
