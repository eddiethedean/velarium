"""Shared ModelMetadata extraction for class-based builders (Phase 0.3)."""

from __future__ import annotations

import inspect
from typing import Any

from velarium.ir import ModelMetadata


def metadata_for_class(cls: type[Any], *, include_source: bool = True) -> ModelMetadata:
    """Build ModelMetadata from a class (module, optional file and line from ``inspect``)."""
    src_file: str | None = None
    line_number: int | None = None
    if include_source:
        try:
            src_file = inspect.getsourcefile(cls)
            _lines, start = inspect.getsourcelines(cls)
            line_number = start
        except (OSError, TypeError):
            pass
    return ModelMetadata(
        source_module=cls.__module__,
        source_file=src_file,
        line_number=line_number,
        generated_by="velarium",
        version=None,
    )
