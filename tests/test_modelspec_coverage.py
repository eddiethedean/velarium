"""Tests for velotype.modelspec_build edge cases."""

from __future__ import annotations

import dataclasses
import sys
from typing import TypedDict

import pytest
from typing_extensions import NotRequired

from velotype.modelspec_build import (
    _module_globals,
    modelspec_from_dataclass,
    modelspec_from_typed_dict,
    typespec_from_object,
)


def test_module_globals_when_module_not_loaded(monkeypatch: pytest.MonkeyPatch) -> None:
    class C:
        __module__ = "___velotype_fake_module___"

    monkeypatch.delitem(sys.modules, "___velotype_fake_module___", raising=False)
    g = _module_globals(C)
    assert isinstance(g, dict)


def test_modelspec_from_dataclass_rejects_non_dataclass() -> None:
    class NotD:
        pass

    with pytest.raises(TypeError, match="not a dataclass"):
        modelspec_from_dataclass(NotD)


def test_modelspec_skips_non_init_fields() -> None:
    @dataclasses.dataclass
    class WithField:
        a: int
        b: int = dataclasses.field(init=False, default=0)

    spec = modelspec_from_dataclass(WithField)
    assert "b" not in spec.fields and "a" in spec.fields


def test_modelspec_get_type_hints_failure_uses_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    @dataclasses.dataclass
    class Bad:
        x: int

    def boom(*_a: object, **_k: object) -> dict[str, object]:
        raise RuntimeError("nope")

    monkeypatch.setattr("velarium.typing_resolve.get_type_hints", boom)
    spec = modelspec_from_dataclass(Bad)
    assert "x" in spec.fields


class TD(TypedDict):
    a: int


def test_modelspec_from_typed_dict() -> None:
    spec = modelspec_from_typed_dict(TD)
    assert spec.name == "TD"
    assert "a" in spec.fields


class TDWithOptional(TypedDict):
    req: int
    opt: NotRequired[str]


def test_modelspec_from_typed_dict_optional_keys() -> None:
    spec = modelspec_from_typed_dict(TDWithOptional)
    assert spec.fields["req"].optional is False
    assert spec.fields["opt"].optional is True


class TDTotalFalse(TypedDict, total=False):
    """Keys optional via total=False; annotations are plain types."""

    only: int


def test_modelspec_from_typed_dict_total_false_sets_optional_without_not_required() -> (
    None
):
    spec = modelspec_from_typed_dict(TDTotalFalse)
    assert spec.fields["only"].optional is True
    assert spec.fields["only"].kind.value == "int"


def test_modelspec_from_typed_dict_rejects_non_typed_dict() -> None:
    class Plain:
        pass

    with pytest.raises(TypeError, match="not a TypedDict"):
        modelspec_from_typed_dict(Plain)


def test_modelspec_from_typed_dict_hints_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def boom(*_a: object, **_k: object) -> dict[str, object]:
        raise RuntimeError("nope")

    monkeypatch.setattr("velarium.typing_resolve.get_type_hints", boom)
    spec = modelspec_from_typed_dict(TD)
    assert "a" in spec.fields


def test_typespec_from_object() -> None:
    ts = typespec_from_object(int)
    assert ts.kind.value == "int"


def test_modelspec_inspect_source_fails_gracefully(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import velarium.modelspec_build as mb

    def bad_getsourcefile(_obj: object) -> str | None:
        raise OSError("no source")

    monkeypatch.setattr(mb.inspect, "getsourcefile", bad_getsourcefile)

    @dataclasses.dataclass
    class X:
        a: int

    spec = mb.modelspec_from_dataclass(X)
    assert spec.metadata is not None
    assert spec.metadata.source_file is None
