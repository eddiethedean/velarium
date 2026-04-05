"""Tests for velotype.cli_support exit codes and error formatting."""

from __future__ import annotations

from velotype.cli_support import (
    EXIT_BUILD,
    EXIT_OK,
    EXIT_USAGE,
    BatchItemError,
    format_batch_error,
)


def test_exit_code_constants() -> None:
    assert EXIT_OK == 0
    assert EXIT_BUILD == 1
    assert EXIT_USAGE == 2


def test_format_batch_error() -> None:
    err = BatchItemError(target="pkg:Mod", phase="build", message="bad")
    assert format_batch_error(err) == "[build] pkg:Mod: bad"
