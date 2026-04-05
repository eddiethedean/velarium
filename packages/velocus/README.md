# velocus

**Role in Velarium:** **Ecosystem CLI** — single entry point to inspect IR, drive builds, and dispatch to backends (**velotype**, **morphra**, **granitus**, future tools) without each package exposing a separate UX.

| | |
|---|---|
| **PyPI** | `velocus` (scaffold) |
| **Status** | **Scaffold** — orchestration not implemented |

## Today

Use the [**velotype**](../velotype/README.md) CLI for:

- `velotype ir` — print ModelSpec JSON for a class the builders support (see [docs/model-sources.md](../../docs/model-sources.md))  
- `velotype stub` — emit `.pyi` body  

## Planned behavior

Thin orchestration only: parse commands, call **`velarium`** and backend packages, format output — no duplicated IR logic (see [docs/valarium.md](../../docs/valarium.md)).

## See also

- [docs/design.md](../../docs/design.md) — CLI philosophy  
- [docs/modelspec-ir.md](../../docs/modelspec-ir.md) — IR consumed by orchestrated tools  
- [Documentation index](../../docs/README.md)  
