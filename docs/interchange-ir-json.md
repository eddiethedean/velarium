# Interchange: ModelSpec JSON outside Python

**Velarium** does not ship a full **JSON Schema** for `ModelSpec` in Phase **0.5**. For non-Python consumers, treat **[`dumps_model_spec`](https://github.com/eddiethedean/velarium/blob/main/packages/velarium/velarium/json_codec.py)** output as the interchange format.

## Stable contract

- **Schema and semantics** are defined in [modelspec-ir.md](modelspec-ir.md) (types, fields, normalization).
- **On the wire:** JSON compatible with `dumps_model_spec` / `loads_model_spec` in **`velarium`**. Round-trip tests in the repo lock behavior.

## Versioning

- Minor **0.x** releases may extend the JSON shape in **additive** ways; see [CHANGELOG.md](../CHANGELOG.md) and the roadmap’s API/IR freeze milestones before **1.0.0**.
- Downstream tools should tolerate unknown keys if they only need a subset of the IR.

## JSON Schema (future)

An experimental or lossy **JSON Schema** projection may appear in a later release; until then, generate IR JSON from Python (`velotype ir`, **`batch ir`**, or `dumps_model_spec`) and consume that JSON in other languages or schema tools as needed.
