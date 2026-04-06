#!/usr/bin/env python3
"""Run cProfile on velotype batch stub for a representative package (Phase 0.6).

Usage (from repo root)::

    uv run python scripts/profile_velotype_batch.py

Requires ``tests`` on ``PYTHONPATH`` (the script prepends ``tests/`` relative to repo root).
"""

from __future__ import annotations

import cProfile
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO / "tests") not in sys.path:
    sys.path.insert(0, str(_REPO / "tests"))

os.environ.setdefault(
    "PYTHONPATH",
    f"{_REPO / 'packages' / 'velotype'}:{_REPO / 'packages' / 'velarium'}:{_REPO / 'tests'}",
)

from velotype.batch import discover_dataclass_targets, emit_batch_stubs  # noqa: E402


def main() -> None:
    import tempfile

    out = Path(tempfile.mkdtemp(prefix="velotype-profile-"))
    targets = discover_dataclass_targets("fixtures.batch_pkg")

    def run() -> None:
        emit_batch_stubs(targets, out, merge=False, fail_fast=False)

    stats_file = _REPO / ".velotype_profile.stats"
    cProfile.runctx("run()", globals(), locals(), stats_file.as_posix())
    print(f"Wrote profile stats to {stats_file}")
    print("Inspect with: python -m pstats .velotype_profile.stats")


if __name__ == "__main__":
    main()
