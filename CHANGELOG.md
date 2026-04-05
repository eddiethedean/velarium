# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Phase 0.2 — type surface and IR fidelity** — `TypeKind` extensions (`paramspec`, `typevartuple`, `protocol`, `nominal`) and optional `TypeSpec` metadata (`name`, `qualname`, `module`); JSON codec round-trips; centralized `get_resolved_hints` / `evaluate_forward_ref` in `velarium.typing_resolve`; richer `annotation_to_typespec` / `type_to_typespec` (e.g. `Annotated`, `Final`, `ClassVar`, `NotRequired`/`Required`, `TypeVar` name/bound, `Protocol`, nominal classes); `modelspec_from_typed_dict` respects `__optional_keys__` / `total=False` optional fields; [supported-annotations.md](docs/supported-annotations.md) documents the matrix and stub fallback (`velotype` renders `typing.Any` for kinds that lack stub declarations). Golden IR fixture under `tests/fixtures/ir_golden/`.

### Changed

- **`Callable[[...], R]`** parameter lists now use `isinstance(param_args, list)` so `list`/`get_origin` mismatch no longer drops the multi-parameter branch.
- Renamed PyPI package **`stubber`** → **`velotype`** (import `velotype`, CLI **`velotype`**). The **`stubber`** 0.1.0 release on PyPI is the previous name; new releases use **`velotype`**.
- Renamed scaffold package **`clarion`** → **`velocus`** — the PyPI project name **`clarion`** is not available for this maintainer ([PyPI project name policy](https://pypi.org/help/#project-name)).

## [0.1.0] - 2026-04-05

Coordinated **0.1.0** line for the monorepo: **`velarium`** and **`velotype`** are the supported libraries; **`viperis`**, **`morphra`**, **`granitus`**, and **`velocus`** (formerly scaffold **`clarion`** in-repo) ship as minimal **scaffold** packages (importable, documented as not yet implemented).

### Packages

| Package   | Version | Notes |
|-----------|---------|--------|
| velarium  | 0.1.0   | ModelSpec IR core (`typing_extensions` only). |
| velotype   | 0.1.0   | Depends on `velarium>=0.1.0`; IR → `.pyi` + CLI. |
| viperis, morphra, granitus, velocus | 0.1.0 | Pre-alpha scaffolds; no runtime dependencies. |

### Added

- **ModelSpec IR** — `ModelSpec`, `TypeSpec`, `TypeKind`, `ModelConfig`, `FieldSpec`, `ModelMetadata` ([docs/modelspec-ir.md](docs/modelspec-ir.md)).
- **JSON** — `dumps_model_spec` / `loads_model_spec` and dict helpers with deterministic ordering where applicable.
- **Normalization** — Union flatten/dedupe; optional encoding via `velarium.normalize`.
- **Builders** — `modelspec_from_dataclass`, `modelspec_from_typed_dict`; `type_to_typespec`, `annotation_to_typespec`.
- **Stubs** — `generate_pyi`, `render_typespec` (dataclass-oriented `.pyi` body).
- **CLI** (Typer) — `velotype ir`, `velotype stub`; `python -m velotype`.
- **`py.typed`** markers for **`velarium`** and **`velotype`** (PEP 561).
- **CI** — GitHub Actions (pytest, ty, build all packages) on Python 3.10–3.13.

### Changed

- **Monorepo** — Split into **`velarium`** (core ModelSpec IR) and **`velotype`** (IR → `.pyi` + CLI). Scaffold packages: **`viperis`**, **`morphra`**, **`granitus`**, **`velocus`**. Root **[uv](https://docs.astral.sh/uv/)** workspace; see [docs/valarium.md](docs/valarium.md) and [README.md](README.md).
- **`velotype`** re-exports IR APIs from `velotype` for compatibility; prefer `from velarium import …` for IR-only use.
- Replaced **mypy** with **[Astral ty](https://docs.astral.sh/ty/)** for static typing in dev and CI (`[tool.ty]` in root `pyproject.toml`).
- `typing_extensions.is_typeddict` used directly in `modelspec_from_typed_dict` (removed redundant try/except).
- Removed unreachable `get_origin` + `Enum` branch in `annotations.type_to_typespec` (enum classes are handled via `isinstance(t, type)`).

### Documentation

- [docs/design.md](docs/design.md), [docs/modelspec-ir.md](docs/modelspec-ir.md), [docs/valarium.md](docs/valarium.md), [docs/README.md](docs/README.md) for the Velarium ecosystem.
- [docs/ROADMAP.md](docs/ROADMAP.md) and [docs/releasing.md](docs/releasing.md) for workspace layout and releases.
- Per-package [packages/*/README.md](packages/) (`velarium`, `velotype`, `viperis`, `morphra`, `granitus`, `velocus`).

[Unreleased]: https://github.com/eddiethedean/velarium/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/eddiethedean/velarium/releases/tag/v0.1.0
