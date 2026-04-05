# velarium

**Role in Velarium:** core **ModelSpec IR** — normalized types (`TypeSpec`, `TypeKind`, …), **`ModelSpec`**, JSON codec, union normalization, and builders that turn dataclasses and `TypedDict` into IR.

| | |
|---|---|
| **PyPI** | `velarium` |
| **Import** | `import velarium` / `from velarium.ir import ModelSpec, TypeSpec` |
| **Dependencies** | `typing_extensions` only |

Downstream packages (e.g. [**velotype**](../velotype/README.md)) consume this IR to emit `.pyi` stubs and other artifacts. The IR contract is specified in [docs/modelspec-ir.md](../../docs/modelspec-ir.md); how Python annotations map to the IR is in [docs/supported-annotations.md](../../docs/supported-annotations.md). Ecosystem context is in [docs/valarium.md](../../docs/valarium.md) and [docs/design.md](../../docs/design.md).

**Public API (high level)**

| Area | Modules / entry points |
|------|-------------------------|
| IR types | `velarium.ir` — `ModelSpec`, `TypeSpec`, `TypeKind`, … |
| JSON | `velarium.json_codec` — `dumps_model_spec`, `loads_model_spec`, dict helpers |
| Normalization | `velarium.normalize` — `normalize_typespec`, unions, optional handling |
| Annotations | `velarium.annotations` — `type_to_typespec`, `annotation_to_typespec` |
| Builders | `velarium.modelspec_build` — `modelspec_from_dataclass`, `modelspec_from_typed_dict`, `typespec_from_object` |
| Resolution | `velarium.typing_resolve` — `get_resolved_hints`, `module_globals_for_class`, `evaluate_forward_ref` (used by builders; re-export not required for typical use) |

## Install

```bash
pip install velarium
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
