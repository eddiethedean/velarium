"""Tests for velarium.model_metadata."""

from __future__ import annotations

import pytest

from velarium.model_metadata import metadata_for_class


class _Loc:
    x: int


def test_metadata_for_class_include_source_true() -> None:
    m = metadata_for_class(_Loc, include_source=True)
    assert m.source_module == __name__
    assert m.generated_by == "velarium"


def test_metadata_for_class_skips_source_when_disabled() -> None:
    m = metadata_for_class(_Loc, include_source=False)
    assert m.source_file is None and m.line_number is None


def test_metadata_inspect_failure_graceful(monkeypatch: pytest.MonkeyPatch) -> None:
    import velarium.model_metadata as mm

    def bad(*_a: object, **_k: object) -> None:
        raise OSError("no")

    monkeypatch.setattr(mm.inspect, "getsourcefile", bad)
    m = metadata_for_class(_Loc, include_source=True)
    assert m.source_file is None


def test_metadata_getsourcelines_failure_keeps_file_when_getsourcefile_ok(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """If ``getsourcelines`` fails after ``getsourcefile`` succeeds, keep file path; line stays unset."""
    import velarium.model_metadata as mm

    def ok_file(_obj: object) -> str:
        return "/fake/path.py"

    def bad_lines(*_a: object, **_k: object) -> tuple[list[str], int]:
        raise OSError("no lines")

    monkeypatch.setattr(mm.inspect, "getsourcefile", ok_file)
    monkeypatch.setattr(mm.inspect, "getsourcelines", bad_lines)
    m = metadata_for_class(_Loc, include_source=True)
    assert m.source_file == "/fake/path.py"
    assert m.line_number is None


def test_metadata_getsourcelines_typeerror(monkeypatch: pytest.MonkeyPatch) -> None:
    import velarium.model_metadata as mm

    def bad_lines(*_a: object, **_k: object) -> tuple[list[str], int]:
        raise TypeError("not a class")

    monkeypatch.setattr(mm.inspect, "getsourcelines", bad_lines)
    m = metadata_for_class(_Loc, include_source=True)
    assert m.line_number is None
