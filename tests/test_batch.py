"""Tests for velotype.batch discovery and batch CLI."""

from __future__ import annotations

import importlib
import json
import os
import types
from pathlib import Path

import pytest
from typer.testing import CliRunner

from velotype.batch import (
    discover_dataclass_targets,
    emit_batch_ir,
    emit_batch_stubs,
    path_matches_excludes,
)
from velotype.cli import app
from velotype.cli_support import BatchItemError, format_batch_error

_REPO_ROOT = Path(__file__).resolve().parent.parent
_runner = CliRunner()


def _env() -> dict[str, str]:
    p = f"{_REPO_ROOT / 'packages' / 'velotype'}:{_REPO_ROOT / 'packages' / 'velarium'}"
    tests_root = str(_REPO_ROOT / "tests")
    return {**os.environ, "PYTHONPATH": f"{p}:{tests_root}"}


def test_path_matches_excludes_tests_dir() -> None:
    assert path_matches_excludes("/proj/pkg/tests/test_foo.py", ())
    assert path_matches_excludes("/proj/pkg/test_bar.py", ())
    assert not path_matches_excludes("/proj/tests/fixtures/pkg/models.py", ())
    assert not path_matches_excludes("/proj/pkg/models.py", ())


def test_discover_batch_pkg_finds_two_dataclasses() -> None:
    t = discover_dataclass_targets("fixtures.batch_pkg")
    names = sorted(f"{c.__module__}:{c.__qualname__}" for c in t)
    assert names == [
        "fixtures.batch_pkg.models:SubModel",
        "fixtures.batch_pkg:RootModel",
    ]


def test_batch_stub_writes_two_files(tmp_path: Path) -> None:
    targets = discover_dataclass_targets("fixtures.batch_pkg")
    r = emit_batch_stubs(targets, tmp_path, merge=False, fail_fast=False)
    assert len(r.written) == 2
    assert not r.errors
    texts = [p.read_text() for p in r.written]
    assert any("RootModel" in t for t in texts)
    assert any("SubModel" in t for t in texts)


def test_batch_stub_merge(tmp_path: Path) -> None:
    targets = discover_dataclass_targets("fixtures.batch_pkg")
    r = emit_batch_stubs(targets, tmp_path, merge=True, fail_fast=False)
    assert len(r.written) == 1
    merged = r.written[0].read_text()
    assert "RootModel" in merged and "SubModel" in merged


def test_batch_ir_merge_json(tmp_path: Path) -> None:
    targets = discover_dataclass_targets("fixtures.batch_pkg")
    r = emit_batch_ir(targets, tmp_path, merge=True, fail_fast=False)
    assert len(r.written) == 1
    import json

    data = json.loads(r.written[0].read_text())
    assert isinstance(data, list)
    assert len(data) == 2


def test_cli_batch_stub_help() -> None:
    r = _runner.invoke(app, ["batch", "stub", "--help"])
    assert r.exit_code == 0
    assert "--out-dir" in r.stdout


def test_cli_batch_stub_runs(tmp_path: Path) -> None:
    r = _runner.invoke(
        app,
        [
            "batch",
            "stub",
            "fixtures.batch_pkg",
            "--out-dir",
            str(tmp_path),
        ],
        env=_env(),
    )
    assert r.exit_code == 0, r.stdout + (r.stderr or "")
    assert list(tmp_path.glob("*.pyi"))


def test_cli_batch_unknown_package_exits_2(tmp_path: Path) -> None:
    r = _runner.invoke(
        app,
        [
            "batch",
            "stub",
            "definitely_missing_pkg_xyz",
            "--out-dir",
            str(tmp_path),
        ],
        env=_env(),
    )
    assert r.exit_code == 2


def test_cli_watch_stub_help() -> None:
    r = _runner.invoke(app, ["watch", "stub", "--help"])
    assert r.exit_code == 0


def test_format_batch_error() -> None:
    s = format_batch_error(BatchItemError(target="m:C", phase="build", message="bad"))
    assert "[build]" in s and "m:C" in s


def test_path_matches_excludes_none_and_patterns() -> None:
    assert not path_matches_excludes(None, ())
    assert path_matches_excludes("/x/test_y.py", ())
    assert path_matches_excludes("/x/testing/z.py", ())
    assert path_matches_excludes("/a/tests.py", ())
    assert path_matches_excludes("/proj/custom/foo.py", ("*/custom/*",))


class _Plain:
    pass


def test_emit_batch_stub_not_dataclass(tmp_path: Path) -> None:
    r = emit_batch_stubs([_Plain], tmp_path, merge=False, fail_fast=False)
    assert len(r.errors) == 1
    assert r.errors[0].phase == "build"


def test_emit_batch_stub_fail_fast(tmp_path: Path) -> None:
    r = emit_batch_stubs([_Plain], tmp_path, fail_fast=True)
    assert len(r.errors) == 1


def test_emit_batch_stub_write_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    orig_wt = Path.write_text

    def guarded(self: Path, *a: object, **k: object) -> None:
        if str(self).endswith(".pyi"):
            raise OSError("nope")
        orig_wt(self, *a, **k)

    monkeypatch.setattr(Path, "write_text", guarded)
    t = discover_dataclass_targets("fixtures.batch_pkg")
    r = emit_batch_stubs(t[:1], tmp_path, fail_fast=False)
    assert any(e.phase == "write" for e in r.errors)


def test_emit_batch_ir_merge_json_decode_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import velotype.batch as batch_mod

    orig_loads = json.loads
    n = [0]

    def flaky_loads(s: str, *a: object, **k: object) -> object:
        n[0] += 1
        if n[0] == 2:
            raise json.JSONDecodeError("expecting value", s, 0)
        return orig_loads(s, *a, **k)

    monkeypatch.setattr(batch_mod.json, "loads", flaky_loads)
    t = discover_dataclass_targets("fixtures.batch_pkg")
    r = emit_batch_ir(t, tmp_path, merge=True, fail_fast=False)
    assert any(e.target == "(merge)" for e in r.errors)


def test_discover_skips_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    real = importlib.import_module

    def imp(name: str) -> object:
        if name == "fixtures.batch_pkg.models":
            raise ImportError("simulated")
        return real(name)

    monkeypatch.setattr(importlib, "import_module", imp)
    t = discover_dataclass_targets("fixtures.batch_pkg")
    names = {f"{c.__module__}:{c.__qualname__}" for c in t}
    assert "fixtures.batch_pkg:RootModel" in names
    assert not any("SubModel" in n for n in names)


def test_cli_batch_build_errors_exit_1(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "velotype.cli.discover_dataclass_targets",
        lambda _p, extra_excludes=(): [object],
    )
    r = _runner.invoke(
        app,
        ["batch", "stub", "x", "--out-dir", str(tmp_path)],
        env=_env(),
    )
    assert r.exit_code == 1


def test_watch_stub_runs_regen(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    regen: list[int] = []

    def fake_run_batch(**_kwargs: object) -> None:
        regen.append(1)

    monkeypatch.setattr("velotype.cli._run_batch", fake_run_batch)

    def one_watch(*_a: object, **_k: object):
        yield set()

    monkeypatch.setattr("watchfiles.watch", one_watch)
    r = _runner.invoke(
        app,
        ["watch", "stub", "fixtures.batch_pkg", "--out-dir", str(tmp_path)],
        env=_env(),
    )
    assert r.exit_code == 0
    assert len(regen) >= 2


def test_watch_stub_no_source_paths_exits_2(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    m = types.ModuleType("empty_mod")
    real = importlib.import_module

    def imp(name: str) -> object:
        if name == "empty_mod":
            return m
        return real(name)

    monkeypatch.setattr(importlib, "import_module", imp)
    r = _runner.invoke(
        app,
        ["watch", "stub", "empty_mod", "--out-dir", str(tmp_path)],
        env=_env(),
    )
    assert r.exit_code == 2


def test_cli_batch_ir_runs(tmp_path: Path) -> None:
    r = _runner.invoke(
        app,
        ["batch", "ir", "fixtures.batch_pkg", "--out-dir", str(tmp_path)],
        env=_env(),
    )
    assert r.exit_code == 0
    assert list(tmp_path.glob("*.json"))


def test_cli_batch_ir_merge(tmp_path: Path) -> None:
    r = _runner.invoke(
        app,
        [
            "batch",
            "ir",
            "fixtures.batch_pkg",
            "--out-dir",
            str(tmp_path),
            "--merge",
        ],
        env=_env(),
    )
    assert r.exit_code == 0
    assert (tmp_path / "merged.json").is_file()


def test_cli_batch_no_targets_exits_2(tmp_path: Path) -> None:
    r = _runner.invoke(
        app,
        ["batch", "stub", "fixtures.empty_pkg", "--out-dir", str(tmp_path)],
        env=_env(),
    )
    assert r.exit_code == 2
    assert "No dataclass targets" in (r.stdout or "") + (r.stderr or "")


def test_discover_module_getfile_typeerror(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import inspect as ins

    real = ins.getfile

    def gf(obj: object) -> str:
        if type(obj).__name__ == "module" and getattr(obj, "__name__", "") == (
            "fixtures.batch_pkg"
        ):
            raise TypeError("simulated")
        return real(obj)

    monkeypatch.setattr(ins, "getfile", gf)
    t = discover_dataclass_targets("fixtures.batch_pkg")
    assert len(t) >= 1


def test_discover_class_getfile_typeerror(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import inspect as ins

    real = ins.getfile

    def gf(obj: object) -> str:
        if isinstance(obj, type) and obj.__name__ == "RootModel":
            raise TypeError("simulated")
        return real(obj)

    monkeypatch.setattr(ins, "getfile", gf)
    t = discover_dataclass_targets("fixtures.batch_pkg")
    assert any(c.__name__ == "RootModel" for c in t)


def test_emit_merge_stub_write_oserror(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    orig = Path.write_text
    n = [0]

    def w(self: Path, *a: object, **k: object) -> None:
        if self.name == "merged.pyi":
            n[0] += 1
            if n[0] == 1:
                raise OSError("merged fail")
        return orig(self, *a, **k)

    monkeypatch.setattr(Path, "write_text", w)
    t = discover_dataclass_targets("fixtures.batch_pkg")
    r = emit_batch_stubs(t, tmp_path, merge=True, fail_fast=False)
    assert any(e.target == "(merge)" for e in r.errors)


def test_emit_stub_fail_fast_on_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    orig = Path.write_text
    n = [0]

    def w(self: Path, *a: object, **k: object) -> None:
        if str(self).endswith(".pyi"):
            n[0] += 1
            if n[0] == 1:
                raise OSError("fail")
        return orig(self, *a, **k)

    monkeypatch.setattr(Path, "write_text", w)
    t = discover_dataclass_targets("fixtures.batch_pkg")
    r = emit_batch_stubs(t, tmp_path, merge=False, fail_fast=True)
    assert r.errors and r.errors[0].phase == "write"


def test_emit_ir_fail_fast_build(tmp_path: Path) -> None:
    r = emit_batch_ir([_Plain], tmp_path, merge=False, fail_fast=True)
    assert len(r.errors) == 1


def test_discover_skips_non_types_and_reexports() -> None:
    t = discover_dataclass_targets("fixtures.batch_mix")
    names = {f"{c.__module__}:{c.__qualname__}" for c in t}
    assert "fixtures.batch_mix:LocalModel" in names
    assert "fixtures.batch_pkg:RootModel" not in names
    assert len([c for c in t if c.__name__ == "LocalModel"]) == 1


def test_discover_class_source_path_can_exclude_without_skipping_module(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import inspect as ins

    real = ins.getfile

    def gf(obj: object) -> str:
        if isinstance(obj, type) and obj.__name__ == "LocalModel":
            return "/tmp/pkg/tests/test_fake.py"
        return real(obj)

    monkeypatch.setattr(ins, "getfile", gf)
    t = discover_dataclass_targets("fixtures.batch_mix")
    names = {f"{c.__module__}:{c.__qualname__}" for c in t}
    assert "fixtures.batch_mix:LocalModel" not in names


def test_discover_extra_exclude_skips_class_file() -> None:
    t = discover_dataclass_targets(
        "fixtures.batch_pkg",
        extra_excludes=("*/models.py",),
    )
    names = {f"{c.__module__}:{c.__qualname__}" for c in t}
    assert "fixtures.batch_pkg:RootModel" in names
    assert "fixtures.batch_pkg.models:SubModel" not in names


def test_emit_ir_two_build_errors_collects(
    tmp_path: Path,
) -> None:
    r = emit_batch_ir([_Plain, _Plain], tmp_path, merge=False, fail_fast=False)
    assert len(r.errors) == 2


def test_emit_ir_write_fail_fast(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    orig = Path.write_text
    n = [0]

    def w(self: Path, *a: object, **k: object) -> None:
        if str(self).endswith(".json"):
            n[0] += 1
            if n[0] == 1:
                raise OSError("w")
        return orig(self, *a, **k)

    monkeypatch.setattr(Path, "write_text", w)
    t = discover_dataclass_targets("fixtures.batch_pkg")
    r = emit_batch_ir(t[:1], tmp_path, merge=False, fail_fast=True)
    assert r.errors and r.errors[0].phase == "write"
