# Velarium documentation

[![CI](https://github.com/eddiethedean/velarium/actions/workflows/ci.yml/badge.svg)](https://github.com/eddiethedean/velarium/actions/workflows/ci.yml)
[![velarium on PyPI](https://img.shields.io/pypi/v/velarium.svg?label=velarium)](https://pypi.org/project/velarium/)
[![velotype on PyPI](https://img.shields.io/pypi/v/velotype.svg?label=velotype)](https://pypi.org/project/velotype/)

**Repository:** [github.com/eddiethedean/velarium](https://github.com/eddiethedean/velarium)

Welcome to the **Velarium** monorepo docs: a shared **ModelSpec IR** ([**velarium** on PyPI](https://pypi.org/project/velarium/)), backends like [**velotype**](https://pypi.org/project/velotype/) (`.pyi`), and scaffold packages for the full pipeline in [valarium.md](https://github.com/eddiethedean/velarium/blob/main/docs/valarium.md).

## Start here

| Document | Contents |
|----------|----------|
| **[Velarium ecosystem spec](https://github.com/eddiethedean/velarium/blob/main/docs/valarium.md)** | Components, pipeline, architecture, **monorepo `packages/`** layout |
| **[Design & philosophy](https://github.com/eddiethedean/velarium/blob/main/docs/design.md)** | Why the IR exists, how we relate to mypy/Pyright/Pydantic, compiler-style framing |
| **[ModelSpec IR specification](https://github.com/eddiethedean/velarium/blob/main/docs/modelspec-ir.md)** | `ModelSpec`, `TypeSpec`, `TypeKind`, normalization, JSON — **implemented in `velarium`** |
| **[Supported annotations (Phase 0.2)](https://github.com/eddiethedean/velarium/blob/main/docs/supported-annotations.md)** | Annotation → IR matrix, PEP 563 / forward refs, TypedDict keys, known gaps |
| **[Model sources (Phase 0.3)](https://github.com/eddiethedean/velarium/blob/main/docs/model-sources.md)** | Builders: dataclass, TypedDict, Pydantic, attrs — install extras, policies |
| **[Stub compatibility (Phase 0.4)](https://github.com/eddiethedean/velarium/blob/main/docs/stub-compatibility.md)** | Guarantees vs best-effort for generated `.pyi`, imports, CI **mypy** / **Pyright** |
| **[Tutorial: stubs (Phase 0.5)](https://github.com/eddiethedean/velarium/blob/main/docs/tutorial-stubs.md)** | Clone → **`velotype batch stub`** / **`batch ir`** |
| **[Troubleshooting CLI](https://github.com/eddiethedean/velarium/blob/main/docs/troubleshooting-cli.md)** | Exit codes, **`PYTHONPATH`**, pre-commit |
| **[IR JSON interchange](https://github.com/eddiethedean/velarium/blob/main/docs/interchange-ir-json.md)** | Using **`dumps_model_spec`** JSON outside Python |
| **[Roadmap to 1.0.0](https://github.com/eddiethedean/velarium/blob/main/docs/ROADMAP.md)** | Phased **0.x** work through stable **1.0.0** |
| **[Installing & releasing](https://github.com/eddiethedean/velarium/blob/main/docs/RELEASING.md)** | uv workspace, editable installs, builds, PyPI |

## Package READMEs (source)

| Package | README |
|---------|--------|
| **velarium** | [packages/velarium/README.md](https://github.com/eddiethedean/velarium/blob/main/packages/velarium/README.md) |
| **velotype** | [packages/velotype/README.md](https://github.com/eddiethedean/velarium/blob/main/packages/velotype/README.md) |
| **viperis** | [packages/viperis/README.md](https://github.com/eddiethedean/velarium/blob/main/packages/viperis/README.md) |
| **morphra** | [packages/morphra/README.md](https://github.com/eddiethedean/velarium/blob/main/packages/morphra/README.md) |
| **granitus** | [packages/granitus/README.md](https://github.com/eddiethedean/velarium/blob/main/packages/granitus/README.md) |
| **velocus** | [packages/velocus/README.md](https://github.com/eddiethedean/velarium/blob/main/packages/velocus/README.md) |

## Repository map

- **Root [README](https://github.com/eddiethedean/velarium/blob/main/README.md)** — Quick install, CLI examples, package table.
- **Source:** `packages/velarium` (IR), `packages/velotype` (stubs + CLI), `packages/viperis`, `packages/morphra`, `packages/granitus`, `packages/velocus` (scaffolds).
- **Changelog:** [CHANGELOG.md](https://github.com/eddiethedean/velarium/blob/main/CHANGELOG.md).
- **CI:** [.github/workflows/ci.yml](https://github.com/eddiethedean/velarium/blob/main/.github/workflows/ci.yml) — pytest, **ty**, wheels, **`stub-check`** (**mypy** + **Pyright** on stub goldens).

## Naming

- **Velarium** — Ecosystem and conceptual IR (“Velarium IR” = ModelSpec IR).
- **`velarium`** — [PyPI package](https://pypi.org/project/velarium/) with the core types and builders.
- **`velotype`** — [PyPI package](https://pypi.org/project/velotype/) for stub generation; re-exports IR symbols for compatibility.
