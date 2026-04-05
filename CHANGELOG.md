# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-04-05

Coordinated **0.1.0** line for the monorepo: **`velarium`** and **`stubber`** are the supported libraries; **`viperis`**, **`morphra`**, **`granitus`**, and **`clarion`** ship as minimal **scaffold** packages (importable, documented as not yet implemented).

### Packages

| Package   | Version | Notes |
|-----------|---------|--------|
| velarium  | 0.1.0   | ModelSpec IR core (`typing_extensions` only). |
| stubber   | 0.1.0   | Depends on `velarium>=0.1.0`; IR → `.pyi` + CLI. |
| viperis, morphra, granitus, clarion | 0.1.0 | Pre-alpha scaffolds; no runtime dependencies. |

### Added

- **ModelSpec IR** — `ModelSpec`, `TypeSpec`, `TypeKind`, `ModelConfig`, `FieldSpec`, `ModelMetadata` ([docs/modelspec-ir.md](docs/modelspec-ir.md)).
- **JSON** — `dumps_model_spec` / `loads_model_spec` and dict helpers with deterministic ordering where applicable.
- **Normalization** — Union flatten/dedupe; optional encoding via `velarium.normalize`.
- **Builders** — `modelspec_from_dataclass`, `modelspec_from_typed_dict`; `type_to_typespec`, `annotation_to_typespec`.
- **Stubs** — `generate_pyi`, `render_typespec` (dataclass-oriented `.pyi` body).
- **CLI** (Typer) — `stubber ir`, `stubber stub`; `python -m stubber`.
- **`py.typed`** markers for **`velarium`** and **`stubber`** (PEP 561).
- **CI** — GitHub Actions (pytest, ty, build all packages) on Python 3.10–3.13.

### Changed

- **Monorepo** — Split into **`velarium`** (core ModelSpec IR) and **`stubber`** (IR → `.pyi` + CLI). Scaffold packages: **`viperis`**, **`morphra`**, **`granitus`**, **`clarion`**. Root **[uv](https://docs.astral.sh/uv/)** workspace; see [docs/valarium.md](docs/valarium.md) and [README.md](README.md).
- **`stubber`** re-exports IR APIs from `stubber` for compatibility; prefer `from velarium import …` for IR-only use.
- Replaced **mypy** with **[Astral ty](https://docs.astral.sh/ty/)** for static typing in dev and CI (`[tool.ty]` in root `pyproject.toml`).
- `typing_extensions.is_typeddict` used directly in `modelspec_from_typed_dict` (removed redundant try/except).
- Removed unreachable `get_origin` + `Enum` branch in `annotations.type_to_typespec` (enum classes are handled via `isinstance(t, type)`).

### Documentation

- [docs/design.md](docs/design.md), [docs/modelspec-ir.md](docs/modelspec-ir.md), [docs/valarium.md](docs/valarium.md), [docs/README.md](docs/README.md) for the Velarium ecosystem.
- [docs/ROADMAP.md](docs/ROADMAP.md) and [docs/releasing.md](docs/releasing.md) for workspace layout and releases.
- Per-package [packages/*/README.md](packages/) (`velarium`, `stubber`, `viperis`, `morphra`, `granitus`, `clarion`).

[Unreleased]: https://github.com/eddiethedean/velarium/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/eddiethedean/velarium/releases/tag/v0.1.0
