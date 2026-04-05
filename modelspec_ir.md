# ModelSpec IR

The **ModelSpec IR** specification lives in the Velarium monorepo:

**[docs/modelspec-ir.md](docs/modelspec-ir.md)**

- **Implementation:** the **`velarium`** package (`velarium.ir`, `velarium.normalize`, `velarium.json_codec`, …).
- **Stub backend:** **`stubber`** depends on `velarium` and emits `.pyi` files.

Design background and ecosystem context: **[docs/design.md](docs/design.md)** and **[docs/valarium.md](docs/valarium.md)**.
