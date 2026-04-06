# granitus

[![PyPI version](https://img.shields.io/pypi/v/granitus.svg)](https://pypi.org/project/granitus/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/eddiethedean/velarium/blob/main/LICENSE)

**Role in Velarium:** **IR → Spark-like schemas** — lower Velarium IR into columnar / distributed schema definitions (e.g. Spark StructType or similar) for data pipelines.

| | |
|---|---|
| **PyPI** | [pypi.org/project/granitus](https://pypi.org/project/granitus/) *(scaffold)* |
| **Repository** | [github.com/eddiethedean/velarium](https://github.com/eddiethedean/velarium) |
| **Python** | 3.10+ (when implemented) |
| **Status** | **Scaffold** — no emitter yet |
| **Related** | [**velarium** on PyPI](https://pypi.org/project/velarium/) — IR contract; [**velotype** on PyPI](https://pypi.org/project/velotype/) — parallel `.pyi` backend |

## Planned use cases

- ETL and big-data jobs that need types aligned with Python stubs and JSON IR  
- Columnar systems that benefit from a single IR → schema mapping  

## See also

- [docs/valarium.md](https://github.com/eddiethedean/velarium/blob/main/docs/valarium.md) — backend overview  
- [docs/modelspec-ir.md](https://github.com/eddiethedean/velarium/blob/main/docs/modelspec-ir.md) — IR schema  
- [docs/interchange-ir-json.md](https://github.com/eddiethedean/velarium/blob/main/docs/interchange-ir-json.md) — JSON IR interchange and **`format_version`**  
- [docs/supported-annotations.md](https://github.com/eddiethedean/velarium/blob/main/docs/supported-annotations.md) — type coverage in IR  
- [docs/model-sources.md](https://github.com/eddiethedean/velarium/blob/main/docs/model-sources.md) — how models become IR today  
- [Roadmap](https://github.com/eddiethedean/velarium/blob/main/docs/ROADMAP.md)  
- [Repository README](https://github.com/eddiethedean/velarium/blob/main/README.md)  
- [Documentation index](https://github.com/eddiethedean/velarium/blob/main/docs/README.md)  
- [**velarium** on PyPI](https://pypi.org/project/velarium/) — IR contract  

## License

MIT — see [LICENSE](https://github.com/eddiethedean/velarium/blob/main/LICENSE).
