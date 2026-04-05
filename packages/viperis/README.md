# viperis

**Role in Velarium:** **Python source → Velarium IR** — parse modules or files, resolve type hints where possible, and emit **`velarium`**-compatible `ModelSpec` / `TypeSpec` graphs. This is the planned *frontend* that complements **`velarium`**’s class-based builders.

| | |
|---|---|
| **PyPI** | `viperis` (scaffold) |
| **Status** | **Scaffold** — no parser implementation yet; use **`velarium.modelspec_build`** from dataclasses / `TypedDict` today |

## Planned responsibilities

- Walk Python AST for modules or file paths  
- Extract annotations and structural information  
- Feed normalized output into the shared IR (`velarium`)

## See also

- [docs/valarium.md](../../docs/valarium.md) — pipeline and component list  
- [docs/design.md](../../docs/design.md) — why the IR exists  
- [**velarium**](../velarium/README.md) — current IR implementation  
