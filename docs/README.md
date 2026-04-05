# Velarium documentation

Welcome to the **Velarium** monorepo docs: a shared **ModelSpec IR** (`velarium`), backends like **`velotype`** (`.pyi`), and scaffold packages for the full pipeline in [valarium.md](https://github.com/eddiethedean/velarium/blob/main/docs/valarium.md).

## Start here

| Document | Contents |
|----------|----------|
| **[Velarium ecosystem spec](https://github.com/eddiethedean/velarium/blob/main/docs/valarium.md)** | Components, pipeline, architecture, **monorepo `packages/`** layout |
| **[Design & philosophy](https://github.com/eddiethedean/velarium/blob/main/docs/design.md)** | Why the IR exists, how we relate to mypy/Pyright/Pydantic, compiler-style framing |
| **[ModelSpec IR specification](https://github.com/eddiethedean/velarium/blob/main/docs/modelspec-ir.md)** | `ModelSpec`, `TypeSpec`, `TypeKind`, normalization, JSON — **implemented in `velarium`** |
| **[Supported annotations (Phase 0.2)](https://github.com/eddiethedean/velarium/blob/main/docs/supported-annotations.md)** | Annotation → IR matrix, PEP 563 / forward refs, TypedDict keys, known gaps |
| **[Model sources (Phase 0.3)](https://github.com/eddiethedean/velarium/blob/main/docs/model-sources.md)** | Builders: dataclass, TypedDict, Pydantic, attrs — install extras, policies |
| **[Roadmap to 1.0.0](https://github.com/eddiethedean/velarium/blob/main/docs/ROADMAP.md)** | Phased **0.x** work through stable **1.0.0** |
| **[Installing & releasing](https://github.com/eddiethedean/velarium/blob/main/docs/releasing.md)** | uv workspace, editable installs, builds, PyPI |

## Repository map

- **Root [README](https://github.com/eddiethedean/velarium/blob/main/README.md)** — Quick install, CLI examples, package table.
- **Source:** `packages/velarium` (IR), `packages/velotype` (stubs + CLI), `packages/viperis`, `packages/morphra`, `packages/granitus`, `packages/velocus` (scaffolds).
- **Changelog:** [CHANGELOG.md](https://github.com/eddiethedean/velarium/blob/main/CHANGELOG.md).

## Naming

- **Velarium** — Ecosystem and conceptual IR (“Velarium IR” = ModelSpec IR).
- **`velarium`** — [PyPI package](https://pypi.org/project/velarium/) with the core types and builders.
- **`velotype`** — [PyPI package](https://pypi.org/project/velotype/) for stub generation; re-exports IR symbols for compatibility.
