# ModelSpec IR (intermediate representation)

This document describes the **ModelSpec IR** implemented by the **`velarium`** package (`velarium.ir` and related modules). The same types are also re-exported from **`velotype`** for compatibility (`velotype.ir`, etc.).

For **non-Python interchange**, see [interchange-ir-json.md](interchange-ir-json.md) (JSON as produced by `dumps_model_spec`). For **untrusted JSON** or size limits when loading IR, see [security.md](security.md).

ModelSpec is the **language-agnostic layer** used to normalize Python annotations, serialize typing structure to JSON, and drive backends (notably **velotype** for `.pyi` generation).

## Overview

ModelSpec is the **intermediate representation (IR)** at the heart of the **Velarium** ecosystem.

It is designed to:

- Normalize Python type annotations into a single semantic shape
- Stay **backend-agnostic** (no reliance on a specific type checker or runtime)
- Remain **fully JSON-serializable** for caching, tooling, and future non-Python backends
- **Loss-minimize** information from type hints, dataclass-like models, Pydantic/attrs (optional extras), and (eventually) raw source via **viperis**
- Stay **deterministic**: same logical input produces the same IR

The **`velarium`** Python package maps this spec from dataclasses, `TypedDict`, Pydantic v2, attrs, and related helpers (see [model-sources.md](model-sources.md)); the IR contract itself is not tied to any single package’s layout.

---

## Core design principles

### 1. Backend agnostic

ModelSpec must not depend on a single Python runtime or checker behavior.

### 2. Fully serializable

All structures are intended to be JSON-serializable (with explicit handling for non-JSON field defaults where needed).

### 3. Loss-minimized

Capture as much typing information as practical from:

- Python `typing` annotations
- Dataclass / `TypedDict` (via **`velarium.modelspec_build`**), Pydantic v2 / attrs (via **`velarium.modelspec_pydantic`** / **`velarium.modelspec_attrs`**, optional extras; see [model-sources.md](model-sources.md))
- Future sources (e.g. **viperis** from source files, other ASTs)

### 4. Deterministic

Same normalized input yields the same IR across environments.

---

## Top-level structure

```python
@dataclass
class ModelSpec:
    name: str
    fields: dict[str, TypeSpec]
    config: ModelConfig | None = None
    metadata: ModelMetadata | None = None
```

### JSON wire format (`format_version`)

When serialized with **`dumps_model_spec`** / **`model_spec_to_dict`**, the JSON object includes a top-level integer **`format_version`** equal to **`MODEL_SPEC_FORMAT_VERSION`** in **`velarium.json_codec`**. This is the **wire** version of the object shape (not the Python package version).

- **Missing or `null` `format_version`** on load is treated as **1** (backward compatible with JSON from **0.7.x** and earlier).
- If the field is present, it must be a JSON **integer**; non-integers (including booleans and floats) raise **`ValueError`**.
- **Future** format integers **greater** than the version supported by your installed **`velarium`** are rejected with a clear **`ValueError`** until you upgrade.

See [interchange-ir-json.md](interchange-ir-json.md) and [migration-ir.md](migration-ir.md) for interchange and migration notes.

---

## TypeSpec (core type system)

```python
@dataclass
class TypeSpec:
    kind: TypeKind
    args: list["TypeSpec"] | None = None
    optional: bool = False
    nullable: bool = False
    default: Any | None = None
    # Optional metadata (Phase 0.2): JSON-serializable strings for type vars and nominal refs
    name: str | None = None  # TypeVar / ParamSpec / TypeVarTuple name
    qualname: str | None = None  # class or Protocol
    module: str | None = None  # declaring module
```

See [supported-annotations.md](supported-annotations.md) for how Python typing maps onto these fields.

---

## TypeKind

Normalized discriminant for Python types (string enum in the wire format).

```python
class TypeKind(str, Enum):
    # Primitives
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    STR = "str"
    BYTES = "bytes"

    # Complex
    LIST = "list"
    TUPLE = "tuple"
    DICT = "dict"
    SET = "set"

    # Special
    UNION = "union"
    LITERAL = "literal"
    ENUM = "enum"
    ANY = "any"
    NONE = "none"

    # Temporal
    DATETIME = "datetime"
    DATE = "date"
    TIME = "time"
    TIMESTAMP = "timestamp"

    # Advanced
    GENERIC = "generic"
    CALLABLE = "callable"
    TYPE_VAR = "typevar"
    PARAM_SPEC = "paramspec"
    TYPE_VAR_TUPLE = "typevartuple"
    PROTOCOL = "protocol"
    NOMINAL = "nominal"
```

---

## ModelConfig

Optional model-level behavior (Pydantic-like ergonomics when applicable).

```python
@dataclass
class ModelConfig:
    frozen: bool = False
    extra: Literal["allow", "forbid", "ignore"] = "forbid"
    validate_assignment: bool = True
    from_attributes: bool = True
    strict: bool = False
```

---

## FieldSpec (expanded form)

Richer per-field view for internal transforms and future tooling.

```python
@dataclass
class FieldSpec:
    name: str
    type: TypeSpec
    required: bool
    default: Any | None = None
    alias: str | None = None
    description: str | None = None
    deprecated: bool = False
```

---

## ModelMetadata

Provenance and generator hints.

```python
@dataclass
class ModelMetadata:
    source_module: str | None = None
    source_file: str | None = None
    line_number: int | None = None
    generated_by: str = "velarium"
    version: str | None = None
```

---

## Union representation

Unions are explicit `TypeSpec` nodes:

```python
TypeSpec(
    kind=TypeKind.UNION,
    args=[TypeSpec(...), TypeSpec(...)],
)
```

Normalization rules (see `velarium.normalize`, also exposed as `velotype.normalize`):

- Flatten nested unions
- Remove duplicate members (by structure)
- Preserve order of first appearance

---

## Optional handling

`Optional[T]` is represented as a union that includes `none`, with `optional=True` on the `TypeSpec`:

```python
TypeSpec(
    kind=TypeKind.UNION,
    args=[T, TypeSpec(kind=TypeKind.NONE)],
    optional=True,
)
```

---

## Generic types

Example: `list[int]`

```python
TypeSpec(
    kind=TypeKind.LIST,
    args=[TypeSpec(kind=TypeKind.INT)],
)
```

---

## Dict types

Example: `dict[str, int]`

```python
TypeSpec(
    kind=TypeKind.DICT,
    args=[
        TypeSpec(kind=TypeKind.STR),
        TypeSpec(kind=TypeKind.INT),
    ],
)
```

---

## Callable types

Illustrative shape (parameter list representation may vary by producer):

```python
TypeSpec(
    kind=TypeKind.CALLABLE,
    args=[
        TypeSpec(kind=TypeKind.LIST),  # parameters
        TypeSpec(kind=TypeKind.INT),   # return
    ],
)
```

---

## Enum types

```python
TypeSpec(
    kind=TypeKind.ENUM,
    args=[...],  # literal values or enum members
)
```

---

## Any

Fallback when the producer cannot classify a type more precisely:

```python
TypeSpec(kind=TypeKind.ANY)
```

---

## Cross-language notes

The IR is designed so it can map cleanly to:

- Rust enums and serde-friendly structs
- PyO3-style FFI boundaries

| IR        | Typical mapping |
|-----------|-----------------|
| ModelSpec | struct        |
| TypeSpec  | nested enum or tagged union |
| TypeKind  | enum discriminant |

---

## Future extensions

Possible additions:

- Refinement types (bounds, regex, etc.)
- Shape hints for tabular data
- Protocol / interface types
- Incremental diffing between IR versions
- Graph-shaped dependency IR

---

## Summary

> ModelSpec IR is a **deterministic, backend-agnostic, serializable** model of Python types.

**Implementation:** [`velarium`](https://pypi.org/project/velarium/) — normalization, JSON codec, builders. **Consumers:** **`velotype`** (`.pyi`), and future packages (**morphra**, **granitus**, …) per [valarium.md](valarium.md). Other tools can consume the same JSON shape without depending on every package in the monorepo.

**Regression tests:** The monorepo keeps integration tests and canonical JSON golden files under `tests/` (see root [README.md](../README.md#development)). Changing wire JSON or normalization should update fixtures and [CHANGELOG.md](../CHANGELOG.md).
