# Velarium

[![CI](https://github.com/eddiethedean/velarium/actions/workflows/ci.yml/badge.svg)](https://github.com/eddiethedean/velarium/actions/workflows/ci.yml)

**Velarium** is a Python monorepo built around a shared **ModelSpec IR**: a normalized representation of models and types, with a JSON codec and pluggable backends. The supported backend today is **stub** generation (`.pyi`) via **velotype**. IR can be built from dataclasses, `TypedDict`, Pydantic v2, and attrs (see [Model sources](https://github.com/eddiethedean/velarium/blob/main/docs/model-sources.md)). **Spark-like** schemas, **IR → Pydantic codegen** (morphra), and a unified umbrella CLI are on the [roadmap](https://github.com/eddiethedean/velarium/blob/main/docs/ROADMAP.md).

- **Single IR** — One structure for tooling to agree on, instead of re-parsing Python differently in every consumer.
- **Core library** — [velarium on PyPI](https://pypi.org/project/velarium/): types, normalization, JSON, and builders (dataclass, `TypedDict`, Pydantic, attrs → `ModelSpec`). Annotation → `TypeSpec` behavior is in [Supported annotations](https://github.com/eddiethedean/velarium/blob/main/docs/supported-annotations.md) (Phase **0.2**); builders and extras are in [Model sources](https://github.com/eddiethedean/velarium/blob/main/docs/model-sources.md) (Phase **0.3**).
- **Stubs + CLI** — [velotype on PyPI](https://pypi.org/project/velotype/): IR → `.pyi` and the `velotype` CLI (`ir`, `stub`).

Requires **Python 3.10+**. Coordinated library releases are tagged in [CHANGELOG.md](https://github.com/eddiethedean/velarium/blob/main/CHANGELOG.md); **0.3.0** is the current line for all six `packages/*` PyPI names.

## Packages

| Package | Role |
|--------|------|
| [**velarium**](https://pypi.org/project/velarium/) | Core IR: `TypeSpec`, `ModelSpec`, normalization, JSON; builders for dataclass, `TypedDict`, Pydantic, attrs ([Model sources](https://github.com/eddiethedean/velarium/blob/main/docs/model-sources.md)) |
| [**velotype**](https://pypi.org/project/velotype/) | IR → `.pyi`; **`velotype`** CLI |
| [**viperis**](https://pypi.org/project/viperis/) | Python source → IR *(scaffold)* |
| [**morphra**](https://pypi.org/project/morphra/) | IR → Pydantic *(scaffold)* |
| [**granitus**](https://pypi.org/project/granitus/) | IR → Spark-like schemas *(scaffold)* |
| [**velocus**](https://pypi.org/project/velocus/) | Ecosystem CLI *(scaffold; use **`velotype`** for now)* |

Scaffold packages are placeholders for the full pipeline; **velarium** and **velotype** are the supported libraries today.

## Install

From [PyPI](https://pypi.org/) (when you only need the libraries):

```bash
pip install velarium velotype
```

From a git clone, use the workspace root with [uv](https://github.com/astral-sh/uv) (recommended):

```bash
uv sync --group dev
```

That installs the **`velarium-workspace`** root (not published to PyPI) plus workspace members **`velarium`** and **`velotype`**, with dev tools (tests, **ty**, **Ruff**, `build`).

Without uv, editable installs:

```bash
pip install -e packages/velarium -e "packages/velotype[dev]"
```

## CLI (`velotype`)

Targets are import paths: `module:Class` or `module:Outer.Inner` (nested class).

```bash
velotype ir myapp.models:User
velotype ir myapp.models:User -o user.ir.json
velotype stub myapp.models:User -o user.pyi
python -m velotype ir myapp.models:User
```

## Library

Import IR and JSON from **`velarium`**; use **`velotype`** for `generate_pyi` and related helpers. **`velotype`** still re-exports IR symbols for compatibility, but new code can import from **`velarium`** directly.

```python
from dataclasses import dataclass

from velarium import dumps_model_spec, modelspec_from_dataclass
from velotype import generate_pyi


@dataclass
class User:
    name: str


spec = modelspec_from_dataclass(User)
print(dumps_model_spec(spec))
print(generate_pyi(spec))
```

## Development

Version constants: **`velarium`** — `packages/velarium/velarium/__init__.py`; **`velotype`** — `packages/velotype/velotype/__init__.py`.

Integration and golden JSON IR tests live under `tests/` (`test_ir_integration.py`, `test_ir_golden.py`, `fixtures/ir_golden/`). CI enforces **100%** line coverage on `velarium` and `velotype` sources.

```bash
uv sync --group dev
uv run pytest
uv run python -m ty check
uv run ruff format .
uv run ruff check .
```

Build wheels for every package under `packages/`:

```bash
for d in packages/*/; do (cd "$d" && uv run python -m build); done
```

CI runs **pytest**, **ty**, and wheel builds for all packages on Python 3.10–3.13 (see [.github/workflows/ci.yml](https://github.com/eddiethedean/velarium/blob/main/.github/workflows/ci.yml)).

## Documentation

| | |
|---|---|
| [Documentation index](https://github.com/eddiethedean/velarium/blob/main/docs/README.md) | Entry point for deeper docs |
| [Velarium ecosystem](https://github.com/eddiethedean/velarium/blob/main/docs/valarium.md) | Architecture and monorepo layout |
| [Design & philosophy](https://github.com/eddiethedean/velarium/blob/main/docs/design.md) | Why the IR exists |
| [ModelSpec IR specification](https://github.com/eddiethedean/velarium/blob/main/docs/modelspec-ir.md) | Schema and normalization |
| [Supported annotations](https://github.com/eddiethedean/velarium/blob/main/docs/supported-annotations.md) | Annotation → IR matrix, gaps, stub behavior |
| [Model sources](https://github.com/eddiethedean/velarium/blob/main/docs/model-sources.md) | Builders (dataclass, TypedDict, Pydantic, attrs), extras, policies |
| [Roadmap](https://github.com/eddiethedean/velarium/blob/main/docs/ROADMAP.md) | Planned work |
| [Installing & releasing](https://github.com/eddiethedean/velarium/blob/main/docs/releasing.md) | Builds and PyPI |
| [Changelog](https://github.com/eddiethedean/velarium/blob/main/CHANGELOG.md) | Release notes |

## License

MIT — see [LICENSE](https://github.com/eddiethedean/velarium/blob/main/LICENSE).
