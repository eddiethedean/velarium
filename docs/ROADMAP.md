# Roadmap to 1.0.0

This document is the **release plan** for the **Velarium** monorepo (notably **`velarium`** IR and **`velotype`** stubs/CLI): what we ship in each **0.X.*** line, how phases depend on each other, and what **1.0.0** commits to. It complements [design.md](design.md) (why the IR exists) and [modelspec-ir.md](modelspec-ir.md) (schema details).

**Conventions**

| Term | Meaning |
|------|--------|
| **Phase** | A **minor** series **0.X.*** (ongoing work until exit criteria are met). |
| **Patch** | **0.X.Y** — bugfixes, docs, and *small* additive changes that do not change the phase’s scope. |
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
- [x] Optional **PyPI publish** workflow on GitHub Release; manual **twine** documented in [releasing.md](releasing.md).

**Exit criteria (0.1 complete):**

- [x] Installable artifact from PyPI *or* documented install from Git with reproducible `python -m build` ([releasing.md](releasing.md)).
- [x] Green CI on the supported Python line with tests + `ty` on **velarium** / **velotype** sources.
- [x] Roadmap, IR spec, and changelog linked from README; [modelspec_ir.md](../modelspec_ir.md) pointer retained.

---

## Phase 0.2.* — Type surface and IR fidelity

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

- [ ] `docs/` page or section: **supported annotations** table + known gaps.
- [ ] No silent behavior change without a test or changelog note for IR output.

---

## Phase 0.3.* — Model sources

**Theme:** Same IR from more than `@dataclass` / `TypedDict`.

**Deliverables:**

- **Pydantic v2:** `modelspec_from_pydantic_model` (name TBD) — fields, defaults, field constraints mapped into `TypeSpec` / metadata as far as the IR allows.
- **Optional extras:** e.g. `pip install velotype[attrs]` (or an extra on **`velarium`** if IR-only) for **attrs** / **msgspec** with parallel tests.
- **Unified metadata:** `ModelMetadata` populated consistently (module, file, line where feasible).
- **Conflict policy:** If multiple sources disagree, document error vs last-wins behavior.

**Exit criteria:**

- [ ] At least **one** non-dataclass source is **tier-1** (tested in default CI job).
- [ ] User-facing doc: how to choose a builder and limitations per source.

---

## Phase 0.4.* — Stub generation quality

**Theme:** `.pyi` output is **reviewable** and **checker-usable**, not only syntactically valid.

**Deliverables:**

- **Import graph:** Emit correct `from … import` / `import` lines; avoid circular import traps in generated stubs.
- **Module layout:** `__all__`, module docstring, optional per-package style presets.
- **Validation:** Run **mypy** and **Pyright** on generated stubs against a **fixture corpus** (mini-packages in-repo).
- **Formatting:** Optional post-pass via **ruff format** or **black** (configurable).
- **`generate_pyi` API:** Parameters for style, header/footer hooks, or template overrides.

**Exit criteria:**

- [ ] Documented **stub compatibility checklist** (what we guarantee vs best-effort).
- [ ] CI job that fails if fixture stubs regress under pinned checker versions.

---

## Phase 0.5.* — Tooling and integrations

**Theme:** velotype fits **repos** and **pipelines**, not only one-off CLI invocations.

**Deliverables:**

- **Batch API:** Walk packages/modules, emit many stubs or one merged artifact; configurable discovery (exclude tests, etc.).
- **Pre-commit:** Official hook config or `pre-commit` mirror repo entry.
- **Watch mode** (optional): filesystem watcher for dev iteration.
- **Errors:** Structured errors with module/class context; exit codes documented.
- **Interchange:** Experimental **JSON Schema** export for `ModelSpec` *or* documented alternative for non-Python consumers (may stay optional/experimental until post-1.0 if scope threatens stability).

**Exit criteria:**

- [ ] “From clone to generated stubs” **tutorial** in docs (copy-paste friendly).
- [ ] Issue template or **troubleshooting** section for common CLI failures.

---

## Phase 0.6.* — Performance and scale

**Theme:** Usable on **large** codebases without unacceptable memory or time.

**Deliverables:**

- **Profiling:** Identify hotspots (normalization, JSON, stub string build).
- **Pure Python wins:** Caching, lazy resolution, fewer intermediate copies where safe.
- **Optional native backend:** Same JSON golden tests; feature flag to enable accelerated normalization (e.g. Rust extension). **No semantic drift.**
- **Incremental mode:** Cache IR keyed by file hash + **velarium** / **velotype** versions + relevant config.

**Exit criteria:**

- [ ] Doc section: **performance expectations** and when to enable native backend.
- [ ] Benchmark script or CI optional job (not necessarily blocking PRs) to catch regressions.

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

## Cross-cutting work (all phases)

| Track | Ongoing expectations |
|-------|----------------------|
| **Tests** | Increase coverage on new code paths; regression tests for every fixed IR/stub bug. |
| **Docs** | Update `modelspec-ir.md` when IR meaning changes; link new user-facing features from the root [README](../README.md) and [docs/README](README.md). |
| **Dependencies** | Conservative bounds; security updates for Typer, typing_extensions, etc. |
| **Contributing** | `CONTRIBUTING.md` when external contributors appear: code style, PR checklist, CoC optional. |

---

## How to change this roadmap

- Propose edits via PR; significant scope changes should update **phase exit criteria** and **dependency overview**.
- **Slipping** work to a later phase is normal; **removing** exit criteria without maintainer agreement is not.
- When a phase’s exit criteria are met, tag a **minor** release and note it in CHANGELOG.

---

## Summary table

| Phase | Focus | Main outcome |
|-------|--------|----------------|
| **0.1** | Foundation | IR + JSON + dataclass/TypedDict + CLI + CI + PyPI path |
| **0.2** | Fidelity | Annotation coverage + golden IR tests + support matrix |
| **0.3** | Sources | Pydantic (+ optional attrs/msgspec) |
| **0.4** | Stubs | Checker-validated `.pyi`, import/style quality |
| **0.5** | Tooling | Batch, pre-commit, docs for workflows |
| **0.6** | Performance | Profiling, cache, optional native backend |
| **0.7** | Hardening | Security doc, fuzzing, resource limits |
| **0.8** | Freeze | Public API + IR version + migration guide |
| **0.9** | RC | Changelog, feedback, no blockers |
| **1.0** | Stable | Semver + long-lived 1.0 line |
