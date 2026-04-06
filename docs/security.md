# Security

This document is the **threat model** and disclosure pointer for **Velarium** and **`velotype`** (Phase **0.7**). It complements [What “1.0.0” means](ROADMAP.md) (security expectations toward stable releases).

## Trust boundaries

### `velotype` CLI (`ir`, `stub`, `batch`, `watch`)

Commands take **import paths** (`module:Class` or `module:Outer.Inner`). The CLI uses `importlib.import_module` to load packages and walks attributes to resolve the target class. **Importing a module executes its top-level code** (and transitively loads dependencies). That is **equivalent to running code you choose**—the same trust model as `python -c "import yourpackage"`.

- **Do not** point the CLI at **untrusted** or unknown packages. There is no sandbox.
- **Batch** and **watch** scan importable trees under a root package; only use roots you trust.

There is **no network fetch** of code in the default CLI paths: behavior is local imports and writing outputs (IR JSON, `.pyi`, batch cache files).

### Library builders and `annotation_to_typespec`

When resolving **string** annotations, [`velarium` annotations](https://github.com/eddiethedean/velarium/blob/main/packages/velarium/velarium/annotations.py) may call `eval` on the annotation string if forward-reference evaluation fails. That code runs with the **class or module namespace** of the model being introspected. It is intended for **trusted** application and library code that defines your models—not for evaluating arbitrary strings supplied by an untrusted user in isolation.

### ModelSpec JSON (`loads_model_spec` / `model_spec_from_dict`)

Parsing IR JSON builds Python objects from structured data. Malformed input can raise exceptions. The top-level **`format_version`** field, when present, must be a JSON **integer** (see [migration-ir.md](migration-ir.md)). **Untrusted JSON** (e.g. from a network peer) should be validated and size-limited before parsing; see [Resource limits](#resource-limits) for optional knobs.

The **batch cache** reads JSON files from `--cache-dir`. Corrupt or hostile files are treated as cache misses when parsing fails; optional **byte limits** apply when configured (see below).

## Resource limits

Optional environment variables limit deserialization **depth** and **size** (see [Troubleshooting CLI](troubleshooting-cli.md) for quick reference):

| Variable | Effect |
|----------|--------|
| `VELARIUM_JSON_MAX_DEPTH` | Maximum nesting depth for `TypeSpec` trees when deserializing from JSON (default **256** if unset). Exceeding the limit raises `ValueError`. |
| `VELARIUM_JSON_MAX_BYTES` | If set to a positive integer, `loads_model_spec` rejects UTF-8 input whose **byte** length exceeds this value before `json.loads`. If unset, no byte limit is applied. |

Batch cache reads honor `VELARIUM_JSON_MAX_BYTES` when set: oversized cache files are ignored (cache miss).

## Reporting issues

Please report security-sensitive bugs **privately** via [GitHub Security Advisories](https://docs.github.com/en/code-security/security-advisories) for this repository, or open a standard issue for non-sensitive failures. Include versions of **velarium** / **velotype**, Python, and a minimal reproducer when possible.

## Related docs

- [interchange-ir-json.md](interchange-ir-json.md) — JSON interchange and untrusted input
- [migration-ir.md](migration-ir.md) — **`format_version`** and legacy JSON
- [modelspec-ir.md](modelspec-ir.md) — IR schema and semantics
- [performance.md](performance.md) — batch cache; byte limits on cache reads
- [troubleshooting-cli.md](troubleshooting-cli.md) — env vars table for limits
