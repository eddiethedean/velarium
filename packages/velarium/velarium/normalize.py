"""Normalize TypeSpec unions per docs/modelspec-ir.md (flatten, dedupe, preserve order)."""

from __future__ import annotations

import importlib
import os

from velarium.ir import TypeKind, TypeSpec


def normalize_union(ts: TypeSpec) -> TypeSpec:
    """Flatten nested unions, remove duplicates, preserve first-seen order."""
    return _normalize_union_python(ts)


def _normalize_union_python(ts: TypeSpec) -> TypeSpec:
    """Flatten nested unions, remove duplicates, preserve first-seen order (Python impl)."""
    if ts.kind != TypeKind.UNION:
        return ts
    flat: list[TypeSpec] = []
    seen: list[str] = []

    def key(x: TypeSpec) -> str:
        from velarium.json_codec import typespec_dedupe_key

        return typespec_dedupe_key(x)

    stack = list(ts.args or [])
    while stack:
        cur = stack.pop(0)
        if cur.kind == TypeKind.UNION and cur.args:
            stack = list(cur.args) + stack
            continue
        k = key(cur)
        if k not in seen:
            seen.append(k)
            flat.append(cur)
    if len(flat) == 1:
        u = flat[0]
        return TypeSpec(
            kind=u.kind,
            args=u.args,
            optional=ts.optional or u.optional,
            nullable=ts.nullable or u.nullable,
            default=ts.default if ts.default is not None else u.default,
            name=u.name,
            qualname=u.qualname,
            module=u.module,
        )
    return TypeSpec(
        kind=TypeKind.UNION,
        args=flat,
        optional=ts.optional,
        nullable=ts.nullable,
        default=ts.default,
        name=ts.name,
        qualname=ts.qualname,
        module=ts.module,
    )


def _normalize_typespec_python(ts: TypeSpec) -> TypeSpec:
    """Recursively normalize unions and nested structures (Python implementation)."""
    args = ts.args
    if args:
        args = [normalize_typespec(a) for a in args]
    out = TypeSpec(
        kind=ts.kind,
        args=args,
        optional=ts.optional,
        nullable=ts.nullable,
        default=ts.default,
        name=ts.name,
        qualname=ts.qualname,
        module=ts.module,
    )
    if out.kind == TypeKind.UNION:
        return _normalize_union_python(out)
    return out


def normalize_typespec(ts: TypeSpec) -> TypeSpec:
    """Recursively normalize unions and nested structures.

    Set ``VELARIUM_NORMALIZE_BACKEND=native`` to use ``velarium._native.normalize_typespec``
    when an optional native extension is installed; otherwise falls back to Python.
    """
    backend = os.environ.get("VELARIUM_NORMALIZE_BACKEND", "python").lower().strip()
    if backend == "native":
        try:
            mod = importlib.import_module("velarium._native")
            native_fn = getattr(mod, "normalize_typespec", None)
            if callable(native_fn):
                return native_fn(ts)  # type: ignore[no-any-return]
        except ImportError:
            pass
    return _normalize_typespec_python(ts)


def optional_to_union(ts: TypeSpec) -> TypeSpec:
    """
    Encode Optional[T] as Union[T, None] with optional=True per spec.
    If ts already includes none, ensure optional flag is set.
    """
    if not ts.optional:
        return ts
    none = TypeSpec(kind=TypeKind.NONE)
    if ts.kind == TypeKind.UNION and ts.args:
        members = list(ts.args)
        has_none = any(m.kind == TypeKind.NONE for m in members)
        if not has_none:
            members.append(none)
        u = TypeSpec(
            kind=TypeKind.UNION,
            args=members,
            optional=True,
            nullable=ts.nullable,
            default=ts.default,
            name=ts.name,
            qualname=ts.qualname,
            module=ts.module,
        )
        return normalize_union(u)
    u = TypeSpec(
        kind=TypeKind.UNION,
        args=[ts, none],
        optional=True,
        nullable=ts.nullable,
        default=ts.default,
        name=ts.name,
        qualname=ts.qualname,
        module=ts.module,
    )
    return normalize_union(u)
