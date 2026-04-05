"""Ensure package __version__ matches distribution metadata (Hatch single source per package)."""

from __future__ import annotations

import importlib.metadata

import velotype
import velarium


def test_velotype_version_matches_distribution_metadata() -> None:
    assert velotype.__version__ == importlib.metadata.version("velotype")


def test_velarium_version_matches_distribution_metadata() -> None:
    assert velarium.__version__ == importlib.metadata.version("velarium")
