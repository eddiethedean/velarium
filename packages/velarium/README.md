# velarium

**Role in Velarium:** core **ModelSpec IR** — normalized types (`TypeSpec`, `TypeKind`, …), **`ModelSpec`**, JSON codec, union normalization, and builders that turn dataclasses and `TypedDict` into IR.

| | |
|---|---|
| **PyPI** | `velarium` |
| **Import** | `import velarium` / `from velarium.ir import ModelSpec, TypeSpec` |
| **Dependencies** | `typing_extensions` only |

Downstream packages (e.g. [**stubber**](../stubber/README.md)) consume this IR to emit `.pyi` stubs and other artifacts. The IR contract is specified in [docs/modelspec-ir.md](../../docs/modelspec-ir.md); ecosystem context is in [docs/valarium.md](../../docs/valarium.md) and [docs/design.md](../../docs/design.md).

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
