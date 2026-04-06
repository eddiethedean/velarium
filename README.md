# Velarium

[![CI](https://github.com/eddiethedean/velarium/actions/workflows/ci.yml/badge.svg)](https://github.com/eddiethedean/velarium/actions/workflows/ci.yml)
[![velarium on PyPI](https://img.shields.io/pypi/v/velarium.svg?label=velarium)](https://pypi.org/project/velarium/)
[![velotype on PyPI](https://img.shields.io/pypi/v/velotype.svg?label=velotype)](https://pypi.org/project/velotype/)
[![Python versions](https://img.shields.io/pypi/pyversions/velarium.svg)](https://pypi.org/project/velarium/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/eddiethedean/velarium/blob/main/LICENSE)

**Repository:** [github.com/eddiethedean/velarium](https://github.com/eddiethedean/velarium)

**Velarium** is a Python monorepo built around a shared **ModelSpec IR**: a normalized representation of models and types, with a JSON codec and pluggable backends. The supported backend today is **stub** generation (`.pyi`) via [**velotype**](https://pypi.org/project/velotype/). IR can be built from dataclasses, `TypedDict`, Pydantic v2, and attrs (see [Model sources](https://github.com/eddiethedean/velarium/blob/main/docs/model-sources.md)). **Spark-like** schemas, **IR → Pydantic codegen** ([**morphra**](https://pypi.org/project/morphra/)), and a unified umbrella CLI ([**velocus**](https://pypi.org/project/velocus/)) are on the [roadmap](https://github.com/eddiethedean/velarium/blob/main/docs/ROADMAP.md).

- **Single IR** — One structure for tooling to agree on, instead of re-parsing Python differently in every consumer.
- **Core library** — [**velarium** on PyPI](https://pypi.org/project/velarium/): types, normalization, JSON, and builders (dataclass, `TypedDict`, Pydantic, attrs → `ModelSpec`). Annotation → `TypeSpec` behavior is in [Supported annotations](https://github.com/eddiethedean/velarium/blob/main/docs/supported-annotations.md) (Phase **0.2**); builders and extras are in [Model sources](https://github.com/eddiethedean/velarium/blob/main/docs/model-sources.md) (Phase **0.3**).
- **Stubs + CLI** — [**velotype** on PyPI](https://pypi.org/project/velotype/): IR → `.pyi`, **`velotype`** CLI (`ir`, `stub`, **`batch`**, optional **`watch`**). Stub guarantees and checker CI are in [Stub compatibility](https://github.com/eddiethedean/velarium/blob/main/docs/stub-compatibility.md) (Phase **0.4**); batch workflows and tutorials are in [Tutorial: stubs](https://github.com/eddiethedean/velarium/blob/main/docs/tutorial-stubs.md) and [Troubleshooting CLI](https://github.com/eddiethedean/velarium/blob/main/docs/troubleshooting-cli.md) (Phase **0.5**).

Requires **Python 3.10+**. Coordinated library releases are tagged in [CHANGELOG.md](https://github.com/eddiethedean/velarium/blob/main/CHANGELOG.md); **0.6.0** is the current published line for all six `packages/*` PyPI names.

## Packages

| Package | PyPI | Role |
|--------|------|------|
| **velarium** | [pypi.org/project/velarium](https://pypi.org/project/velarium/) | Core IR: `TypeSpec`, `ModelSpec`, normalization, JSON; builders ([Model sources](https://github.com/eddiethedean/velarium/blob/main/docs/model-sources.md)) — [README](https://github.com/eddiethedean/velarium/blob/main/packages/velarium/README.md) |
| **velotype** | [pypi.org/project/velotype](https://pypi.org/project/velotype/) | IR → `.pyi`; **`velotype`** CLI — [README](https://github.com/eddiethedean/velarium/blob/main/packages/velotype/README.md) |
| **viperis** | [pypi.org/project/viperis](https://pypi.org/project/viperis/) | Python source → IR *(scaffold)* — [README](https://github.com/eddiethedean/velarium/blob/main/packages/viperis/README.md) |
| **morphra** | [pypi.org/project/morphra](https://pypi.org/project/morphra/) | IR → Pydantic *(scaffold)* — [README](https://github.com/eddiethedean/velarium/blob/main/packages/morphra/README.md) |
| **granitus** | [pypi.org/project/granitus](https://pypi.org/project/granitus/) | IR → Spark-like schemas *(scaffold)* — [README](https://github.com/eddiethedean/velarium/blob/main/packages/granitus/README.md) |
| **velocus** | [pypi.org/project/velocus](https://pypi.org/project/velocus/) | Ecosystem CLI *(scaffold; use **velotype** for stubs today)* — [README](https://github.com/eddiethedean/velarium/blob/main/packages/velocus/README.md) |

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
velotype batch stub myapp.models --out-dir stubs/
velotype batch stub myapp.models --out-dir stubs/ --cache-dir .velotype-cache
python -m velotype ir myapp.models:User
```

See [docs/tutorial-stubs.md](https://github.com/eddiethedean/velarium/blob/main/docs/tutorial-stubs.md) for a full **clone → batch stub** walkthrough.

## Library

Import IR and JSON from **`velarium`**; use **`velotype`** for `generate_pyi`, `format_stub_text`, and related helpers. **`velotype`** still re-exports IR symbols for compatibility; new code can import from **`velarium`** directly when only IR is needed.

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

Version constants: **`velarium`** — `packages/velarium/velarium/__init__.py`; **`velotype`** — `packages/velotype/velotype/__init__.py` (all six `packages/*` names share the same **`__version__`**).

Integration and golden JSON IR tests live under `tests/` (`test_ir_integration.py`, `test_ir_golden.py`, `fixtures/ir_golden/`). Stub goldens (`ModelSpec` JSON + expected `.pyi`) live under `tests/fixtures/stub_corpus/`; **`test_stubgen_corpus.py`** compares **`generate_pyi`** output to those files. CI enforces **100%** line coverage on `velarium` and `velotype` sources.

The root `pyproject.toml` sets `pythonpath = ["tests"]` for pytest so fixture packages (for example `fixtures.batch_pkg`) import without extra env. Batch CLI coverage lives in **`tests/test_batch.py`**, **`tests/test_batch_subprocess.py`** (subprocess `python -m velotype`), and **`tests/test_cli.py`**.

```bash
uv sync --group dev
uv run pytest
uv run python -m ty check
# Optional: same mypy + Pyright pass as the stub-check job (install checkers first)
uv sync --group stubcheck
uv run mypy --config-file tests/fixtures/stub_corpus/mypy.ini tests/fixtures/stub_corpus/*.pyi
uv run pyright --project tests/fixtures/stub_corpus
uv run ruff format .
uv run ruff check .
```

Build wheels for every package under `packages/`:

```bash
for d in packages/*/; do (cd "$d" && uv run python -m build); done
```

CI runs **pytest**, **ty**, and wheel builds for all packages on Python 3.10–3.13, and a separate **`stub-check`** job that runs pinned **mypy** + **Pyright** on `tests/fixtures/stub_corpus/` (see [.github/workflows/ci.yml](https://github.com/eddiethedean/velarium/blob/main/.github/workflows/ci.yml)).

## Documentation

| | |
|---|---|
| [Documentation index](https://github.com/eddiethedean/velarium/blob/main/docs/README.md) | Entry point for deeper docs |
| [Performance](https://github.com/eddiethedean/velarium/blob/main/docs/performance.md) | Batch `--cache-dir`, `VELARIUM_NORMALIZE_BACKEND`, scripts |
| [Velarium ecosystem](https://github.com/eddiethedean/velarium/blob/main/docs/valarium.md) | Architecture and monorepo layout |
| [Design & philosophy](https://github.com/eddiethedean/velarium/blob/main/docs/design.md) | Why the IR exists |
| [ModelSpec IR specification](https://github.com/eddiethedean/velarium/blob/main/docs/modelspec-ir.md) | Schema and normalization |
| [Supported annotations](https://github.com/eddiethedean/velarium/blob/main/docs/supported-annotations.md) | Annotation → IR matrix, gaps, stub behavior |
| [Model sources](https://github.com/eddiethedean/velarium/blob/main/docs/model-sources.md) | Builders (dataclass, TypedDict, Pydantic, attrs), extras, policies |
| [Stub compatibility](https://github.com/eddiethedean/velarium/blob/main/docs/stub-compatibility.md) | Generated `.pyi` guarantees, **`generate_pyi`** options, CI **mypy** / **Pyright** |
| [Roadmap](https://github.com/eddiethedean/velarium/blob/main/docs/ROADMAP.md) | Planned work |
| [Tutorial: stubs](https://github.com/eddiethedean/velarium/blob/main/docs/tutorial-stubs.md) | Clone → **`velotype batch stub`** |
| [Troubleshooting CLI](https://github.com/eddiethedean/velarium/blob/main/docs/troubleshooting-cli.md) | Exit codes, imports, pre-commit |
| [IR JSON interchange](https://github.com/eddiethedean/velarium/blob/main/docs/interchange-ir-json.md) | Non-Python consumers |
| [Installing & releasing](https://github.com/eddiethedean/velarium/blob/main/docs/RELEASING.md) | Builds and PyPI |
| [Changelog](https://github.com/eddiethedean/velarium/blob/main/CHANGELOG.md) | Release notes |

## License

MIT — see [LICENSE](https://github.com/eddiethedean/velarium/blob/main/LICENSE).
