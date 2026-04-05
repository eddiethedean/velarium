# ModelSpec IR

The **ModelSpec IR** specification lives in the Velarium monorepo:

**[docs/modelspec-ir.md](https://github.com/eddiethedean/velarium/blob/main/docs/modelspec-ir.md)**

- **Implementation:** the [**velarium** PyPI package](https://pypi.org/project/velarium/) (`velarium.ir`, `velarium.normalize`, `velarium.json_codec`, …).
- **Stub backend:** [**velotype** on PyPI](https://pypi.org/project/velotype/) depends on `velarium` and emits `.pyi` files.

Design background and ecosystem context: **[docs/design.md](https://github.com/eddiethedean/velarium/blob/main/docs/design.md)** and **[docs/valarium.md](https://github.com/eddiethedean/velarium/blob/main/docs/valarium.md)**. Annotation coverage: **[docs/supported-annotations.md](https://github.com/eddiethedean/velarium/blob/main/docs/supported-annotations.md)**. Class-based builders (dataclass, `TypedDict`, Pydantic, attrs): **[docs/model-sources.md](https://github.com/eddiethedean/velarium/blob/main/docs/model-sources.md)**.
