# Velarium

[![CI](https://github.com/eddiethedean/valarium/actions/workflows/ci.yml/badge.svg)](https://github.com/eddiethedean/valarium/actions/workflows/ci.yml)

**Velarium** is a Python monorepo built around a shared **ModelSpec IR**: a normalized representation of models and types, with a JSON codec and pluggable backends. Today the main backend is **stub** generation (`.pyi`); Pydantic, Spark-like schemas, and a unified CLI are on the [roadmap](docs/ROADMAP.md).

- **Single IR** — One structure for tooling to agree on, instead of re-parsing Python differently in every consumer.
- **Core library** — [`velarium`](packages/velarium/README.md) on PyPI: types, normalization, JSON, and builders (e.g. dataclass → `ModelSpec`).
- **Stubs + CLI** — [`stubber`](packages/stubber/README.md): IR → `.pyi` and the `stubber` CLI (`ir`, `stub`).

Requires **Python 3.10+**.

## Packages

| Package | Role |
|--------|------|
| [**velarium**](packages/velarium/README.md) | Core IR: `TypeSpec`, `ModelSpec`, normalization, JSON, dataclass / `TypedDict` → IR |
| [**stubber**](packages/stubber/README.md) | IR → `.pyi`; **`stubber`** CLI |
| [**viperis**](packages/viperis/README.md) | Python source → IR *(scaffold)* |
| [**morphra**](packages/morphra/README.md) | IR → Pydantic *(scaffold)* |
| [**granitus**](packages/granitus/README.md) | IR → Spark-like schemas *(scaffold)* |
| [**clarion**](packages/clarion/README.md) | Ecosystem CLI *(scaffold; use **`stubber`** for now)* |

Scaffold packages are placeholders for the full pipeline; **velarium** and **stubber** are the supported libraries today.

## Install

From [PyPI](https://pypi.org/) (when you only need the libraries):

```bash
pip install velarium stubber
```

From a git clone, use the workspace root with [uv](https://docs.astral.sh/uv/) (recommended):

```bash
uv sync --group dev
```

That installs the **`velarium-workspace`** root (not published to PyPI) plus workspace members **`velarium`** and **`stubber`**, with dev tools (tests, **ty**, **Ruff**, `build`).

Without uv, editable installs:

```bash
pip install -e packages/velarium -e "packages/stubber[dev]"
```

## CLI (`stubber`)

Targets are import paths: `module:Class` or `module:Outer.Inner` (nested class).

```bash
stubber ir myapp.models:User
stubber ir myapp.models:User -o user.ir.json
stubber stub myapp.models:User -o user.pyi
python -m stubber ir myapp.models:User
```

## Library

Import IR and JSON from **`velarium`**; use **`stubber`** for `generate_pyi` and related helpers. **`stubber`** still re-exports IR symbols for compatibility, but new code can import from **`velarium`** directly.

```python
from dataclasses import dataclass

from velarium import dumps_model_spec, modelspec_from_dataclass
from stubber import generate_pyi


@dataclass
class User:
    name: str


spec = modelspec_from_dataclass(User)
print(dumps_model_spec(spec))
print(generate_pyi(spec))
```

## Development

Version constants: **`velarium`** — `packages/velarium/velarium/__init__.py`; **`stubber`** — `packages/stubber/stubber/__init__.py`.

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

CI runs **pytest**, **ty**, and wheel builds for all packages on Python 3.10–3.13 (see [.github/workflows/ci.yml](.github/workflows/ci.yml)).

## Documentation

| | |
|---|---|
| [Documentation index](docs/README.md) | Entry point for deeper docs |
| [Velarium ecosystem](docs/valarium.md) | Architecture and monorepo layout |
| [Design & philosophy](docs/design.md) | Why the IR exists |
| [ModelSpec IR specification](docs/modelspec-ir.md) | Schema and normalization |
| [Roadmap](docs/ROADMAP.md) | Planned work |
| [Installing & releasing](docs/releasing.md) | Builds and PyPI |
| [Changelog](CHANGELOG.md) | Release notes |

## License

MIT — see [LICENSE](LICENSE).
