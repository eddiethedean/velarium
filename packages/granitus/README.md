# granitus

**Role in Velarium:** **IR → Spark-like schemas** — lower Velarium IR into columnar / distributed schema definitions (e.g. Spark StructType or similar) for data pipelines.

| | |
|---|---|
| **PyPI** | [pypi.org/project/granitus](https://pypi.org/project/granitus/) (scaffold) |
| **Repository** | [github.com/eddiethedean/velarium](https://github.com/eddiethedean/velarium) |
| **Status** | **Scaffold** — no emitter yet |

## Planned use cases

- ETL and big-data jobs that need types aligned with Python stubs and JSON IR  
- Columnar systems that benefit from a single IR → schema mapping  

## See also

- [docs/valarium.md](https://github.com/eddiethedean/velarium/blob/main/docs/valarium.md) — backend overview  
- [docs/modelspec-ir.md](https://github.com/eddiethedean/velarium/blob/main/docs/modelspec-ir.md) — IR schema  
- [docs/supported-annotations.md](https://github.com/eddiethedean/velarium/blob/main/docs/supported-annotations.md) — type coverage in IR  
- [docs/model-sources.md](https://github.com/eddiethedean/velarium/blob/main/docs/model-sources.md) — how models become IR today  
- [**velarium** on PyPI](https://pypi.org/project/velarium/) — IR contract  
