# velarium

**Role in Velarium:** core **ModelSpec IR** — normalized types (`TypeSpec`, `TypeKind`, …), **`ModelSpec`**, JSON codec, union normalization, and builders that turn dataclasses, `TypedDict`, Pydantic `BaseModel`, and attrs classes into IR (see [model-sources.md](../../docs/model-sources.md)).

| | |
|---|---|
| **PyPI** | `velarium` |
| **Import** | `import velarium` / `from velarium.ir import ModelSpec, TypeSpec` |
| **Dependencies** | `typing_extensions` only; optional `velarium[pydantic]`, `velarium[attrs]`, or `velarium[sources]` |

Downstream packages (e.g. [**velotype**](../velotype/README.md)) consume this IR to emit `.pyi` stubs and other artifacts. The IR contract is specified in [docs/modelspec-ir.md](../../docs/modelspec-ir.md); how Python annotations map to the IR is in [docs/supported-annotations.md](../../docs/supported-annotations.md); builders and optional extras are in [docs/model-sources.md](../../docs/model-sources.md). Ecosystem context is in [docs/valarium.md](../../docs/valarium.md) and [docs/design.md](../../docs/design.md).

**Public API (high level)**

| Area | Modules / entry points |
|------|-------------------------|
| IR types | `velarium.ir` — `ModelSpec`, `TypeSpec`, `TypeKind`, … |
| JSON | `velarium.json_codec` — `dumps_model_spec`, `loads_model_spec`, dict helpers |
| Normalization | `velarium.normalize` — `normalize_typespec`, unions, optional handling |
| Annotations | `velarium.annotations` — `type_to_typespec`, `annotation_to_typespec` |
| Builders | `velarium.modelspec_build` — `modelspec_from_dataclass`, `modelspec_from_typed_dict`, `typespec_from_object`; `velarium.modelspec_pydantic` / `modelspec_from_pydantic_model` (extra); `velarium.modelspec_attrs` / `modelspec_from_attrs_class` (extra) |
| Resolution | `velarium.typing_resolve` — `get_resolved_hints`, `module_globals_for_class`, `evaluate_forward_ref` (used by builders; re-export not required for typical use) |

## Install

```bash
pip install velarium
# Optional: Pydantic v2 / attrs builders
pip install velarium[pydantic]   # or velarium[attrs] / velarium[sources]
```

From the monorepo root (with [uv](https://docs.astral.sh/uv/)):

```bash
uv sync --group dev
```

## Version

`__version__` lives in `velarium/__init__.py` (Hatch reads it from that package’s `pyproject.toml`).

## See also

- [Repository README](../../README.md) — full package table and workspace setup  
- [Documentation index](../../docs/README.md)
