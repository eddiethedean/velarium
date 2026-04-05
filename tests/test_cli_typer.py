"""Typer CliRunner tests for stubber.cli (full line coverage)."""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from stubber.cli import app

_REPO_ROOT = Path(__file__).resolve().parent.parent
_runner = CliRunner()


def _pkg_paths() -> str:
    return (
        f"{_REPO_ROOT / 'packages' / 'stubber'}:{_REPO_ROOT / 'packages' / 'velarium'}"
    )


def _env() -> dict[str, str]:
    return {**os.environ, "PYTHONPATH": _pkg_paths()}


def test_cli_no_colon_exits_2() -> None:
    r = _runner.invoke(app, ["ir", "nocolon"])
    assert r.exit_code == 2
    assert "module:Class" in r.output or "module:Class" in (r.stderr or "")


def test_cli_empty_segment_exits_2() -> None:
    r = _runner.invoke(app, [":Class"])
    assert r.exit_code == 2


def test_cli_empty_qual_after_colon_exits_2() -> None:
    r = _runner.invoke(
        app,
        ["ir", "tests.fixtures.sample_pkg:"],
        env=_env(),
    )
    assert r.exit_code == 2


def test_cli_target_not_a_class() -> None:
    r = _runner.invoke(app, ["ir", "builtins:len"])
    assert r.exit_code == 2
    assert "not a class" in (r.stdout or r.stderr or "").lower()


def test_cli_ir_dataclass_stdout() -> None:
    r = _runner.invoke(
        app,
        ["ir", "tests.fixtures.sample_pkg:Sample"],
        env=_env(),
    )
    assert r.exit_code == 0
    assert "Sample" in r.stdout


def test_cli_ir_writes_file(tmp_path: Path) -> None:
    out = tmp_path / "ir.json"
    r = _runner.invoke(
        app,
        ["ir", "tests.fixtures.sample_pkg:Sample", "-o", str(out)],
        env=_env(),
    )
    assert r.exit_code == 0
    assert out.read_text()
    assert "Wrote IR" in r.stdout


def test_cli_stub_writes_file(tmp_path: Path) -> None:
    out = tmp_path / "s.pyi"
    r = _runner.invoke(
        app,
        ["stub", "tests.fixtures.sample_pkg:Sample", "-o", str(out)],
        env=_env(),
    )
    assert r.exit_code == 0
    assert "class Sample" in out.read_text()


def test_cli_not_dataclass_exits_1() -> None:
    r = _runner.invoke(
        app,
        ["ir", "builtins:object"],
        env=_env(),
    )
    assert r.exit_code == 1


def test_cli_stub_not_dataclass_exits_1() -> None:
    r = _runner.invoke(
        app,
        ["stub", "builtins:object"],
        env=_env(),
    )
    assert r.exit_code == 1


def test_cli_stub_stdout_without_out() -> None:
    r = _runner.invoke(
        app,
        ["stub", "tests.fixtures.sample_pkg:Sample"],
        env=_env(),
    )
    assert r.exit_code == 0
    assert "class Sample" in r.stdout


def test___main___exec_help(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["stubber", "--help"])
    main_path = _REPO_ROOT / "packages" / "stubber" / "stubber" / "__main__.py"
    spec = importlib.util.spec_from_file_location("__stubber_main__", main_path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    with pytest.raises(SystemExit) as ei:
        spec.loader.exec_module(mod)
    assert ei.value.code == 0
