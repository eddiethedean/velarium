"""Mix of definitions for discovery edge cases."""

from __future__ import annotations

import dataclasses

from fixtures.batch_pkg import RootModel as ReExported  # noqa: F401 — re-export for discovery tests


def not_a_type() -> None:
    """Not a type — skipped in discovery."""


class NotDataclass:
    """Plain class — skipped."""


@dataclasses.dataclass
class LocalModel:
    """Kept."""

    a: int


LocalAlias = LocalModel  # same object — second name skipped in discovery
