# Velarium: design intent and philosophy

**Velarium** is a **compiler-inspired ecosystem** for Python types: a shared **ModelSpec IR** (the “Velarium” representation), small focused **packages** under one repository, and pluggable **backends** that turn that IR into stubs, schemas, and other artifacts.

This document explains **why** that IR exists and how we think about typing tooling—not as “another type checker,” but as a **thin compilation layer** between annotations and portable outputs.

For the concrete schema (`ModelSpec`, `TypeSpec`, `TypeKind`, …), see [ModelSpec IR](modelspec-ir.md). For package roles and the target pipeline, see [Velarium ecosystem spec](valarium.md).

---

## 1. Ecosystem at a glance

| Piece | PyPI / import | Role today |
|-------|----------------|------------|
| **velarium** | `velarium` | Core IR: types, normalization, JSON codec, builders (e.g. dataclass → `ModelSpec`) |
| **velotype** | `velotype` | Backend: IR → `.pyi`; ships the **`velotype`** CLI (`ir`, `stub`). Depends on **velarium**. |
| **viperis** | `viperis` | Planned frontend: Python source → IR (scaffold) |
| **morphra** | `morphra` | Planned backend: IR → Pydantic (scaffold) |
| **granitus** | `granitus` | Planned backend: IR → Spark-like schemas (scaffold) |
| **velocus** | `velocus` | Planned umbrella CLI (scaffold); **`velotype`** is the supported CLI until then |

The **`velotype`** package **re-exports** most IR symbols for backward compatibility; new code may import from **`velarium`** directly.

---

## 2. The core problem

Python’s typing ecosystem is powerful but fragmented:

- **mypy** enforces one plugin-heavy interpretation of types.
- **Pyright** uses a different inference model and semantics.
- **Pydantic** and similar runtimes add another interpretation at execution time.
- **IDEs** often add yet another partial model.

The same source can **behave differently** depending on which tool is active. That creates friction for library authors (hard to target every checker), for application teams (weaker trust in static guarantees), and for advanced features (they become checker-specific hacks instead of portable abstractions).

---

## 3. What Velarium is not

Velarium is **not** a replacement for mypy or Pyright.

It is a **portable IR and compilation layer**: normalize annotations into **ModelSpec**, then transform that IR deterministically into artifacts such as **`.pyi` stubs**, JSON for tooling, or (eventually) Pydantic models and Spark schemas.

Goals:

- Express types in **one canonical model** that multiple consumers can agree on.
- Emit **checker-friendly** stubs where possible (outputs should work with common checkers without per-checker forks in the IR).
- Keep room for **non-Python backends** (e.g. high-performance IR passes) **without** changing the IR’s public meaning.
- Evolve the IR **safely** behind explicit versioning and normalization rules.

The **velarium** package implements that IR in Python; **velotype** is one **backend** on top of it.

---

## 4. The central idea: ModelSpec IR

At the center is the **ModelSpec intermediate representation**: a **loss-minimized** abstraction between:

- Python source and annotations,
- static analysis and IDEs,
- runtime validation systems,
- and future compiled or accelerated backends.

Instead of asking every tool to re-parse Python the same way, compatible producers target **one structure**:

> If we agree on this IR, everything else becomes a transformation problem.

See [modelspec-ir.md](modelspec-ir.md) for the full datatype layout.

---

## 5. Why an intermediate representation matters

Many typing tools fail because they work **directly on syntax** without a **normalized semantic model**. That encourages:

- Inconsistent treatment of `Union`, `Optional`, and generics,
- Ambiguous or tool-specific “dynamic” behavior,
- Non-portable plugin extensions.

ModelSpec addresses this with an explicit **contract**:

- Every field type is a normalized **`TypeSpec`**.
- Every model is a deterministic **`ModelSpec`**.
- Provenance lives in **`ModelMetadata`**.

Typing becomes a **graph transformation** problem (normalize → analyze → emit), not a pile of ad hoc special cases per tool.

---

## 6. “Compiler thinking in Python”

Velarium borrows from compiler architecture:

| Compiler idea   | Velarium angle |
|-----------------|----------------|
| AST / surface   | Python source and annotations (today: builders; future: **viperis**) |
| IR              | **ModelSpec** + **TypeSpec** ( **`velarium`** ) |
| Backends        | **velotype** (`.pyi`), future **morphra**, **granitus**, JSON, etc. |
| Passes          | Normalization, optional encoding, inference hooks |

The design is **IR-first**, not decorator-first or runtime-first. The point is not to “decorate Python,” but to **compile typing intent into a stable intermediate form** that downstream tools can share.

---

## 7. Why not only Pydantic or only mypy?

**Pydantic** excels at runtime validation but is tied to execution semantics and is not primarily a cross-checker contract for static tools.

**mypy / Pyright** excel at checking but do not expose a **stable, reusable IR** for codegen pipelines.

Velarium’s role is **above** both in the stack: it does not replace them—it **coordinates** them through a **shared representation** when you need portable IR and generated artifacts. **velotype** and future backends sit **around** the IR—not inside the type checkers.

---

## 8. Performance and other languages

The IR is defined so that **hot paths** could eventually be implemented in a faster language (e.g. Rust), following patterns seen in tools like **Polars** or **Ruff**: Python for ergonomics, native code for throughput.

Architectural rule: **alternative backends must not change the IR’s meaning**—only how fast or where it is computed. The Python API and JSON shape stay stable.

---

## 9. Why the IR is strictly structured

ModelSpec is **opinionated** on purpose:

- **`TypeSpec`** is normalized; duplicate surface forms collapse to one shape.
- **Unions** are explicit nodes.
- **Optional** is encoded structurally (see [modelspec-ir.md](modelspec-ir.md)).
- Primitives and containers are **canonicalized** where possible.

That avoids a common failure mode: **ambiguity pretending to be flexibility**. Early normalization makes the IR easier to compare, cache, test, and lower to other languages.

---

## 10. Dynamic behavior is represented, not erased

Python is dynamic. The IR acknowledges that:

- **`TypeKind.ANY`** exists as an honest fallback.
- Unions are explicit.
- Defaults and similar metadata can ride on **`TypeSpec`** / model metadata where needed.

The aim is not to pretend Python is a different language, but to capture **intent** in a structured way.

---

## 11. CLI and developer experience

Today, the **`velotype`** CLI is intentionally **thin** and built with **Typer**: commands call into **velarium** + **velotype** library code. A future **velocus** CLI would orchestrate multiple backends without duplicating IR logic—see [valarium.md](valarium.md).

---

## 12. Multi-checker friendliness

A practical constraint for generated stubs and idioms is that they should be **useful under common checkers** (e.g. mypy and Pyright) **without** forked “pyright-only” or “mypy-only” IR variants. That pushes the design toward:

- Strict normalization,
- Avoiding ambiguous constructs at the IR level,
- Preferring portable `.pyi` shapes.

We **normalize in velarium** before downstream tools see the result, instead of encoding checker quirks into the IR.

---

## 13. Long-term vision

ModelSpec (and this monorepo as a reference implementation) can underpin:

- Portable **type compilation** pipelines,
- **Cross-language** representation (e.g. Python ↔ Rust) at the IR boundary,
- Deterministic **stub and schema** generation,
- IDE and CI workflows that share one IR artifact.

Aspirational framing: what the AST is to execution, a stable IR could be to **typing**—a shared substrate for tools that agree on structure first.

---

## 14. Summary

> If we define a solid intermediate representation for Python types, everything else becomes a translation problem.

**ModelSpec** is that representation. The **`velarium`** package implements it in Python; **`velotype`** implements stub emission and the current CLI; other packages will add parsers and backends—see [valarium.md](valarium.md). Checkers, IDEs, and future runtimes sit **around** that core—not inside it.
