# stubber

**Role in Velarium:** **IR → `.pyi`** — render Velarium (ModelSpec) IR as minimal stub text, and expose the **`stubber`** CLI for quick IR export and stub generation from live classes.

| | |
|---|---|
| **PyPI** | `stubber` |
| **Depends on** | [**velarium**](../velarium/README.md) (required) |
| **CLI** | `stubber ir`, `stubber stub` (also `python -m stubber`) |

The IR types and builders live in **`velarium`**. **`stubber`** re-exports most public IR symbols from `stubber` for backward compatibility; prefer `from velarium import …` in new code when you only need IR.

## Install

```bash
pip install stubber
```

From the monorepo root:

```bash
uv sync --group dev
# or
pip install -e packages/velarium -e "packages/stubber[dev]"
```

## CLI

```bash
stubber ir myapp.models:User
stubber ir myapp.models:User -o user.ir.json
stubber stub myapp.models:User -o user.pyi
```

## Library

```python
from velarium import modelspec_from_dataclass, dumps_model_spec
from stubber import generate_pyi

spec = modelspec_from_dataclass(MyModel)
print(generate_pyi(spec))
```

## Version

`__version__` is in `stubber/__init__.py` (Hatch dynamic metadata in this package’s `pyproject.toml`).

## See also

- [docs/modelspec-ir.md](../../docs/modelspec-ir.md) — IR schema  
- [docs/valarium.md](../../docs/valarium.md) — ecosystem and backends  
- [Documentation index](../../docs/README.md)
