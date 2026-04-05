# morphra

**Role in Velarium:** **IR → Pydantic** — map Velarium (`ModelSpec` / `TypeSpec`) into Pydantic v2 models (generated source or runtime construction), preserving validation intent where the IR allows.

| | |
|---|---|
| **PyPI** | `morphra` (scaffold) |
| **Status** | **Scaffold** — no code generation yet |

## Planned use cases

- FastAPI / service layers that want models aligned with the same IR as stubs  
- Shared typing story between static stubs (**stubber**) and runtime validation  

## See also

- [docs/valarium.md](../../docs/valarium.md) — backend placement in the pipeline  
- [**velarium**](../velarium/README.md) — IR types morphra will consume  
