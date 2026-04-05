"""Ensure package version matches distribution metadata (single source: stubber.__version__)."""

from __future__ import annotations

import importlib.metadata

import stubber


def test_version_matches_distribution_metadata() -> None:
    assert stubber.__version__ == importlib.metadata.version("stubber")
