# velocus

**Role in Velarium:** **Ecosystem CLI** — single entry point to inspect IR, drive builds, and dispatch to backends (**velotype**, **morphra**, **granitus**, future tools) without each package exposing a separate UX.

| | |
|---|---|
| **PyPI** | [pypi.org/project/velocus](https://pypi.org/project/velocus/) (scaffold) |
| **Repository** | [github.com/eddiethedean/velarium](https://github.com/eddiethedean/velarium) |
| **Status** | **Scaffold** — orchestration not implemented |

## Today

Use the [**velotype** CLI on PyPI](https://pypi.org/project/velotype/) for:

- `velotype ir` — print ModelSpec JSON for a class the builders support (see [docs/model-sources.md](https://github.com/eddiethedean/velarium/blob/main/docs/model-sources.md))  
- `velotype stub` — emit `.pyi` body  

## Planned behavior

Thin orchestration only: parse commands, call **`velarium`** and backend packages, format output — no duplicated IR logic (see [docs/valarium.md](https://github.com/eddiethedean/velarium/blob/main/docs/valarium.md)).

## See also

- [docs/design.md](https://github.com/eddiethedean/velarium/blob/main/docs/design.md) — CLI philosophy  
- [docs/modelspec-ir.md](https://github.com/eddiethedean/velarium/blob/main/docs/modelspec-ir.md) — IR consumed by orchestrated tools  
- [Documentation index](https://github.com/eddiethedean/velarium/blob/main/docs/README.md)  
