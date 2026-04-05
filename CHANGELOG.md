# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-04-05

### Added

- **ModelSpec IR** — `ModelSpec`, `TypeSpec`, `TypeKind`, `ModelConfig`, `FieldSpec`, `ModelMetadata` ([docs/modelspec-ir.md](docs/modelspec-ir.md)).
- **JSON** — `dumps_model_spec` / `loads_model_spec` and dict helpers with deterministic ordering where applicable.
- **Normalization** — Union flatten/dedupe; optional encoding (`stubber.normalize`).
- **Builders** — `modelspec_from_dataclass`, `modelspec_from_typed_dict`; `type_to_typespec`, `annotation_to_typespec`.
- **Stubs** — `generate_pyi`, `render_typespec` (dataclass-oriented `.pyi` body).
- **CLI** (Typer) — `stubber ir`, `stubber stub`; `python -m stubber`.
- **Docs** — Design notes, IR spec, roadmap to 1.0.0.
- **CI** — GitHub Actions (pytest, mypy, build) on Python 3.10–3.13.

### Packaging

- Version is read from `stubber.__version__` via Hatch (`[tool.hatch.version]`); single source of truth for release numbers.

[Unreleased]: https://github.com/eddiethedean/stubber/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/eddiethedean/stubber/releases/tag/v0.1.0
