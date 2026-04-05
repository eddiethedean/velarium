"""Tests for velarium.typing_resolve."""

from __future__ import annotations

import sys

import pytest

from velarium.typing_resolve import (
    get_resolved_hints,
    module_globals_for_class,
)


def test_module_globals_for_class_when_module_not_loaded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class C:
        __module__ = "___velarium_fake_mod_for_resolve___"

    monkeypatch.delitem(sys.modules, "___velarium_fake_mod_for_resolve___", raising=False)
    g = module_globals_for_class(C)
    assert isinstance(g, dict) and g.get("__module__") == "___velarium_fake_mod_for_resolve___"


def test_evaluate_forward_ref_legacy_positional_recursive_guard(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Older typing._evaluate(globalns, localns, frozenset()) — no keyword-only param."""
    from velarium.typing_resolve import evaluate_forward_ref

    class LegacyRef:
        def _evaluate(
            self,
            globalns: dict[str, object],
            localns: dict[str, object],
            rg: frozenset[object],
        ) -> type:
            return int

    assert evaluate_forward_ref(LegacyRef(), {"int": int}) is int  # type: ignore[arg-type]


def test_get_resolved_hints_swallows_get_type_hints_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class X:
        x: int

    def boom(*_a: object, **_k: object) -> dict[str, object]:
        raise RuntimeError("no hints")

    monkeypatch.setattr("velarium.typing_resolve.get_type_hints", boom)
    assert get_resolved_hints(X) == {}
