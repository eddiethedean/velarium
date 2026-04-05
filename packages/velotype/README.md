# velotype

[![PyPI version](https://img.shields.io/pypi/v/velotype.svg)](https://pypi.org/project/velotype/)
[![Python versions](https://img.shields.io/pypi/pyversions/velotype.svg)](https://pypi.org/project/velotype/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/eddiethedean/velarium/blob/main/LICENSE)

**Role in Velarium:** **IR → `.pyi`** — render Velarium (ModelSpec) IR as minimal stub text, and expose the **`velotype`** CLI for quick IR export and stub generation from live classes.

| | |
|---|---|
| **PyPI** | [pypi.org/project/velotype](https://pypi.org/project/velotype/) |
| **Repository** | [github.com/eddiethedean/velarium](https://github.com/eddiethedean/velarium) |
| **Python** | 3.10+ (follows **velarium**) |
| **Depends on** | [**velarium** on PyPI](https://pypi.org/project/velarium/) (required) |
| **CLI** | `velotype ir`, `velotype stub` (also `python -m velotype`) |

The IR types and builders live in **`velarium`**. **`velotype`** re-exports the same public IR symbols and builder entry points as **`velarium`** (including `modelspec_from_pydantic_model` and `modelspec_from_attrs_class` when extras are installed); prefer `from velarium import …` in new code when you only need IR. See [docs/model-sources.md](https://github.com/eddiethedean/velarium/blob/main/docs/model-sources.md) for optional dependencies.

**Stub output:** `generate_pyi` / `render_typespec` aim for valid, checker-friendly `.pyi` text. Optional **`generate_pyi`** arguments include **`module_docstring`**, **`header`** / **`footer`**, **`include_all`** (emits **`__all__`**), and **`style`** (`"default"` banner vs `"minimal"`). Optional **`format_stub_text(..., backend="ruff")`** runs **`ruff format -`** when available. Advanced `TypeKind` values (`protocol`, `nominal`, `paramspec`, `typevartuple`, and bare `typevar` in fields) are rendered as **`typing.Any`** in stubs so generated files do not invent `TypeVar`/`ParamSpec` declarations; the JSON IR still carries `name` / `qualname` / `module` for tooling.

| Topic | Doc |
|-------|-----|
| Stub fallbacks | [docs/supported-annotations.md](https://github.com/eddiethedean/velarium/blob/main/docs/supported-annotations.md) |
| Guarantees, imports, CI **mypy** / **Pyright** | [docs/stub-compatibility.md](https://github.com/eddiethedean/velarium/blob/main/docs/stub-compatibility.md) |

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
from velotype import format_stub_text, generate_pyi

spec = modelspec_from_dataclass(MyModel)
print(generate_pyi(spec))
# Optional: print(format_stub_text(generate_pyi(spec), backend="ruff"))
```

## Version

`__version__` is in `velotype/__init__.py` (Hatch dynamic metadata in this package’s `pyproject.toml`).

## See also

- [docs/modelspec-ir.md](https://github.com/eddiethedean/velarium/blob/main/docs/modelspec-ir.md) — IR schema  
- [docs/model-sources.md](https://github.com/eddiethedean/velarium/blob/main/docs/model-sources.md) — builders (dataclass, TypedDict, Pydantic, attrs) and `velarium` extras  
- [docs/stub-compatibility.md](https://github.com/eddiethedean/velarium/blob/main/docs/stub-compatibility.md) — stub guarantees and CI validation  
- [docs/valarium.md](https://github.com/eddiethedean/velarium/blob/main/docs/valarium.md) — ecosystem and backends  
- [Repository README](https://github.com/eddiethedean/velarium/blob/main/README.md)  
- [Documentation index](https://github.com/eddiethedean/velarium/blob/main/docs/README.md)  
- [Roadmap](https://github.com/eddiethedean/velarium/blob/main/docs/ROADMAP.md) — Phase **0.4** (stub quality)  
- [Changelog](https://github.com/eddiethedean/velarium/blob/main/CHANGELOG.md)

## License

MIT — see [LICENSE](https://github.com/eddiethedean/velarium/blob/main/LICENSE).
