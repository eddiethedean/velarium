"""Smoke tests for the stubber CLI entry points."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize("argv", [["-m", "stubber", "ir"], ["-m", "stubber", "stub"]])
def test_cli_help_exits_zero(argv: list[str]) -> None:
    r = subprocess.run(
        [sys.executable, *argv, "--help"],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, r.stderr


def test_cli_ir_json_sample_dataclass() -> None:
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "stubber",
            "ir",
            "tests.fixtures.sample_pkg:Sample",
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "PYTHONPATH": str(_REPO_ROOT)},
    )
    assert r.returncode == 0, r.stderr
    assert '"name": "Sample"' in r.stdout
    assert "int" in r.stdout
