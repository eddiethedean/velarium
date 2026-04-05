# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- **Monorepo** — Split into **`velarium`** (core ModelSpec IR) and **`stubber`** (IR → `.pyi` + CLI). Scaffold packages: **`viperis`**, **`morphra`**, **`granitus`**, **`clarion`**. Root **[uv](https://docs.astral.sh/uv/)** workspace; see [docs/valarium.md](docs/valarium.md) and [README.md](README.md).
- **`stubber` 0.2.0** — Depends on **`velarium`**; re-exports IR APIs from `stubber` for compatibility.
- Replaced **mypy** with **[Astral ty](https://docs.astral.sh/ty/)** for static typing in dev and CI (`[tool.ty]` in root `pyproject.toml`).
- `typing_extensions.is_typeddict` used directly in `modelspec_from_typed_dict` (removed redundant try/except).
- Removed unreachable `get_origin` + `Enum` branch in `annotations.type_to_typespec` (enum classes are handled via `isinstance(t, type)`).

### Added

- Expanded test suite (JSON, normalization, annotations, stubgen, CLI via Typer runner, `__main__`); **100% line coverage** on **`velarium`** / **`stubber`** sources enforced via `pytest-cov`.

### Documentation

- Rewrote **[docs/design.md](docs/design.md)**, **[docs/modelspec-ir.md](docs/modelspec-ir.md)**, **[docs/valarium.md](docs/valarium.md)**, **[docs/README.md](docs/README.md)** for the Velarium ecosystem (packages, pipeline, naming).
- Updated **[docs/ROADMAP.md](docs/ROADMAP.md)** and **[docs/releasing.md](docs/releasing.md)** for the workspace and tier-1 vs scaffold packages.
- Refreshed **[modelspec_ir.md](modelspec_ir.md)** (root pointer) and per-package **[packages/*/README.md](packages/)** (`velarium`, `stubber`, `viperis`, `morphra`, `granitus`, `clarion`).

## [0.1.0] - 2026-04-05

### Added

- **ModelSpec IR** — `ModelSpec`, `TypeSpec`, `TypeKind`, `ModelConfig`, `FieldSpec`, `ModelMetadata` ([docs/modelspec-ir.md](docs/modelspec-ir.md)).
- **JSON** — `dumps_model_spec` / `loads_model_spec` and dict helpers with deterministic ordering where applicable.
- **Normalization** — Union flatten/dedupe; optional encoding (`stubber.normalize` in the single-package layout; later `velarium.normalize` in the monorepo).
- **Builders** — `modelspec_from_dataclass`, `modelspec_from_typed_dict`; `type_to_typespec`, `annotation_to_typespec`.
- **Stubs** — `generate_pyi`, `render_typespec` (dataclass-oriented `.pyi` body).
- **CLI** (Typer) — `stubber ir`, `stubber stub`; `python -m stubber`.
- **Docs** — Design notes, IR spec, roadmap to 1.0.0.
- **CI** — GitHub Actions (pytest, ty, build) on Python 3.10–3.13.

### Packaging

- Version was read from `stubber.__version__` via Hatch (`[tool.hatch.version]`); single source of truth for release numbers (pre-monorepo layout).

[Unreleased]: https://github.com/eddiethedean/valarium/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/eddiethedean/stubber/releases/tag/v0.1.0
