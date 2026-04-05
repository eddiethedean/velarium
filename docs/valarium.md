# Velarium ecosystem design

## Overview

The **Velarium** ecosystem is a modular, compiler-inspired Python type transformation system. It unifies type representation, inference, and code generation across multiple backends through a stable intermediate representation (**ModelSpec IR**, implemented in the **`velarium`** package).

The intended pipeline:

```text
Python source → Viperis → Velarium IR → Backend generators → Outputs
```

An umbrella CLI (**Clarion**) will orchestrate the ecosystem; today **`stubber`** provides the supported CLI for IR export and stub generation.

---

## Core philosophy

1. **Stable intermediate representation** — All transformations depend on a shared IR that acts as the single source of truth.
2. **Unidirectional compilation flow** — Source moves forward through the system; each stage is deterministic and does not mutate upstream representations.
3. **Backend pluggability** — Multiple independent backends consume the IR (stubs, Pydantic models, Spark schemas, …).

---

## System components

### 1. `velarium` (core IR)

**Role:** The **Velarium** representation as concrete Python types and JSON — the truth layer.

**Responsibilities:**

- Represent Python types in a normalized graph (`TypeSpec`, `ModelSpec`, …).
- Encode primitives, unions, generics, structs, and constraints.
- Provide a language-agnostic schema for downstream tools.

**Characteristics:** Minimal dependencies (`typing_extensions`), immutable data shapes, JSON-serializable design.

**Monorepo:** [`packages/velarium`](../packages/velarium/README.md) · PyPI: **`velarium`**

---

### 2. `viperis` (Python → IR)

**Role:** Transform Python **source** into Velarium IR (the main **frontend** parser).

**Responsibilities:** Parse AST, extract type hints and structure, resolve local definitions where possible, emit IR.

**Input:** Python files. **Output:** Velarium IR.

**Status:** Scaffold — builders today live in **`velarium`** (e.g. dataclass → IR); **viperis** will generalize source-level ingestion.

**Monorepo:** [`packages/viperis`](../packages/viperis/README.md) · PyPI: **`viperis`** (placeholder releases as needed)

---

### 3. `stubber` (IR → `.pyi`)

**Role:** Generate Python stub files from Velarium IR.

**Responsibilities:** Render IR as `.pyi` syntax, preserve type fidelity where possible, emit minimal stubs.

**Output:** `.pyi` files. **CLI:** `stubber ir`, `stubber stub`.

**Monorepo:** [`packages/stubber`](../packages/stubber/README.md) · PyPI: **`stubber`** · depends on **`velarium`**

---

### 4. `morphra` (IR → Pydantic)

**Role:** Transform Velarium IR into Pydantic models (generated code or runtime objects).

**Use cases:** FastAPI, validation layers.

**Status:** Scaffold.

**Monorepo:** [`packages/morphra`](../packages/morphra/README.md)

---

### 5. `granitus` (IR → Spark-like schemas)

**Role:** Generate distributed / columnar schemas (Spark-like) from IR.

**Use cases:** Big data pipelines, ETL.

**Status:** Scaffold.

**Monorepo:** [`packages/granitus`](../packages/granitus/README.md)

---

### 6. `clarion` (ecosystem CLI)

**Role:** User-facing CLI that dispatches to ecosystem modules (inspect, build, emit backends).

**Example commands (target):**

```text
clarion inspect file.py
clarion build
clarion emit pydantic User
clarion graph module.py
```

**Status:** Scaffold — use **`stubber`** for IR and stub commands until **clarion** ships.

**Monorepo:** [`packages/clarion`](../packages/clarion/README.md)

---

## Architecture

### Primary pipeline

```text
Python Source
    ↓
 Viperis (planned)
    ↓
 Velarium IR  ← implemented in package `velarium`
    ↓
┌──────────────┬──────────────┬──────────────┐
│ stubber      │ morphra      │ granitus     │
│ (.pyi)       │ (Pydantic)   │ (Spark)      │
└──────────────┴──────────────┴──────────────┘
```

### CLI (target)

```text
User → Clarion → ecosystem APIs → backends → output
```

Today: **User → `stubber` CLI → velarium + stubber**.

---

## Data flow

1. **Parsing** — Viperis (future) turns Python into IR nodes; today, **velarium** builders do the same from live classes.
2. **Normalization** — IR conforms to a unified schema (`velarium.normalize`).
3. **Transformation** — Backends consume IR without redefining core types.
4. **Emission** — Each backend produces its own artifact format.

---

## Design constraints

**Velarium IR must:** be backend-agnostic; avoid unnecessary runtime dependencies; remain stable across versions; support serialization.

**Backend tools must:** not mutate the IR **definition**; only consume and transform; stay independently versionable on PyPI.

**Clarion (when implemented) must:** stay thin — orchestration only, no duplicated business logic.

---

## Extensibility

New backends can be added without changing **`velarium`**’s core types.

Examples: SQL schemas, Rust types, GraphQL, OpenAPI.

Pattern: **Velarium IR → new backend → output**.

---

## Long-term vision

A **universal intermediate representation** for Python types and downstream schema generators — enabling cross-tool consistency, multi-runtime codegen, and unified type reasoning.

---

## Package summary

| Package   | Role |
|-----------|------|
| **velarium** | Core IR (truth layer) |
| **viperis**  | Python → IR |
| **stubber**  | IR → stubs + current CLI |
| **morphra**  | IR → Pydantic |
| **granitus** | IR → Spark-like schemas |
| **clarion**  | Ecosystem CLI (planned) |

---

## Repository layout (this monorepo)

The Git repository is a **[uv](https://docs.astral.sh/uv/) workspace** (see root [`pyproject.toml`](../pyproject.toml) and [README](../README.md)). Installable packages live under **`packages/`**:

| Directory | PyPI name | Status |
|-----------|-----------|--------|
| `packages/velarium` | `velarium` | **Core IR** — JSON, normalization, dataclass/TypedDict builders |
| `packages/stubber` | `stubber` | **IR → `.pyi`** — `stubber` CLI (`ir`, `stub`) |
| `packages/viperis` | `viperis` | Scaffold — Python → IR |
| `packages/morphra` | `morphra` | Scaffold — IR → Pydantic |
| `packages/granitus` | `granitus` | Scaffold — IR → Spark-like schemas |
| `packages/clarion` | `clarion` | Scaffold — umbrella CLI (use **`stubber`** until implemented) |

See also [Installing & releasing](releasing.md) and [Design & philosophy](design.md).
