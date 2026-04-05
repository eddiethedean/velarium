# Model sources (builders)

This document describes how **`velarium`** turns Python model definitions into **`ModelSpec` IR**. Choose a builder that matches how your types are declared.

## Summary

| Source | Function | Install |
|--------|----------|---------|
| **`@dataclass`** | `modelspec_from_dataclass` | core `velarium` only |
| **`typing.TypedDict`** | `modelspec_from_typed_dict` | core `velarium` only |
| **Pydantic v2 `BaseModel`** | `modelspec_from_pydantic_model` | `pip install velarium[pydantic]` |
| **attrs** (`@define`, …) | `modelspec_from_attrs_class` | `pip install velarium[attrs]` |

Convenience: `pip install velarium[sources]` installs **pydantic** and **attrs** extras.

## Policy: annotations vs runtime defaults

- **`TypeSpec`** (field types) comes from **resolved annotations**, using the same `annotation_to_typespec` / `get_type_hints` path as other builders (see [supported-annotations.md](supported-annotations.md)).
- **Field defaults** on `TypeSpec.default` are copied when a **static** default exists at extraction time.
- **Pydantic** `default_factory` is **not** run; IR has **no** default in that case (lossy).
- **Pydantic** `Field()` **constraints** (`ge`, `pattern`, …) are **not** represented in IR (lossy); use downstream tools if you need them.
- **attrs** **`attrs.field(factory=…)`** / **`attrs.Factory`** defaults are **not** copied to IR (same idea as Pydantic `default_factory`).
- **attrs** **frozen** / **slots** are **not** mapped into `ModelConfig` in the current release (defaults apply).

If annotations and runtime behavior disagree, **annotations win** for the static IR shape; defaults on `TypeSpec` reflect the model’s declared default when we can read it without executing arbitrary code.

## Pydantic v2

Requires **`pydantic>=2`**.

`model_config` is partially mapped: **`frozen`** and **`extra`** (`allow` / `forbid` / `ignore`) → `ModelConfig` in [`modelspec-ir.md`](modelspec-ir.md). Other settings are ignored in IR until a later phase.

## attrs

Requires **`attrs>=23`**.

Uses `attrs.resolve_types` when possible; failure is ignored (best-effort forward references).

## Metadata

`ModelMetadata` (module, optional file/line) is filled via `metadata_for_class` for dataclass, TypedDict, Pydantic, and attrs builders where `inspect` succeeds.

## See also

- [ModelSpec IR](modelspec-ir.md)
- [Supported annotations](supported-annotations.md)
- [Roadmap Phase 0.3](ROADMAP.md#phase-03--model-sources)
