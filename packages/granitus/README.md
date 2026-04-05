# granitus

**Role in Velarium:** **IR → Spark-like schemas** — lower Velarium IR into columnar / distributed schema definitions (e.g. Spark StructType or similar) for data pipelines.

| | |
|---|---|
| **PyPI** | `granitus` (scaffold) |
| **Status** | **Scaffold** — no emitter yet |

## Planned use cases

- ETL and big-data jobs that need types aligned with Python stubs and JSON IR  
- Columnar systems that benefit from a single IR → schema mapping  

## See also

- [docs/valarium.md](../../docs/valarium.md) — backend overview  
- [docs/modelspec-ir.md](../../docs/modelspec-ir.md) — IR schema  
- [docs/supported-annotations.md](../../docs/supported-annotations.md) — type coverage in IR  
- [**velarium**](../velarium/README.md) — IR contract  
