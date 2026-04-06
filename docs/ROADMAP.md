# Roadmap to 1.0.0

This document is the **release plan** for the **Velarium** monorepo and its **six** installable Python packages: what we ship in each **0.X.*** line, how phases depend on each other, what **1.0.0** commits to, and how the **planned backend packages** advance on **1.x phases** ([Scaffold packages: 1.x phase plan](#scaffold-packages-1x-phase-plan)). A **tier‑1 × 0.x phase** matrix is in [Release alignment by phase and package](#release-alignment-by-phase-and-package). It complements [design.md](design.md) (why the IR exists) and [modelspec-ir.md](modelspec-ir.md) (schema details).

| Package | PyPI | Role today | Plan (see [Plans by package](#plans-by-package)) |
|---------|------|------------|-----------------------------------------------------|
| [**velarium**](../packages/velarium/README.md) | `velarium` | **Tier 1** — ModelSpec IR, JSON, normalization, builders | Phases **0.2–0.8**; owns IR contract and stability |
| [**velotype**](../packages/velotype/README.md) | `velotype` | **Tier 1** — IR → `.pyi`, **`velotype`** CLI | Phases **0.1–0.7**; stubs, CLI, tooling, hardening |
| [**viperis**](../packages/viperis/README.md) | `viperis` | **Scaffold** — Python source → IR | [Phases **1.1–1.3**](#viperis--1x-roadmap) (after stable **velarium** IR); groundwork in **0.2+** |
| [**morphra**](../packages/morphra/README.md) | `morphra` | **Scaffold** — IR → Pydantic | [Phases **1.1–1.3**](#morphra--1x-roadmap); groundwork in **0.3+** |
| [**granitus**](../packages/granitus/README.md) | `granitus` | **Scaffold** — IR → Spark-like schemas | [Phases **1.1–1.3**](#granitus--1x-roadmap); parallel **morphra** |
| [**velocus**](../packages/velocus/README.md) | `velocus` | **Scaffold** — umbrella ecosystem CLI | [Phases **1.1–1.3**](#velocus--1x-roadmap); after **velotype** **1.0** + a backend **1.1** |

**Conventions**

| Term | Meaning |
|------|--------|
| **0.x phase** | Monorepo **minor** series **0.X.*** until **1.0.0** — primarily **velarium** + **velotype** ([Phase dependency overview](#phase-dependency-overview)). |
| **1.x phase (scaffold)** | **Per-package** milestones **1.1**, **1.2**, **1.3** for **viperis**, **morphra**, **granitus**, **velocus** ([Scaffold packages: 1.x phase plan](#scaffold-packages-1x-phase-plan)). These track *feature maturity*; the monorepo **semver** tag still bumps all wheels together ([RELEASING.md](RELEASING.md)). |
| **Patch** | **0.X.Y** or **1.X.Y** — bugfixes, docs, and *small* additive changes that do not change the phase’s scope. |
| **Breaking change** | Removes or incompatibly changes a **documented public API** or **documented JSON IR** shape. Breaking changes are avoided in patch releases; before 1.0 they are allowed in minors with changelog notes. |

Dates are not promised; **order and dependencies** drive sequencing.

---

## Guiding principles

1. **IR first** — Normalization and JSON interchange are the contract; CLI and stubs are consumers.
2. **Checker-friendly outputs** — Generated `.pyi` and idioms should aim to work under **mypy** and **Pyright** without forked “dialects.”
3. **Honest fallbacks** — Prefer an explicit `any` (or documented lossy node) over silent wrong types.
4. **Backend-agnostic core** — Optional native acceleration must not change IR semantics (same tests, same JSON meaning).
5. **Small API surface** — Prefer a few well-documented entry points over many overlapping helpers.

---

## Non-goals (for 1.0.0)

These are **out of scope** for the 1.0.0 milestone unless explicitly moved into a phase below:

- Replacing **mypy**, **Pyright**, or **Ruff** as a type checker or linter.
- Full **inference** of untyped code (today’s builders focus on stated annotations and model structure).
- Guaranteeing identical behavior to every edge case in every checker—we target **practical** portability, documented where we diverge.
- A **GUI** or language-server implementation (downstream of IR is fine; shipping one is not required for 1.0).

---

## What “1.0.0” means

At **1.0.0**, adopters can rely on:

| Area | Commitment |
|------|------------|
| **Python API** | [Semver](https://semver.org/): breaking changes only in major versions; deprecations follow a stated minimum period. |
| **Public surface** | Explicit list of supported modules, functions, and classes (see Phase 0.8). |
| **ModelSpec JSON** | Documented schema version or evolution rules; breaking IR changes require a major **or** a clearly versioned alternate export. |
| **Support matrix** | Documented Python versions and tier-1 / tier-2 support for checkers and optional deps. |
| **Quality** | Automated tests, CI on supported platforms, and a maintained **CHANGELOG**. |
| **Security** | Documented threat model for CLI (dynamic import / `eval` boundaries) and responsible disclosure process. |

Patch releases **1.0.z** are bugfixes and safe doc/typing updates only.

---

## Phase dependency overview

Phases build on earlier work:

```text
0.1 foundation ──► 0.2 IR fidelity ──► 0.3 model sources
                         │                      │
                         └──────────┬───────────┘
                                    ▼
                         0.4 stub quality ──► 0.5 tooling
                                    │
                                    ▼
                         0.6 performance ──► 0.7 hardening
                                    │
                                    ▼
                         0.8 API / IR freeze ──► 0.9 RC ──► 1.0.0
```

You can parallelize **some** work (e.g. docs vs code) within a phase, but **do not** promise 0.4-quality stubs before 0.2 has stabilized the IR shapes those stubs render from.

**Scaffold packages** (viperis, morphra, granitus, velocus) ship minimal **0.1.x** placeholders on PyPI; feature work below is **planned**, not promised by date.

```text
                    ┌─────────────┐
                    │  velarium   │  ← IR truth (JSON, types, normalization)
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
     ┌──────────┐   ┌──────────┐   ┌──────────┐
     │ viperis  │   │ velotype │   │ (future) │
     │ Py→IR    │   │ IR→.pyi  │   │ backends │
     └──────────┘   └────┬─────┘   └────┬─────┘
                         │              │
                    ┌────┴────┐    ┌────┴────┐
                    │ morphra │    │ granitus│
                    │ IR→Pyd  │    │ IR→Spark│
                    └────┬────┘    └────┬────┘
                         └──────┬─────┘
                                ▼
                          ┌──────────┐
                          │ velocus  │  ← orchestration CLI (optional)
                          └──────────┘
```

---

## Release alignment by phase and package

**Versioning:** Every tag bumps **all** `packages/*` to the same **`__version__`** (see [RELEASING.md](RELEASING.md)). Phases are **monorepo-wide**: tier‑1 exit criteria are what gate calling a line (e.g. **0.5.0**) “done” for the release notes—**scaffold** packages may still be placeholders on PyPI until their [exit criteria](#plans-by-package) are met, even though their version number moves in lockstep.

| Phase | **velarium** | **velotype** | **viperis** | **morphra** | **granitus** | **velocus** |
|-------|--------------|--------------|-------------|-------------|--------------|-------------|
| **0.1** | IR, JSON, dataclass/TypedDict builders, annotation MVP | Stubs + `velotype` CLI MVP | Placeholder | Placeholder | Placeholder | Placeholder |
| **0.2** | Annotation → IR fidelity, golden IR tests | Stubs track IR shapes | **Start** Python source → IR (depends on stable IR semantics) | — | — | — |
| **0.3** | Pydantic v2 + attrs sources, unified metadata | — | Continue | **Start** IR → Pydantic | **Start** IR → Spark-like | — |
| **0.4** | — | Checker‑validated `.pyi`, import/style, **stub-check** CI | Continue | Continue | Continue | — |
| **0.5** | — | Batch / pre-commit / repo workflows ([Phase 0.5](#phase-05--tooling-and-integrations)) | **Target** first “usable” slice (optional) | **Target** first “usable” path (optional) | **Target** first “usable” path (optional) | **Start** only if **velotype** + ≥1 other backend are worth orchestrating |
| **0.6** | Performance hooks, optional native acceleration ([Phase 0.6](#phase-06--performance-and-scale)) *(shipped **0.6.0**)* | Performance, incremental cache *(shipped **0.6.0**)* | Optional | Optional | Optional | Optional |
| **0.7** | — | Security / fuzzing / CLI limits ([Phase 0.7](#phase-07--hardening)) | — | — | — | Harden if already shipping |
| **0.8** | Public API audit + IR versioning ([Phase 0.8](#phase-08--api-and-ir-stability-prep)) | Track tier‑1 freeze | Docs vs IR spec; no contradiction | Stable emit API surface | Stable emit API surface | Subcommand freeze if shipped |
| **0.9** | RC ([Phase 0.9](#phase-09--release-candidate)) | RC | RC if feature-complete | RC if feature-complete | RC if feature-complete | RC if feature-complete |
| **1.0** | Core **1.0** | **1.x** stubs/CLI ([summary](#package-summary-toward-100)) | [Independent bar](#package-summary-toward-100) | [Independent bar](#package-summary-toward-100) | [Independent bar](#package-summary-toward-100) | Optional orchestrator |

**Legend:** **Start** = meaningful implementation work toward that package’s [plan](#plans-by-package) and [1.x roadmap](#scaffold-packages-1x-phase-plan). **—** = no dedicated phase milestone for that package (it still gets the same version bump). **Target** = stretch goal for a first “usable” scaffold in that window; may slip with roadmap edits. **Placeholder** = installable stub on PyPI, no user-facing pipeline yet.

---

## Plans by package

The numbered phases below (**0.2**–**0.9**) are **monorepo-wide** for **velarium** and **velotype**. **viperis**, **morphra**, **granitus**, and **velocus** follow **[1.x phases](#scaffold-packages-1x-phase-plan)** after core **1.0.0** (with groundwork during **0.2+** as in [Release alignment](#release-alignment-by-phase-and-package)).

### velarium (core IR)

**Owns:** `ModelSpec` / `TypeSpec` schema, JSON codec, normalization, annotation builders shared by every backend.

- **0.2–0.3:** IR fidelity and richer model sources (see phases below); schema and docs updated in lockstep.
- **0.6–0.8:** Performance hooks, optional acceleration **without** semantic drift; IR versioning and public API freeze.
- **Exit:** IR JSON and Python API meet [What “1.0.0” means](#what-100-means) for the core.

### velotype (stubs + CLI)

**Owns:** `.pyi` generation, `generate_pyi` / `render_typespec`, **`velotype`** CLI (`ir`, `stub`, **`batch`**, optional **`watch`**).

- **0.2–0.5:** Directly tracked by phases **0.2** (fidelity), **0.4** (stub quality), **0.5** (batch/pre-commit/workflows) — see [tutorial-stubs.md](tutorial-stubs.md).
- **0.6–0.7:** Performance and security story for stub pipelines and CLI (see phases **0.6**, **0.7**).
- **Exit:** Checker-usable stubs and documented CLI threat model toward **1.0.0**.

### viperis (Python → IR)

**Goal:** Parse Python **source** (AST) into the same **ModelSpec IR** that `velarium` uses. Groundwork can track **0.2+** IR fidelity; **product** milestones are **[Phases 1.1–1.3](#viperis--1x-roadmap)** (first “usable” slice ≈ **Phase 1.1** exit column).

### morphra (IR → Pydantic)

**Goal:** Emit **Pydantic v2** from `ModelSpec`. **velarium** **0.3** metadata helps; optional **`velotype`** cross-check for `.pyi` vs models. Roadmap: **[Phases 1.1–1.3](#morphra--1x-roadmap)**.

### granitus (IR → Spark-like schemas)

**Goal:** Emit pipeline schemas from `ModelSpec`; coordinate with **morphra** on shared conventions. Roadmap: **[Phases 1.1–1.3](#granitus--1x-roadmap)**.

### velocus (umbrella CLI)

**Goal:** One **Typer** CLI over **`velotype`** + backends ([valarium.md](valarium.md)). Roadmap: **[Phases 1.1–1.3](#velocus--1x-roadmap)**; **Phase 1.1** matches the historical “two backends” bar.

---

## Phase 0.1.* — Foundation *(completed 0.1.0)*

**Theme:** End-to-end path from Python models to IR JSON and minimal stubs.

**Reference implementation (shipped in 0.1.0):**

| Area | Status |
|------|--------|
| IR types | `ModelSpec`, `TypeSpec`, `TypeKind`, `ModelConfig`, `FieldSpec`, `ModelMetadata` in `velarium.ir` (also re-exported as `velotype.ir`) |
| Serialization | `dumps_model_spec` / `loads_model_spec`, dict helpers |
| Normalization | Union flatten/dedupe, optional encoding in `velarium.normalize` (also `velotype.normalize`) |
| Builders | `modelspec_from_dataclass`, `modelspec_from_typed_dict` |
| Annotations | `type_to_typespec`, `annotation_to_typespec` (MVP coverage) |
| Stubs | `generate_pyi`, `render_typespec` (dataclass-oriented) |
| CLI | Typer: `velotype ir`, `velotype stub`; `python -m velotype` |
| Docs | `docs/design.md`, `docs/modelspec-ir.md`, README |

**Refinements that closed 0.1.*:**

- [x] Version from `velotype.__version__` / `velarium.__version__` via Hatch per package; aligned with distribution metadata.
- [x] **CI** on GitHub Actions: Python 3.10–3.13, `pytest`, `ty check`, `python -m build`.
- [x] **[CHANGELOG.md](../CHANGELOG.md)** (Keep a Changelog).
- [x] Optional **PyPI publish** workflow on GitHub Release; manual **twine** documented in [RELEASING.md](RELEASING.md).

**Exit criteria (0.1 complete):**

- [x] Installable artifact from PyPI *or* documented install from Git with reproducible `python -m build` ([RELEASING.md](RELEASING.md)).
- [x] Green CI on the supported Python line with tests + `ty` on **velarium** / **velotype** sources.
- [x] Roadmap, IR spec, and changelog linked from README; [modelspec_ir.md](../modelspec_ir.md) pointer retained.

---

## Phase 0.2.* — Type surface and IR fidelity *(completed — shipped in **0.2.0**)*

**Theme:** Reduce `any` noise; make annotation → IR behavior **predictable and testable**.

**Deliverables:**

- **Forward references:** Consistent resolution with `get_type_hints` and module namespaces; document behavior for unresolvable refs.
- **`from __future__ import annotations`:** String annotations handled uniformly across builders.
- **`typing` coverage:** `Protocol`, `TypedDict` (required/optional keys), nested `Literal`, `Annotated` (strip or preserve per policy), `Final`, `ClassVar` where they affect field typing.
- **Type variables:** Represent `TypeVar`, `ParamSpec`, `TypeVarTuple` in IR with documented lossy cases.
- **Nominal types:** Policy for user-defined classes (e.g. qualified name string vs `GENERIC` vs `ANY`) documented in `modelspec-ir.md`.
- **Golden tests:** Curated `annotation → JSON IR` fixtures in `tests/` (or `tests/fixtures/`).

**Risks:**

- Explosion of edge cases; mitigate with a **support matrix** and explicit “not yet” list.

**Exit criteria:**

- [x] `docs/` page or section: **supported annotations** table + known gaps ([supported-annotations.md](supported-annotations.md)).
- [x] No silent behavior change without a test or changelog note for IR output (integration + golden tests in `tests/`).

---

## Phase 0.3.* — Model sources *(completed — shipped in **0.3.0**)*

**Theme:** Same IR from more than `@dataclass` / `TypedDict`.

**Deliverables:**

- **Pydantic v2:** `modelspec_from_pydantic_model` — fields, defaults; `model_config` partially mapped (`frozen`, `extra`); constraints are lossy (see [model-sources.md](model-sources.md)).
- **Optional extras:** `pip install velarium[pydantic]`, `velarium[attrs]`, or `velarium[sources]` (both).
- **Unified metadata:** `metadata_for_class` / `ModelMetadata` (module, file, line where feasible).
- **Conflict policy:** Documented in [model-sources.md](model-sources.md) (annotations vs runtime defaults).

**Exit criteria:**

- [x] At least **one** non-dataclass source is **tier-1** (tested in default CI job).
- [x] User-facing doc: how to choose a builder and limitations per source.

---

## Phase 0.4.* — Stub generation quality *(completed — shipped in **0.4.0**)*

**Theme:** `.pyi` output is **reviewable** and **checker-usable**, not only syntactically valid.

**Deliverables:**

- **Import graph:** Emit correct `from … import` / `import` lines; avoid circular import traps in generated stubs.
- **Module layout:** `__all__`, module docstring, optional per-package style presets.
- **Validation:** Run **mypy** and **Pyright** on generated stubs against a **fixture corpus** (mini-packages in-repo).
- **Formatting:** Optional post-pass via **ruff format** or **black** (configurable).
- **`generate_pyi` API:** Parameters for style, header/footer hooks, or template overrides.

**Exit criteria:**

- [x] Documented **stub compatibility checklist** (what we guarantee vs best-effort).
- [x] CI job that fails if fixture stubs regress under pinned checker versions.

---

## Phase 0.5.* — Tooling and integrations *(completed — shipped in **0.5.0**)*

**Theme:** velotype fits **repos** and **pipelines**, not only one-off CLI invocations.

**Deliverables:**

- **Batch API:** Walk packages/modules, emit many stubs or one merged artifact; configurable discovery (exclude tests, etc.).
- **Pre-commit:** Official hook config or `pre-commit` mirror repo entry.
- **Watch mode** (optional): filesystem watcher for dev iteration.
- **Errors:** Structured errors with module/class context; exit codes documented.
- **Interchange:** Experimental **JSON Schema** export for `ModelSpec` *or* documented alternative for non-Python consumers (may stay optional/experimental until post-1.0 if scope threatens stability).

**Exit criteria:**

- [x] “From clone to generated stubs” **tutorial** in docs (copy-paste friendly) — [tutorial-stubs.md](tutorial-stubs.md).
- [x] Issue template or **troubleshooting** section for common CLI failures — [troubleshooting-cli.md](troubleshooting-cli.md), [.github/ISSUE_TEMPLATE/cli_failure.md](../.github/ISSUE_TEMPLATE/cli_failure.md).

**Reference implementation (0.5.0):**

- **Library:** `velotype.batch` — `discover_dataclass_targets`, `emit_batch_stubs`, `emit_batch_ir`, `path_matches_excludes`.
- **CLI:** `velotype batch stub`, `velotype batch ir`, `velotype watch stub` (requires **`velotype[watch]`**); exit codes in [troubleshooting-cli.md](troubleshooting-cli.md).
- **Pre-commit:** [`.pre-commit-hooks.yaml`](../.pre-commit-hooks.yaml) (copy into your `.pre-commit-config.yaml`).
- **Interchange:** [interchange-ir-json.md](interchange-ir-json.md) (JSON via `dumps_model_spec`; full JSON Schema deferred).

---

## Phase 0.6.* — Performance and scale *(completed — shipped in **0.6.0**)*

**Theme:** Usable on **large** codebases without unacceptable memory or time.

**Deliverables:**

- **Profiling:** Identify hotspots (normalization, JSON, stub string build).
- **Pure Python wins:** Caching, lazy resolution, fewer intermediate copies where safe.
- **Optional native backend:** Same JSON golden tests; feature flag to enable accelerated normalization (e.g. Rust extension). **No semantic drift.**
- **Incremental mode:** Cache IR keyed by file hash + **velarium** / **velotype** versions + relevant config.

**Exit criteria:**

- [x] Doc section: **performance expectations** and when to enable native backend — [performance.md](performance.md).
- [x] Benchmark script or CI optional job (not necessarily blocking PRs) to catch regressions — `scripts/benchmark_velotype_batch.py`, `scripts/profile_velotype_batch.py`, [`.github/workflows/benchmark.yml`](../.github/workflows/benchmark.yml) (`workflow_dispatch`).

**Reference implementation (0.6.0):**

- **Library:** `velarium.json_codec.typespec_dedupe_key` — stable union dedupe keys; `VELARIUM_NORMALIZE_BACKEND` (`python` default, `native` attempts `velarium._native.normalize_typespec`, falls back to Python).
- **Library:** `velotype.batch.emit_batch_stubs` / `emit_batch_ir` — optional `cache_dir`, `use_cache`, `stub_style` (batch stubs use `minimal` by default).
- **CLI:** `velotype batch stub` / `batch ir` — `--cache-dir`, `--no-cache`.
- **Scripts:** `scripts/profile_velotype_batch.py` (cProfile), `scripts/benchmark_velotype_batch.py` (cold vs cached).
- **Native wheel:** deferred to a future **0.6.x** (hook + tests land in **0.6.0**).

---

## Phase 0.7.* — Hardening

**Theme:** Security, robustness, and abuse resistance.

**Deliverables:**

- **Fuzzing / property tests:** JSON round-trip, normalization idempotence where applicable.
- **CLI threat model:** Document what `velotype ir` / `velotype stub` load and execute; minimize `eval`; sandbox recommendations for untrusted code **never** assumed safe.
- **Resource limits:** Optional caps on input size / recursion for hostile inputs.
- **Bug triage:** No open **critical** crashes or security issues on the 1.0 milestone.

**Exit criteria:**

- [ ] `docs/security.md` or equivalent section in README.
- [ ] Fuzz/property tests in CI or documented manual cadence.

---

## Phase 0.8.* — API and IR stability prep

**Theme:** Everything public is **named**, **documented**, and **versioned**.

**Deliverables:**

- **Public API audit:** Final `__all__` and “public module” list; hide or underscore internal helpers.
- **IR versioning:** explicit `model_spec` / IR version field in JSON *or* parallel `model_spec_v2` export—pick one strategy and document migration (owned by **`velarium`** contract).
- **Deprecations:** `warnings.warn` with `DeprecationWarning` and docstrings for anything removed before 1.0.
- **Migration guide:** From early 0.x snapshots to current IR JSON.

**Exit criteria:**

- [ ] “**API reference**” (Sphinx, mkdocs, or hand-maintained) for public symbols.
- [ ] Commitment text: only **additive** minors or **deprecation** paths until 1.0 after this phase starts.

---

## Phase 0.9.* — Release candidate

**Theme:** **1.0.0** is a tag, not a surprise.

**Deliverables:**

- **Changelog** complete from 0.1 through 0.9.
- **RC releases** on PyPI (`0.9.0rc1`, etc.) if needed; no breaking API/IR changes without bumping RC or documenting exception.
- **Feedback window:** README section for RC feedback (issues/discussions).
- **Third-party smoke:** Optional downstream project checks (manual or nightly).

**Exit criteria:**

- [ ] Maintainers agree: **no P0/P1** blockers; matrix and docs ready.
- [ ] **1.0.0** release notes drafted (highlights + breaking vs stable areas).

---

## 1.0.0 — Stable release

**Theme:** Durable baseline for libraries and internal tools.

**Deliverables:**

- Git tag **v1.0.0**, PyPI **1.0.0**.
- Stability statement (pointer back to [What “1.0.0” means](#what-100-means)).
- **Support policy:** Which Python versions receive patch fixes for the 1.0 line.

**After 1.0.0**

- Features ship as **1.y.0** minors; fixes as **1.0.z** patches.
- **2.0.0** only for intentional breaking API **or** incompatible IR revision with migration path.

---

## Scaffold packages: 1.x phase plan

**Scope:** **viperis**, **morphra**, **granitus**, and **velocus** only. **velarium** and **velotype** follow **[0.1–0.9](#phase-dependency-overview)** and **[1.0.0](#100--stable-release)**; their post-1.0 work is ordinary **1.y.0** semver, not broken out as named “1.x phases” here.

**Versioning:** **Phase 1.1**, **1.2**, **1.3** are **maturity milestones** per package. The monorepo still ships **one version** on every tag ([RELEASING.md](RELEASING.md)); a phase may complete in a **patch** or land alongside unrelated package bumps—changelog and per-package READMEs record what finished.

**Cross-dependencies**

| When | Blocker or prerequisite |
|------|-------------------------|
| **viperis 1.1** | **velarium** IR contract stable enough to promise golden tests (target: **[1.0.0](#what-100-means)**). |
| **morphra 1.1** / **granitus 1.1** | **velarium** **1.0.0**; shared emit conventions where both touch the same `TypeSpec` shapes. |
| **velocus 1.1** | **velotype** at **1.0**-quality stubs/CLI; at least **viperis** or **morphra** at **1.1**. |

### viperis — 1.x roadmap

**Role:** Python **source** (AST) → **ModelSpec** IR, beyond `velarium`’s live-class builders.

| Phase | Theme | Deliverables | Exit criteria |
|-------|--------|--------------|---------------|
| **1.1** | MVP | Discover modules/classes from files; map AST types to `TypeSpec` for common typing; golden `*.py` → IR JSON; documented public API or CLI entry | At least one **non-dataclass** path in default CI; doc: **viperis** vs **`velarium`** builders |
| **1.2** | Parity | Package layouts and import paths; shrink gaps vs `annotation_to_typespec`; configurable roots/excludes | Support matrix + regression tests for listed constructs |
| **1.3** | Scale + safety | Optional incremental/cache; structured diagnostics; threat model for imports/exec ([valarium.md](valarium.md)) | Performance expectations doc; security section cross-linked |

### morphra — 1.x roadmap

**Role:** **ModelSpec** → **Pydantic v2** models / codegen for runtime validation.

| Phase | Theme | Deliverables | Exit criteria |
|-------|--------|--------------|---------------|
| **1.1** | MVP | `ModelSpec` → `BaseModel` (or documented codegen) for primitives + nested models; tests in default CI | One **tier-1** path documented; user-facing limitations vs hand-written Pydantic |
| **1.2** | Expressiveness | Map IR constraints to `Field()` where possible; `model_config` hooks; lossy cases explicit in docs | Golden snapshots or round-trip **IR → morphra → IR** where feasible |
| **1.3** | Ergonomics | Import layout, `__all__`, optional multi-file output; optional cross-check with **`velotype`**-generated `.pyi` | Stable public API for emit; changelog semver notes |

### granitus — 1.x roadmap

**Role:** **ModelSpec** → **Spark**-like (or documented) schemas for pipelines.

| Phase | Theme | Deliverables | Exit criteria |
|-------|--------|--------------|---------------|
| **1.1** | MVP | `schema_from_model_spec` (name TBD); primitives + struct + list in CI fixtures | Documented **support matrix** (format and/or Spark version) |
| **1.2** | Real-world shapes | Policy for unions, optionals, nested structs; explicit fallbacks for unsupported `TypeKind`s | Expanded corpus; no silent widening |
| **1.3** | Interop | Optional alternate emit (e.g. JSON Schema for columns); pipeline docs | Versioned schema output if format evolves |

### velocus — 1.x roadmap

**Role:** Single **Typer** CLI over **`velarium`** + backends—no forked IR ([valarium.md](valarium.md)).

| Phase | Theme | Deliverables | Exit criteria |
|-------|--------|--------------|---------------|
| **1.1** | MVP | Subcommands delegating to **`velotype`** and one of **viperis** / **morphra**; `--help` parity with scope statement | **Two** backends behind **velocus**; README vs **`velotype`** alone |
| **1.2** | Workflow | Shared config file (optional); consistent exit codes and errors across backends | Troubleshooting doc; pre-commit / CI recipe (optional) |
| **1.3** | Full stack | **granitus** (and **viperis** if not already) behind subcommands; threat model inherits **`velotype`** | All planned backends reachable; enterprise-facing doc |

---

## Cross-cutting work (all phases)

| Track | Ongoing expectations |
|-------|----------------------|
| **Tests** | Increase coverage on new code paths; regression tests for every fixed IR/stub bug. |
| **Docs** | Update `modelspec-ir.md` when IR meaning changes; link new user-facing features from the root [README](../README.md) and [docs/README](README.md). Per-package READMEs should reflect status vs [Plans by package](#plans-by-package) and, for scaffolds, [Scaffold packages: 1.x phase plan](#scaffold-packages-1x-phase-plan). |
| **Dependencies** | Conservative bounds; security updates for Typer, typing_extensions, etc. |
| **Contributing** | `CONTRIBUTING.md` when external contributors appear: code style, PR checklist, CoC optional. |

---

## How to change this roadmap

- Propose edits via PR; significant scope changes should update **phase exit criteria** and **dependency overview** (both **0.x** and **scaffold 1.x** tables).
- **Slipping** work to a later phase is normal; **removing** exit criteria without maintainer agreement is not.
- When a phase’s exit criteria are met, tag a **minor** release and note it in CHANGELOG; record **scaffold 1.x** completions in changelog/README when they land.

---

## Package summary (toward 1.0.0)

| Package | What “ready for the 1.0 era” implies |
|---------|----------------------------------------|
| **velarium** | IR + JSON semantics and Python API match Phase **0.8** freeze; [What “1.0.0” means](#what-100-means) applies to core types. |
| **velotype** | Stub + CLI quality and security commitments from Phases **0.4**–**0.7**; published as **1.x** in step with or shortly after **velarium** 1.0. |
| **viperis** | **[Phase 1.1](#viperis--1x-roadmap)** exit criteria met (Python → IR docs + CI); does not block **velarium** / **velotype** 1.0 but must not contradict the IR spec. |
| **morphra** | **[Phase 1.1](#morphra--1x-roadmap)** exit criteria (supported IR → Pydantic path); semver independent unless re-exporting **velarium** APIs. |
| **granitus** | **[Phase 1.1](#granitus--1x-roadmap)** exit criteria (supported schema path + matrix); same independence note as **morphra**. |
| **velocus** | Optional for ecosystem **1.0**; **[Phase 1.1](#velocus--1x-roadmap)** when orchestration ships—thin layer over **velotype** and backends (no forked IR). |

---

## Summary table

Phase themes for the repo as a whole; **which packages move in each 0.x phase** is in [Release alignment by phase and package](#release-alignment-by-phase-and-package). **viperis**, **morphra**, **granitus**, and **velocus** use **[1.1–1.3 milestones](#scaffold-packages-1x-phase-plan)** after core **1.0.0**.

| Phase | Focus | Main outcome |
|-------|--------|----------------|
| **0.1** | Foundation | IR + JSON + dataclass/TypedDict + CLI + CI + PyPI path |
| **0.2** | Fidelity | Annotation coverage + golden IR tests + support matrix |
| **0.3** | Sources | Pydantic (+ optional attrs/msgspec) |
| **0.4** | Stubs | Checker-validated `.pyi`, import/style quality |
| **0.5** | Tooling | Batch / watch CLI, pre-commit hook, tutorials *(shipped **0.5.0**)* |
| **0.6** | Performance | Profiling, cache, native hook *(shipped **0.6.0**)*; optional native wheel **0.6.x** |
| **0.7** | Hardening | Security doc, fuzzing, resource limits |
| **0.8** | Freeze | Public API + IR version + migration guide |
| **0.9** | RC | Changelog, feedback, no blockers |
| **1.0** | Stable | Semver + long-lived 1.0 line |
