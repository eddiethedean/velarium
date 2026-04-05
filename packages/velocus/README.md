# velocus

**Role in Velarium:** **Ecosystem CLI** — single entry point to inspect IR, drive builds, and dispatch to backends (**stubber**, **morphra**, **granitus**, future tools) without each package exposing a separate UX.

| | |
|---|---|
| **PyPI** | `velocus` (scaffold) |
| **Status** | **Scaffold** — orchestration not implemented |

## Today

Use the [**stubber**](../stubber/README.md) CLI for:

- `stubber ir` — print ModelSpec JSON for a dataclass  
- `stubber stub` — emit `.pyi` body  

## Planned behavior

Thin orchestration only: parse commands, call **`velarium`** and backend packages, format output — no duplicated IR logic (see [docs/valarium.md](../../docs/valarium.md)).

## See also

- [docs/design.md](../../docs/design.md) — CLI philosophy  
- [Documentation index](../../docs/README.md)  
