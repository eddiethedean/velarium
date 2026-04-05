# morphra

**Role in Velarium:** **IR → Pydantic** — map Velarium (`ModelSpec` / `TypeSpec`) into Pydantic v2 models (generated source or runtime construction), preserving validation intent where the IR allows. This is **codegen from IR**, distinct from **ingesting** existing Pydantic models into IR (that lives in **`velarium`** — see [docs/model-sources.md](../../docs/model-sources.md)).

| | |
|---|---|
| **PyPI** | `morphra` (scaffold) |
| **Status** | **Scaffold** — no code generation yet |

## Planned use cases

- FastAPI / service layers that want models aligned with the same IR as stubs  
- Shared typing story between static stubs (**velotype**) and runtime validation  

## See also

- [docs/valarium.md](../../docs/valarium.md) — backend placement in the pipeline  
- [docs/modelspec-ir.md](../../docs/modelspec-ir.md) — `ModelSpec` / `TypeSpec` schema  
- [docs/supported-annotations.md](../../docs/supported-annotations.md) — what the IR can represent today  
- [docs/model-sources.md](../../docs/model-sources.md) — Pydantic → IR ingestion in **velarium** (this package is the reverse direction)  
- [**velarium**](../velarium/README.md) — IR types morphra will consume  
