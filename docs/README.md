# Velarium documentation

Welcome to the **Velarium** monorepo docs: a shared **ModelSpec IR** (`velarium`), backends like **`velotype`** (`.pyi`), and scaffold packages for the full pipeline in [valarium.md](valarium.md).

## Start here

| Document | Contents |
|----------|----------|
| **[Velarium ecosystem spec](valarium.md)** | Components, pipeline, architecture, **monorepo `packages/`** layout |
| **[Design & philosophy](design.md)** | Why the IR exists, how we relate to mypy/Pyright/Pydantic, compiler-style framing |
| **[ModelSpec IR specification](modelspec-ir.md)** | `ModelSpec`, `TypeSpec`, `TypeKind`, normalization, JSON — **implemented in `velarium`** |
| **[Supported annotations (Phase 0.2)](supported-annotations.md)** | Annotation → IR matrix, PEP 563 / forward refs, TypedDict keys, known gaps |
| **[Roadmap to 1.0.0](ROADMAP.md)** | Phased **0.x** work through stable **1.0.0** |
| **[Installing & releasing](releasing.md)** | uv workspace, editable installs, builds, PyPI |

## Repository map

- **Root [README](../README.md)** — Quick install, CLI examples, package table.
- **Source:** `packages/velarium` (IR), `packages/velotype` (stubs + CLI), `packages/viperis`, `packages/morphra`, `packages/granitus`, `packages/velocus` (scaffolds).
- **Changelog:** [CHANGELOG.md](../CHANGELOG.md).

## Naming

- **Velarium** — Ecosystem and conceptual IR (“Velarium IR” = ModelSpec IR).
- **`velarium`** — PyPI package with the core types and builders.
- **`velotype`** — PyPI package for stub generation; re-exports IR symbols for compatibility.
