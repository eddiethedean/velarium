# Velarium

[![CI](https://github.com/eddiethedean/velarium/actions/workflows/ci.yml/badge.svg)](https://github.com/eddiethedean/velarium/actions/workflows/ci.yml)
[![velarium on PyPI](https://img.shields.io/pypi/v/velarium.svg?label=velarium)](https://pypi.org/project/velarium/)
[![velotype on PyPI](https://img.shields.io/pypi/v/velotype.svg?label=velotype)](https://pypi.org/project/velotype/)
[![Python versions](https://img.shields.io/pypi/pyversions/velarium.svg)](https://pypi.org/project/velarium/)
[![Documentation](https://readthedocs.org/projects/velarium/badge/?version=latest)](https://velarium.readthedocs.io/en/latest/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/eddiethedean/velarium/blob/main/LICENSE)

**Repository:** [github.com/eddiethedean/velarium](https://github.com/eddiethedean/velarium) · **Documentation:** [velarium.readthedocs.io](https://velarium.readthedocs.io/en/latest/)

**Velarium** is a Python monorepo built around a shared **ModelSpec IR**: a normalized representation of models and types, with a JSON codec and pluggable backends. The supported backend today is **stub** generation (`.pyi`) via [**velotype**](https://pypi.org/project/velotype/). IR can be built from dataclasses, `TypedDict`, Pydantic v2, and attrs (see [Model sources](https://velarium.readthedocs.io/en/latest/model-sources/)). **Spark-like** schemas, **IR → Pydantic codegen** ([**morphra**](https://pypi.org/project/morphra/)), and a unified umbrella CLI ([**velocus**](https://pypi.org/project/velocus/)) are on the [roadmap](https://velarium.readthedocs.io/en/latest/ROADMAP/).

- **Single IR** — One structure for tooling to agree on, instead of re-parsing Python differently in every consumer.
- **Core library** — [**velarium** on PyPI](https://pypi.org/project/velarium/): types, normalization, JSON, and builders (dataclass, `TypedDict`, Pydantic, attrs → `ModelSpec`). Annotation → `TypeSpec` behavior is in [Supported annotations](https://velarium.readthedocs.io/en/latest/supported-annotations/) (Phase **0.2**); builders and extras are in [Model sources](https://velarium.readthedocs.io/en/latest/model-sources/) (Phase **0.3**).
- **Stubs + CLI** — [**velotype** on PyPI](https://pypi.org/project/velotype/): IR → `.pyi`, **`velotype`** CLI (`ir`, `stub`, **`batch`**, optional **`watch`**). Stub guarantees and checker CI are in [Stub compatibility](https://velarium.readthedocs.io/en/latest/stub-compatibility/) (Phase **0.4**); batch workflows and tutorials are in [Tutorial: stubs](https://velarium.readthedocs.io/en/latest/tutorial-stubs/) and [Troubleshooting CLI](https://velarium.readthedocs.io/en/latest/troubleshooting-cli/) (Phase **0.5**). Performance and batch cache are in [Performance](https://velarium.readthedocs.io/en/latest/performance/) (Phase **0.6**); CLI / JSON hardening is in [Security](https://velarium.readthedocs.io/en/latest/security/) (Phase **0.7**); public API and IR **`format_version`** are in [API reference](https://velarium.readthedocs.io/en/latest/api-reference/), [Stability](https://velarium.readthedocs.io/en/latest/stability/), and [IR JSON migration](https://velarium.readthedocs.io/en/latest/migration-ir/) (Phase **0.8**).

Requires **Python 3.10+**. Coordinated library releases are tagged in [CHANGELOG.md](https://github.com/eddiethedean/velarium/blob/main/CHANGELOG.md); **0.8.0** is the current monorepo version for all six `packages/*` PyPI names (upload after tagging per [Installing & releasing](https://velarium.readthedocs.io/en/latest/RELEASING/)).

## Packages

| Package | PyPI | Role |
|--------|------|------|
| **velarium** | [pypi.org/project/velarium](https://pypi.org/project/velarium/) | Core IR: `TypeSpec`, `ModelSpec`, normalization, JSON; builders ([Model sources](https://velarium.readthedocs.io/en/latest/model-sources/)) — [README](https://github.com/eddiethedean/velarium/blob/main/packages/velarium/README.md) |
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

That installs the **`velarium-workspace`** root (not published to PyPI) plus workspace members **`velarium`** and **`velotype`**, with dev tools (tests, **Hypothesis**, **ty**, **Ruff**, `build`).

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

See [Tutorial: stubs](https://velarium.readthedocs.io/en/latest/tutorial-stubs/) for a full **clone → batch stub** walkthrough.

## Library

Import IR and JSON from **`velarium`**; use **`velotype`** for `generate_pyi`, `format_stub_text`, and related helpers. **`velotype`** still re-exports IR symbols for compatibility; new code can import from **`velarium`** directly when only IR is needed.

A checked-in script that runs the same pattern (plus JSON round-trip checks) lives at [`examples/getting_started.py`](examples/getting_started.py) — run `uv run python examples/getting_started.py` from a clone.

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

Integration and golden JSON IR tests live under `tests/` (`test_ir_integration.py`, `test_ir_golden.py`, `fixtures/ir_golden/`). Stub goldens (`ModelSpec` JSON + expected `.pyi`) live under `tests/fixtures/stub_corpus/`; **`test_stubgen_corpus.py`** compares **`generate_pyi`** output to those files. **Hypothesis** property tests (`test_property_json_codec.py`, `test_json_limits.py`) cover JSON round-trip (including **`format_version`** invariants and legacy JSON without that field), normalization idempotence, and optional deserialization limits (Phases **0.7**–**0.8**). CI enforces **100%** line coverage on `velarium` and `velotype` sources.

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

CI uses **`uv sync --locked`**: a **`lint`** job on **Ubuntu** runs [**ruff**](https://docs.astral.sh/ruff/) (`check` + `format --check`) and [**ty**](https://docs.astral.sh/ty/); **`pytest`** (including **Hypothesis** property tests) and wheel builds for all packages run on **Ubuntu** across Python 3.10–3.13, plus **Windows** and **macOS** on Python 3.12 (with **uv** dependency caching); a **`stub-check`** job runs pinned **mypy** + **Pyright** on `tests/fixtures/stub_corpus/` on all three OSes (see [.github/workflows/ci-reusable.yml](https://github.com/eddiethedean/velarium/blob/main/.github/workflows/ci-reusable.yml), invoked from [.github/workflows/ci.yml](https://github.com/eddiethedean/velarium/blob/main/.github/workflows/ci.yml)).

## Documentation

Hosted on **Read the Docs** ([MkDocs](https://www.mkdocs.org/) + [Material](https://squidfunk.github.io/mkdocs-material/)). Browse everything below on **[velarium.readthedocs.io](https://velarium.readthedocs.io/en/latest/)** (or jump into the repo’s `docs/` tree on GitHub if you prefer raw Markdown).

| | |
|---|---|
| [Documentation home](https://velarium.readthedocs.io/en/latest/) | Same content as the docs index |
| [User guides](https://velarium.readthedocs.io/en/latest/guides/) | Getting started, [whole-package stubs](https://velarium.readthedocs.io/en/latest/guides/package-stubs/), **`velotype`** CLI, **`velarium`** library |
| [API reference](https://velarium.readthedocs.io/en/latest/api-reference/) | Public **`velarium`** / **`velotype`** surface (`__all__`, CLI, batch helpers) |
| [Stability](https://velarium.readthedocs.io/en/latest/stability/) | Pre-1.0 semver and IR policy |
| [IR JSON migration](https://velarium.readthedocs.io/en/latest/migration-ir/) | **`format_version`**, legacy JSON, fixtures |
| [Performance](https://velarium.readthedocs.io/en/latest/performance/) | Batch `--cache-dir`, `VELARIUM_NORMALIZE_BACKEND`, scripts |
| [Velarium ecosystem](https://velarium.readthedocs.io/en/latest/valarium/) | Architecture and monorepo layout |
| [Design & philosophy](https://velarium.readthedocs.io/en/latest/design/) | Why the IR exists |
| [ModelSpec IR specification](https://velarium.readthedocs.io/en/latest/modelspec-ir/) | Schema, normalization, JSON wire **`format_version`** |
| [Supported annotations](https://velarium.readthedocs.io/en/latest/supported-annotations/) | Annotation → IR matrix, gaps, stub behavior |
| [Model sources](https://velarium.readthedocs.io/en/latest/model-sources/) | Builders (dataclass, `TypedDict`, Pydantic, attrs), extras, policies |
| [Stub compatibility](https://velarium.readthedocs.io/en/latest/stub-compatibility/) | Generated `.pyi` guarantees, **`generate_pyi`** options, CI **mypy** / **Pyright** |
| [Roadmap](https://velarium.readthedocs.io/en/latest/ROADMAP/) | Planned work |
| [Tutorial: stubs](https://velarium.readthedocs.io/en/latest/tutorial-stubs/) | Clone → **`velotype batch stub`** |
| [Troubleshooting CLI](https://velarium.readthedocs.io/en/latest/troubleshooting-cli/) | Exit codes, imports, pre-commit |
| [IR JSON interchange](https://velarium.readthedocs.io/en/latest/interchange-ir-json/) | Non-Python consumers |
| [Installing & releasing](https://velarium.readthedocs.io/en/latest/RELEASING/) | Builds and PyPI; [Read the Docs setup](https://velarium.readthedocs.io/en/latest/RELEASING/#documentation-site-read-the-docs) |
| [Security](https://velarium.readthedocs.io/en/latest/security/) | CLI trust model, JSON limits, disclosure (Phase **0.7**) |
| [Changelog (docs)](https://velarium.readthedocs.io/en/latest/changelog/) | Pointer to release notes; canonical file: [CHANGELOG.md](https://github.com/eddiethedean/velarium/blob/main/CHANGELOG.md) on GitHub |

Build config for the doc site: [`.readthedocs.yaml`](https://github.com/eddiethedean/velarium/blob/main/.readthedocs.yaml), [`mkdocs.yml`](https://github.com/eddiethedean/velarium/blob/main/mkdocs.yml).

## License

MIT — see [LICENSE](https://github.com/eddiethedean/velarium/blob/main/LICENSE).
