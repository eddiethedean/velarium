# velotype

**Role in Velarium:** **IR → `.pyi`** — render Velarium (ModelSpec) IR as minimal stub text, and expose the **`velotype`** CLI for quick IR export and stub generation from live classes.

| | |
|---|---|
| **PyPI** | [pypi.org/project/velotype](https://pypi.org/project/velotype/) |
| **Repository** | [github.com/eddiethedean/velarium](https://github.com/eddiethedean/velarium) |
| **Depends on** | [**velarium** on PyPI](https://pypi.org/project/velarium/) (required) |
| **CLI** | `velotype ir`, `velotype stub` (also `python -m velotype`) |

The IR types and builders live in **`velarium`**. **`velotype`** re-exports the same public IR symbols and builder entry points as **`velarium`** (including `modelspec_from_pydantic_model` and `modelspec_from_attrs_class` when extras are installed); prefer `from velarium import …` in new code when you only need IR. See [docs/model-sources.md](https://github.com/eddiethedean/velarium/blob/main/docs/model-sources.md) for optional dependencies.

**Stub output:** `generate_pyi` / `render_typespec` aim for valid, checker-friendly `.pyi` text. Advanced `TypeKind` values (`protocol`, `nominal`, `paramspec`, `typevartuple`, and bare `typevar` in fields) are rendered as **`typing.Any`** in stubs so generated files do not invent `TypeVar`/`ParamSpec` declarations; the JSON IR still carries `name` / `qualname` / `module` for tooling. See [docs/supported-annotations.md](https://github.com/eddiethedean/velarium/blob/main/docs/supported-annotations.md) § Stub generation.

## Install

```bash
pip install velotype
```

From the monorepo root:

```bash
uv sync --group dev
# or
pip install -e packages/velarium -e "packages/velotype[dev]"
```

## CLI

```bash
velotype ir myapp.models:User
velotype ir myapp.models:User -o user.ir.json
velotype stub myapp.models:User -o user.pyi
```

## Library

```python
from velarium import modelspec_from_dataclass, dumps_model_spec
from velotype import generate_pyi

spec = modelspec_from_dataclass(MyModel)
print(generate_pyi(spec))
```

## Version

`__version__` is in `velotype/__init__.py` (Hatch dynamic metadata in this package’s `pyproject.toml`).

## See also

- [docs/modelspec-ir.md](https://github.com/eddiethedean/velarium/blob/main/docs/modelspec-ir.md) — IR schema  
- [docs/model-sources.md](https://github.com/eddiethedean/velarium/blob/main/docs/model-sources.md) — builders (dataclass, TypedDict, Pydantic, attrs) and `velarium` extras  
- [docs/valarium.md](https://github.com/eddiethedean/velarium/blob/main/docs/valarium.md) — ecosystem and backends  
- [Documentation index](https://github.com/eddiethedean/velarium/blob/main/docs/README.md)
