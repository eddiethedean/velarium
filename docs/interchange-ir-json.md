# Interchange: ModelSpec JSON outside Python

**Velarium** does not ship a full **JSON Schema** for `ModelSpec` yet (as of **0.8.x**); Phase **0.5** focused on documenting interchange. For non-Python consumers, treat **[`dumps_model_spec`](https://github.com/eddiethedean/velarium/blob/main/packages/velarium/velarium/json_codec.py)** output as the interchange format. Canonical JSON includes a top-level **`format_version`** integer (see [migration-ir.md](migration-ir.md)).

## Stable contract

- **Schema and semantics** are defined in [modelspec-ir.md](modelspec-ir.md) (types, fields, normalization).
- **On the wire:** JSON compatible with `dumps_model_spec` / `loads_model_spec` in **`velarium`**. Round-trip tests in the repo lock behavior; **Hypothesis** property tests further exercise `ModelSpec` JSON round-trip and normalization idempotence (Phase **0.7**).

## Untrusted or oversized JSON

If you parse IR JSON from external sources, use optional limits in **`velarium`** (**`VELARIUM_JSON_MAX_DEPTH`**, **`VELARIUM_JSON_MAX_BYTES`**) and read the threat model in [security.md](security.md). Batch cache reads honor the byte limit when set ([troubleshooting-cli.md](troubleshooting-cli.md)).

## Versioning

- The **`format_version`** field (integer, monotonic) labels the **top-level JSON shape** for `ModelSpec`. **`velarium`** emits the current version; **`loads_model_spec`** accepts missing/`null` **`format_version`** as **1** for older files.
- Minor **0.x** releases may extend the JSON shape in **additive** ways; see [CHANGELOG.md](../CHANGELOG.md), [stability.md](stability.md), and the roadmap’s API/IR milestones before **1.0.0**.
- Downstream tools should tolerate unknown keys if they only need a subset of the IR.

## JSON Schema (future)

An experimental or lossy **JSON Schema** projection may appear in a later release; until then, generate IR JSON from Python (`velotype ir`, **`batch ir`**, or `dumps_model_spec`) and consume that JSON in other languages or schema tools as needed.
