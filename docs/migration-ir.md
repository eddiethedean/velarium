# Migrating ModelSpec IR JSON

This guide covers **JSON** produced by `dumps_model_spec` / consumed by `loads_model_spec` in **`velarium`** (and the **`velotype ir`** / **`velotype batch ir`** commands).

## `format_version` field

Since **0.8.0**, canonical JSON includes a top-level integer field:

```json
{
  "format_version": 1,
  "name": "MyModel",
  "fields": {}
}
```

- **`MODEL_SPEC_FORMAT_VERSION`** in code (exported from **`velarium`** and **`velotype`**) is the **current** format number emitted by `dumps_model_spec`.
- **`loads_model_spec`** / **`model_spec_from_dict`**: if **`format_version`** is **missing** or **`null`**, it is treated as **1**, so **older snapshots** (0.7.x and earlier) still load unchanged.
- When present, **`format_version`** must be a JSON **integer** (not a string, boolean, or float). Non-integers raise **`ValueError`** (booleans are rejected because JSON `true`/`false` are not valid wire versions).
- If **`format_version`** is **greater** than the version supported by your installed **`velarium`**, loading raises **`ValueError`** — upgrade **`velarium`** (and **`velotype`** if you use the CLI) to a release that supports that format.

There is **no** separate `model_spec_v2` export path; evolution is a **single codec** plus an explicit version integer.

## Bumping format in your own pipeline

1. Serialize with the **`velarium`** version you run in CI (`dumps_model_spec`); output always includes **`format_version`** for **0.8.0+**.
2. When upgrading across minors, read [CHANGELOG.md](../CHANGELOG.md) for additive JSON fields or normalization changes.
3. Golden / fixture JSON in this repo lives under **`tests/fixtures/ir_golden/`** (strict round-trips) and **`tests/fixtures/stub_corpus/`** (ModelSpec JSON inputs for stub tests). Regenerate intentionally when IR output changes.

## Related docs

- [modelspec-ir.md](modelspec-ir.md) — IR types and semantics  
- [interchange-ir-json.md](interchange-ir-json.md) — using JSON outside Python  
- [stability.md](stability.md) — pre-1.0 API and IR policy  
- [security.md](security.md) — limits on untrusted JSON (`VELARIUM_JSON_MAX_DEPTH`, `VELARIUM_JSON_MAX_BYTES`)
