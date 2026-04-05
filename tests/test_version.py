"""Ensure package __version__ matches distribution metadata (Hatch single source per package)."""

from __future__ import annotations

import importlib.metadata

import stubber
import velarium


def test_stubber_version_matches_distribution_metadata() -> None:
    assert stubber.__version__ == importlib.metadata.version("stubber")


def test_velarium_version_matches_distribution_metadata() -> None:
    assert velarium.__version__ == importlib.metadata.version("velarium")
