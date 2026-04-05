"""Shared namespace and forward-ref resolution for get_type_hints (Phase 0.2)."""

from __future__ import annotations

from typing import Any, ForwardRef, get_type_hints

from typing_extensions import NotRequired, Required


def module_globals_for_class(cls: type) -> dict[str, Any]:
    """Merge module globals with the class name in scope (see modelspec_build._module_globals)."""
    import sys as _sys

    mod = _sys.modules.get(cls.__module__)
    if mod is None:
        return dict(vars(cls))
    g = dict(vars(mod))
    g.setdefault(cls.__name__, cls)
    return g


def get_resolved_hints(
    cls: type,
    *,
    include_extras: bool = True,
) -> dict[str, Any]:
    """Call get_type_hints with a stable globalns for PEP 563 / forward refs."""
    globalns = module_globals_for_class(cls)
    try:
        return get_type_hints(
            cls,
            globalns=globalns,
            localns=None,
            include_extras=include_extras,
        )
    except Exception:
        return {}


def evaluate_forward_ref(
    fr: ForwardRef,
    globalns: dict[str, Any],
    localns: dict[str, Any] | None = None,
) -> Any:
    """Best-effort evaluation of a ForwardRef; raises on failure."""
    ln = localns if localns is not None else globalns
    rg = frozenset()
    try:
        return fr._evaluate(globalns, ln, recursive_guard=rg)  # type: ignore[call-arg]
    except TypeError:
        # Older typing: _evaluate(globalns, localns, recursive_guard) all positional.
        return fr._evaluate(globalns, ln, rg)  # type: ignore[attr-defined,no-any-return]


__all__ = [
    "Required",
    "NotRequired",
    "evaluate_forward_ref",
    "get_resolved_hints",
    "module_globals_for_class",
]
