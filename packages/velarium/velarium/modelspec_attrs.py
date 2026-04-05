"""Build ModelSpec from ``attrs`` classes (optional dependency)."""

from __future__ import annotations

from typing import Any

from velarium.annotations import annotation_to_typespec
from velarium.ir import ModelConfig, ModelSpec, TypeSpec
from velarium.model_metadata import metadata_for_class
from velarium.normalize import normalize_typespec
from velarium.typing_resolve import get_resolved_hints, module_globals_for_class


def modelspec_from_attrs_class(
    cls: type[Any],
    *,
    include_extras: bool = True,
) -> ModelSpec:
    """Extract ModelSpec from an ``attrs``-decorated class (``@define``, ``@frozen``, etc.).

    Requires ``pip install velarium[attrs]`` (or ``attrs`` in the environment).

    **Policy:** ``TypeSpec`` comes from resolved **annotations** (same as other builders).
    **Defaults** from ``attrs`` fields are copied onto ``TypeSpec.default`` when not
    ``attrs.NOTHING`` and not ``attrs.Factory``. **Frozen** / **slots** are not mapped into ``ModelConfig`` in this MVP
    (``ModelConfig`` uses defaults); see **model-sources** docs in the repo.
    """
    try:
        import attrs as attrs_mod
    except ImportError as e:  # pragma: no cover
        raise ImportError(
            "modelspec_from_attrs_class requires attrs; install velarium[attrs]"
        ) from e

    if not attrs_mod.has(cls):
        raise TypeError(f"{cls!r} is not an attrs class")

    # `attrs.Factory` is typed as overloads; use concrete class for isinstance (ty-safe).
    _attrs_factory_cls = type(attrs_mod.Factory(list))

    globalns = module_globals_for_class(cls)
    try:
        attrs_mod.resolve_types(cls, globalns=globalns, localns=None)
    except Exception:
        pass

    hints = get_resolved_hints(cls, include_extras=include_extras)

    fields: dict[str, TypeSpec] = {}
    for a in attrs_mod.fields(cls):
        raw = hints.get(a.name, a.type)
        ts = annotation_to_typespec(raw, globalns=globalns)
        ts = normalize_typespec(ts)
        static_default = a.default
        if static_default is not attrs_mod.NOTHING and not isinstance(
            static_default, _attrs_factory_cls
        ):
            ts = TypeSpec(
                kind=ts.kind,
                args=ts.args,
                optional=ts.optional,
                nullable=ts.nullable,
                default=static_default,
                name=ts.name,
                qualname=ts.qualname,
                module=ts.module,
            )
        fields[a.name] = ts

    meta = metadata_for_class(cls, include_source=True)
    cfg = ModelConfig(frozen=False, extra="forbid")
    return ModelSpec(name=cls.__name__, fields=fields, config=cfg, metadata=meta)
