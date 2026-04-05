"""Tests for stubber.normalize edge cases."""

from __future__ import annotations

from stubber.ir import TypeKind, TypeSpec
from stubber.normalize import normalize_typespec, normalize_union, optional_to_union


def test_normalize_union_not_union_returns_unchanged() -> None:
    ts = TypeSpec(kind=TypeKind.INT)
    assert normalize_union(ts) is ts


def test_normalize_union_single_member_collapses() -> None:
    u = TypeSpec(
        kind=TypeKind.UNION,
        args=[TypeSpec(kind=TypeKind.INT)],
        optional=True,
    )
    out = normalize_union(u)
    assert out.kind == TypeKind.INT
    assert out.optional is True


def test_normalize_union_duplicate_members_collapses_to_one() -> None:
    a = TypeSpec(kind=TypeKind.INT)
    u = TypeSpec(kind=TypeKind.UNION, args=[a, TypeSpec(kind=TypeKind.INT)])
    out = normalize_union(u)
    assert out.kind == TypeKind.INT


def test_optional_to_union_noop_when_not_optional() -> None:
    ts = TypeSpec(kind=TypeKind.STR, optional=False)
    assert optional_to_union(ts) is ts


def test_optional_to_union_union_without_none_appends_none() -> None:
    ts = TypeSpec(
        kind=TypeKind.UNION,
        args=[TypeSpec(kind=TypeKind.STR)],
        optional=True,
    )
    out = optional_to_union(ts)
    assert out.kind == TypeKind.UNION
    assert out.args is not None
    assert any(x.kind == TypeKind.NONE for x in out.args)


def test_optional_to_union_non_union_wraps() -> None:
    ts = TypeSpec(kind=TypeKind.STR, optional=True)
    out = optional_to_union(ts)
    assert out.kind == TypeKind.UNION
    assert len(out.args or []) == 2


def test_normalize_typespec_recurses_into_args() -> None:
    inner = TypeSpec(
        kind=TypeKind.UNION,
        args=[TypeSpec(kind=TypeKind.INT), TypeSpec(kind=TypeKind.INT)],
    )
    ts = TypeSpec(kind=TypeKind.LIST, args=[inner])
    out = normalize_typespec(ts)
    assert out.kind == TypeKind.LIST
    assert out.args is not None
    assert out.args[0].kind == TypeKind.INT
