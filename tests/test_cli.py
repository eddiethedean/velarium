"""Smoke tests for the velotype CLI entry points."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from pythonpath_helpers import repo_pythonpath

_REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize("argv", [["-m", "velotype", "ir"], ["-m", "velotype", "stub"]])
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
            "velotype",
            "ir",
            "tests.fixtures.sample_pkg:Sample",
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={
            **os.environ,
            "PYTHONPATH": repo_pythonpath(_REPO_ROOT, include_tests=False),
        },
    )
    assert r.returncode == 0, r.stderr
    assert '"name": "Sample"' in r.stdout
    assert "int" in r.stdout
