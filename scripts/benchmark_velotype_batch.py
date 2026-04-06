#!/usr/bin/env python3
"""Compare cold vs cached velotype batch stub runs (stdlib ``timeit``, Phase 0.6).

Usage (from repo root)::

    uv run python scripts/benchmark_velotype_batch.py

Requires ``tests`` on ``PYTHONPATH`` (the script prepends ``tests/``).
"""

from __future__ import annotations

import os
import sys
import tempfile
import timeit
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
    targets = discover_dataclass_targets("fixtures.batch_pkg")
    cache = Path(tempfile.mkdtemp(prefix="velotype-bench-cache-"))
    cold_out = Path(tempfile.mkdtemp(prefix="velotype-bench-cold-"))
    warm_out = Path(tempfile.mkdtemp(prefix="velotype-bench-warm-"))

    emit_batch_stubs(
        targets,
        warm_out,
        merge=False,
        fail_fast=False,
        cache_dir=cache,
        use_cache=True,
    )

    def cold() -> None:
        emit_batch_stubs(
            targets,
            cold_out,
            merge=False,
            fail_fast=False,
            cache_dir=None,
            use_cache=True,
        )

    def warm() -> None:
        emit_batch_stubs(
            targets,
            warm_out,
            merge=False,
            fail_fast=False,
            cache_dir=cache,
            use_cache=True,
        )

    n = 20
    t_cold = timeit.timeit(cold, number=n) / n
    t_warm = timeit.timeit(warm, number=n) / n
    print(
        f"fixtures.batch_pkg — {len(targets)} dataclass(es), {n} iterations per phase"
    )
    print(f"  cold (no cache dir):  {t_cold * 1000:.3f} ms/run")
    print(f"  warm (cache hit):     {t_warm * 1000:.3f} ms/run")


if __name__ == "__main__":
    main()
