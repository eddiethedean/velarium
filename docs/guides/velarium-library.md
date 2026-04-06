# Velarium library user guide

**`velarium`** exposes **ModelSpec** IR: **`TypeSpec`**, **`ModelSpec`**, normalization, and a deterministic **JSON codec**. Install:

```bash
pip install velarium
```

Optional extras for builders: **`velarium[pydantic]`**, **`velarium[attrs]`**, or **`velarium[sources]`** (see [Model sources](../model-sources.md)).

## Mental model

1. **Build** a **`ModelSpec`** from a Python type or class (dataclass, `TypedDict`, Pydantic, attrs, …).
2. Optionally **normalize** types (unions, optionals).
3. **Serialize** to JSON with **`dumps_model_spec`** / **`model_spec_to_dict`**, or feed a backend (e.g. **`velotype`**’s **`generate_pyi`**).

Public symbols are listed in [API reference](../api-reference.md) (`velarium.__all__`). A full runnable script lives at **[`examples/getting_started.py`](https://github.com/eddiethedean/velarium/blob/main/examples/getting_started.py)** in the repo.

## Dataclass → `ModelSpec`

```python
from dataclasses import dataclass

from velarium import dumps_model_spec, modelspec_from_dataclass


@dataclass
class User:
    name: str
    age: int


spec = modelspec_from_dataclass(User)
print(dumps_model_spec(spec))
```

## TypedDict, Pydantic, attrs

Use the matching builders (`modelspec_from_typed_dict`, `modelspec_from_pydantic_model`, `modelspec_from_attrs_class`) after installing the right extra. Details and policies: [Model sources](../model-sources.md).

## JSON: save, load, version

```python
from dataclasses import dataclass

from velarium import dumps_model_spec, loads_model_spec, modelspec_from_dataclass


@dataclass
class Item:
    id: int


spec = modelspec_from_dataclass(Item)
text = dumps_model_spec(spec)
spec2 = loads_model_spec(text)
assert spec2 == spec
```

- Serialized JSON includes **`format_version`** (integer).
- Older files **without** **`format_version`** still load (treated as version **1**). See [migration-ir.md](../migration-ir.md).
- Optional env limits for untrusted input: **`VELARIUM_JSON_MAX_DEPTH`**, **`VELARIUM_JSON_MAX_BYTES`** ([Security](../security.md)).

## Annotations → `TypeSpec`

For ad hoc typing objects (not a full model), use **`type_to_typespec`** (and **`annotation_to_typespec`** for string annotations with the right `globals` / `locals`—see [Supported annotations](../supported-annotations.md)):

```python
from velarium import type_to_typespec

ts = type_to_typespec(int)
assert ts.kind.value == "int"
```

Coverage and edge cases: [Supported annotations](../supported-annotations.md).

## Normalization

```python
from dataclasses import dataclass

from velarium import modelspec_from_dataclass, normalize_typespec


@dataclass
class M:
    x: int


spec = modelspec_from_dataclass(M)
normalized = normalize_typespec(spec.fields["x"])
```

Optional **`VELARIUM_NORMALIZE_BACKEND`** (Python vs native hook): [Performance](../performance.md).

## Working with `velotype`

Stub generation stays in **`velotype`**:

```python
from dataclasses import dataclass

from velarium import modelspec_from_dataclass
from velotype import generate_pyi, format_stub_text


@dataclass
class User:
    name: str


spec = modelspec_from_dataclass(User)
text = generate_pyi(spec)
# optional: format_stub_text(text, backend="ruff")
```

**`velotype`** re-exports most **`velarium`** public API for convenience; new code can **`import velarium`** for IR-only use.

## Stability

Pre-1.0 policy and semver expectations: [stability.md](../stability.md).
