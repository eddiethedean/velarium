"""Shared CLI helpers: exit codes and structured batch errors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# Documented in docs/troubleshooting-cli.md
EXIT_OK = 0
EXIT_BUILD = (
    1  # model/builder failure (not a dataclass, TypeError from builder, write error)
)
EXIT_USAGE = 2  # bad arguments, import errors, unresolved path

Phase = Literal["import", "build", "write"]


@dataclass(frozen=True)
class BatchItemError:
    """One failure while processing ``target`` (``module:Class`` or ``module:Outer.Inner``)."""

    target: str
    phase: Phase
    message: str


def format_batch_error(err: BatchItemError) -> str:
    return f"[{err.phase}] {err.target}: {err.message}"
