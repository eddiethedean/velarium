# Velarium ecosystem design

## Overview

The **Velarium** ecosystem is a modular, compiler-inspired Python type transformation system. It unifies type representation, inference, and code generation across multiple backends through a stable intermediate representation (**ModelSpec IR**, implemented in the **`velarium`** package).

The intended pipeline:

```text
Python source → Viperis → Velarium IR → Backend generators → Outputs
```

An umbrella CLI (**Velocus**) will orchestrate the ecosystem; today **`velotype`** provides the supported CLI for IR export and stub generation.

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
- Map `typing` constructs and class-based builders (dataclass, `TypedDict`, Pydantic v2, attrs with optional extras) to IR with documented behavior; see [Supported annotations](supported-annotations.md) and [Model sources](model-sources.md).

**Characteristics:** Minimal dependencies (`typing_extensions`), immutable data shapes, JSON-serializable design. The in-repo test suite includes integration tests (`tests/test_ir_integration.py`), JSON golden fixtures (`tests/fixtures/ir_golden/`), and **Hypothesis** property tests plus deserialization limit tests (`tests/test_property_json_codec.py`, `tests/test_json_limits.py`) to guard the IR contract and JSON codec behavior (Phases **0.7**–**0.8**, including **`format_version`** on wire JSON).

**Monorepo:** [`packages/velarium`](../packages/velarium/README.md) · PyPI: **`velarium`**

---

### 2. `viperis` (Python → IR)

**Role:** Transform Python **source** into Velarium IR (the main **frontend** parser).

**Responsibilities:** Parse AST, extract type hints and structure, resolve local definitions where possible, emit IR.

**Input:** Python files. **Output:** Velarium IR.

**Status:** Scaffold — class-based builders today live in **`velarium`** (see [Model sources](model-sources.md)); **viperis** will generalize source-level ingestion.

**Monorepo:** [`packages/viperis`](../packages/viperis/README.md) · PyPI: **`viperis`** (placeholder releases as needed)

---

### 3. `velotype` (IR → `.pyi`)

**Role:** Generate Python stub files from Velarium IR.

**Responsibilities:** Render IR as `.pyi` syntax, preserve type fidelity where possible, emit minimal stubs.

**Output:** `.pyi` files. **CLI:** `velotype ir`, `velotype stub`.

**Monorepo:** [`packages/velotype`](../packages/velotype/README.md) · PyPI: **`velotype`** · depends on **`velarium`**

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

### 6. `velocus` (ecosystem CLI)

**Role:** User-facing CLI that dispatches to ecosystem modules (inspect, build, emit backends).

**Example commands (target):**

```text
velocus inspect file.py
velocus build
velocus emit pydantic User
velocus graph module.py
```

**Status:** Scaffold — use **`velotype`** for IR and stub commands until **velocus** ships.

**Monorepo:** [`packages/velocus`](../packages/velocus/README.md)

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
│ velotype      │ morphra      │ granitus     │
│ (.pyi)       │ (Pydantic)   │ (Spark)      │
└──────────────┴──────────────┴──────────────┘
```

### CLI (target)

```text
User → Velocus → ecosystem APIs → backends → output
```

Today: **User → `velotype` CLI → velarium + velotype**.

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

**Velocus (when implemented) must:** stay thin — orchestration only, no duplicated business logic.

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
| **velotype**  | IR → stubs + current CLI |
| **morphra**  | IR → Pydantic |
| **granitus** | IR → Spark-like schemas |
| **velocus**  | Ecosystem CLI (planned) |

---

## Repository layout (this monorepo)

The Git repository is a **[uv](https://docs.astral.sh/uv/) workspace** (see root [`pyproject.toml`](../pyproject.toml) and [README](../README.md)). Installable packages live under **`packages/`**:

| Directory | PyPI name | Status |
|-----------|-----------|--------|
| `packages/velarium` | `velarium` | **Core IR** — JSON, normalization, builders ([Model sources](model-sources.md)) |
| `packages/velotype` | `velotype` | **IR → `.pyi`** — `velotype` CLI (`ir`, `stub`) |
| `packages/viperis` | `viperis` | Scaffold — Python → IR |
| `packages/morphra` | `morphra` | Scaffold — IR → Pydantic |
| `packages/granitus` | `granitus` | Scaffold — IR → Spark-like schemas |
| `packages/velocus` | `velocus` | Scaffold — umbrella CLI (use **`velotype`** until implemented) |

See also [Installing & releasing](RELEASING.md) and [Design & philosophy](design.md).
