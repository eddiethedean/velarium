# API reference (public surface)

Hand-maintained index of **tier‑1** public symbols. Source of truth for **exports** is `__all__` in each package’s `__init__.py`.

**Policy:** Prefer `from velarium import …` / `from velotype import …` for the symbols below. Submodules remain importable for advanced use (see [stability.md](stability.md)).

## `velarium`

Defined in [`packages/velarium/velarium/__init__.py`](https://github.com/eddiethedean/velarium/blob/main/packages/velarium/velarium/__init__.py).

| Symbol | Description |
|--------|-------------|
| `MODEL_SPEC_FORMAT_VERSION` | Current ModelSpec JSON **`format_version`** wire integer (JSON number without fraction; not boolean/float; see [migration-ir.md](migration-ir.md)). |
| `ModelSpec`, `FieldSpec`, `ModelConfig`, `ModelMetadata`, `TypeSpec`, `TypeKind` | Core IR types (`velarium.ir`). |
| `dumps_model_spec`, `loads_model_spec`, `model_spec_to_dict`, `model_spec_from_dict` | JSON codec (`velarium.json_codec`). |
| `annotation_to_typespec`, `type_to_typespec` | Annotation → `TypeSpec` (`velarium.annotations`). |
| `metadata_for_class` | Optional model metadata (`velarium.model_metadata`). |
| `modelspec_from_attrs_class` | attrs class → `ModelSpec` (requires extra). |
| `modelspec_from_dataclass`, `modelspec_from_typed_dict`, `typespec_from_object` | Builders (`velarium.modelspec_build`). |
| `modelspec_from_pydantic_model` | Pydantic v2 → `ModelSpec` (requires extra). |
| `normalize_typespec`, `normalize_union`, `optional_to_union` | Normalization (`velarium.normalize`). |

## `velotype`

Defined in [`packages/velotype/velotype/__init__.py`](https://github.com/eddiethedean/velarium/blob/main/packages/velotype/velotype/__init__.py).

Includes **all** `velarium` exports above, plus:

| Symbol | Description |
|--------|-------------|
| `format_stub_text` | Post-process stub text (optional **ruff** formatting). |
| `generate_pyi` | `ModelSpec` → `.pyi` body text. |
| `render_typespec` | Render a `TypeSpec` as type string for stubs. |

### CLI

- **`velotype ir`**, **`velotype stub`** — import path targets (`module:Class`).
- **`velotype batch stub`**, **`velotype batch ir`** — package-wide discovery; see [tutorial-stubs.md](tutorial-stubs.md).
- **`velotype watch stub`** — optional **`velotype[watch]`** extra.
- **`python -m velotype`** — same commands.

### `velotype.batch` (extended)

Not re-exported at package root; stable for scripting alongside the CLI:

- **`emit_batch_stubs`**, **`emit_batch_ir`** — programmatic batch emission (see [performance.md](performance.md) for cache options).

## Deprecations

**None** as of **0.8.0**; see [stability.md](stability.md) and [CHANGELOG.md](../CHANGELOG.md).

## Scaffold packages

**viperis**, **morphra**, **granitus**, **velocus** are versioned in lockstep but remain **pre-1.0 scaffolds**; public API promises follow each package’s README and roadmap, not this tier‑1 table.
