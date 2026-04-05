"""Minimal dataclass for CLI integration tests."""

from __future__ import annotations

import dataclasses


@dataclasses.dataclass
class Sample:
    x: int
