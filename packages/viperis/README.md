# viperis

**Role in Velarium:** **Python source → Velarium IR** — parse modules or files, resolve type hints where possible, and emit **`velarium`**-compatible `ModelSpec` / `TypeSpec` graphs. This is the planned *frontend* that complements **`velarium`**’s class-based builders.

| | |
|---|---|
| **PyPI** | [pypi.org/project/viperis](https://pypi.org/project/viperis/) (scaffold) |
| **Repository** | [github.com/eddiethedean/velarium](https://github.com/eddiethedean/velarium) |
| **Status** | **Scaffold** — no parser implementation yet; use **`velarium`** class-based builders ([docs/model-sources.md](https://github.com/eddiethedean/velarium/blob/main/docs/model-sources.md)) today |

## Planned responsibilities

- Walk Python AST for modules or file paths  
- Extract annotations and structural information  
- Feed normalized output into the shared IR (`velarium`)

## See also

- [docs/valarium.md](https://github.com/eddiethedean/velarium/blob/main/docs/valarium.md) — pipeline and component list  
- [docs/design.md](https://github.com/eddiethedean/velarium/blob/main/docs/design.md) — why the IR exists  
- [docs/supported-annotations.md](https://github.com/eddiethedean/velarium/blob/main/docs/supported-annotations.md) — annotation → IR matrix (what **viperis** will eventually preserve from source)  
- [**velarium** on PyPI](https://pypi.org/project/velarium/) — current IR implementation  
