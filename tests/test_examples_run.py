"""Ensure documented runnable examples execute (see examples/README.md)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent


def test_examples_getting_started_runs() -> None:
    script = _ROOT / "examples" / "getting_started.py"
    r = subprocess.run(
        [sys.executable, str(script)],
        cwd=_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert "OK:" in r.stdout


def test_doc_cli_ir_batch_fixture_runs() -> None:
    """Matches docs: PYTHONPATH=tests velotype ir fixtures.batch_pkg:RootModel"""
    env = {**os.environ, "PYTHONPATH": str(_ROOT / "tests")}
    r = subprocess.run(
        [sys.executable, "-m", "velotype", "ir", "fixtures.batch_pkg:RootModel"],
        cwd=_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert '"format_version"' in r.stdout
    assert "RootModel" in r.stdout
