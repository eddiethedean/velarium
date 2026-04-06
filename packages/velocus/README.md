# velocus

[![PyPI version](https://img.shields.io/pypi/v/velocus.svg)](https://pypi.org/project/velocus/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/eddiethedean/velarium/blob/main/LICENSE)

**Role in Velarium:** **Ecosystem CLI** — single entry point to inspect IR, drive builds, and dispatch to backends ([**velotype**](https://pypi.org/project/velotype/), [**morphra**](https://pypi.org/project/morphra/), [**granitus**](https://pypi.org/project/granitus/), future tools) without each package exposing a separate UX.

| | |
|---|---|
| **PyPI** | [pypi.org/project/velocus](https://pypi.org/project/velocus/) *(scaffold)* |
| **Repository** | [github.com/eddiethedean/velarium](https://github.com/eddiethedean/velarium) |
| **Python** | 3.10+ (when implemented) |
| **Status** | **Scaffold** — orchestration not implemented |

## Today

Use the [**velotype** CLI on PyPI](https://pypi.org/project/velotype/) for:

- `velotype ir` — print ModelSpec JSON for a class the builders support (see [docs/model-sources.md](https://github.com/eddiethedean/velarium/blob/main/docs/model-sources.md))  
- `velotype stub` — emit `.pyi` body  
- `velotype batch stub` / `velotype batch ir` — package-wide dataclass discovery and merged outputs (see [docs/tutorial-stubs.md](https://github.com/eddiethedean/velarium/blob/main/docs/tutorial-stubs.md))

Stub behavior and CI validation are documented in [docs/stub-compatibility.md](https://github.com/eddiethedean/velarium/blob/main/docs/stub-compatibility.md).

## Planned behavior

Thin orchestration only: parse commands, call [**velarium**](https://pypi.org/project/velarium/) and backend packages, format output — no duplicated IR logic (see [docs/valarium.md](https://github.com/eddiethedean/velarium/blob/main/docs/valarium.md)).

## See also

- [docs/design.md](https://github.com/eddiethedean/velarium/blob/main/docs/design.md) — CLI philosophy  
- [docs/modelspec-ir.md](https://github.com/eddiethedean/velarium/blob/main/docs/modelspec-ir.md) — IR consumed by orchestrated tools  
- [docs/api-reference.md](https://github.com/eddiethedean/velarium/blob/main/docs/api-reference.md) — tier‑1 **`velarium`** / **`velotype`** CLI and library surface  
- [Roadmap](https://github.com/eddiethedean/velarium/blob/main/docs/ROADMAP.md)  
- [Repository README](https://github.com/eddiethedean/velarium/blob/main/README.md)  
- [Documentation index](https://github.com/eddiethedean/velarium/blob/main/docs/README.md)  
- [**velotype** on PyPI](https://pypi.org/project/velotype/) — use this for stubs and IR export today  

## License

MIT — see [LICENSE](https://github.com/eddiethedean/velarium/blob/main/LICENSE).
