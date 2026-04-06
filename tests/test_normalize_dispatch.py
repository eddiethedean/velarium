"""Tests for VELARIUM_NORMALIZE_BACKEND and native hook dispatch."""

from __future__ import annotations

import sys
import types

import pytest

from velarium.ir import TypeKind, TypeSpec
from velarium.json_codec import typespec_dedupe_key
from velarium.normalize import _normalize_typespec_python, normalize_typespec


def test_typespec_dedupe_key_matches_structural_identity() -> None:
    a = TypeSpec(kind=TypeKind.INT)
    b = TypeSpec(kind=TypeKind.INT)
    assert typespec_dedupe_key(a) == typespec_dedupe_key(b)


def test_normalize_typespec_native_import_error_falls_back(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("VELARIUM_NORMALIZE_BACKEND", "native")
    monkeypatch.delitem(sys.modules, "velarium._native", raising=False)
    ts = TypeSpec(kind=TypeKind.STR)
    assert normalize_typespec(ts) == _normalize_typespec_python(ts)


def test_normalize_typespec_native_module_used_when_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called: list[bool] = []

    def native_impl(ts: TypeSpec) -> TypeSpec:
        called.append(True)
        return _normalize_typespec_python(ts)

    mod = types.ModuleType("velarium._native")
    mod.normalize_typespec = native_impl
    monkeypatch.setitem(sys.modules, "velarium._native", mod)
    monkeypatch.setenv("VELARIUM_NORMALIZE_BACKEND", "native")

    ts = TypeSpec(
        kind=TypeKind.UNION,
        args=[TypeSpec(kind=TypeKind.INT), TypeSpec(kind=TypeKind.STR)],
    )
    out = normalize_typespec(ts)
    assert len(called) >= 1 and all(called)
    assert out.kind == TypeKind.UNION


def test_normalize_typespec_non_native_env_uses_python(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("VELARIUM_NORMALIZE_BACKEND", "python")
    mod = types.ModuleType("velarium._native")
    mod.normalize_typespec = lambda ts: ts  # would break if called
    monkeypatch.setitem(sys.modules, "velarium._native", mod)
    ts = TypeSpec(kind=TypeKind.INT)
    assert normalize_typespec(ts).kind == TypeKind.INT


def test_normalize_typespec_native_missing_callable_falls_back(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mod = types.ModuleType("velarium._native")
    monkeypatch.setitem(sys.modules, "velarium._native", mod)
    monkeypatch.setenv("VELARIUM_NORMALIZE_BACKEND", "native")
    ts = TypeSpec(kind=TypeKind.INT)
    assert normalize_typespec(ts) == _normalize_typespec_python(ts)
