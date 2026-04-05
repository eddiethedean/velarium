"""Batch fixture package."""

from __future__ import annotations

import dataclasses


@dataclasses.dataclass
class RootModel:
    """Defined in package __init__."""

    name: str
