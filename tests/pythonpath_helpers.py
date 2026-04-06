"""Cross-platform PYTHONPATH for subprocess and CliRunner tests (Windows uses ``;``)."""

from __future__ import annotations

import os
from pathlib import Path


def repo_pythonpath(repo_root: Path, *, include_tests: bool = True) -> str:
    """Join velotype, velarium, and optionally ``tests`` with ``os.pathsep``."""
    parts = [
        str(repo_root / "packages" / "velotype"),
        str(repo_root / "packages" / "velarium"),
    ]
    if include_tests:
        parts.append(str(repo_root / "tests"))
    return os.pathsep.join(parts)
