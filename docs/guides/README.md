# User guides

Task-oriented documentation for **library users** and **CLI users**. For architecture and IR semantics, see the [documentation index](../README.md).

Runnable scripts that CI exercises live under **[`examples/`](https://github.com/eddiethedean/velarium/tree/main/examples)** in the repository (see **`examples/README.md`**).

| Guide | You are… |
|-------|----------|
| [Getting started](getting-started.md) | New to Velarium; want install + first success in minutes. |
| [Stubs for a whole package](package-stubs.md) | **`velotype batch stub`** across an importable package: **`PYTHONPATH`**, flags, type checkers, non-dataclass models. |
| [Velotype CLI](velotype-cli.md) | Using **`velotype`** from the terminal (`ir`, `stub`, **`batch`**, **`watch`**). |
| [Velarium library](velarium-library.md) | Importing **`velarium`** in Python: builders, JSON, normalization. |

## Related

- [Tutorial: clone → batch stubs](../tutorial-stubs.md) — repo-specific walkthrough with **`fixtures.batch_pkg`**
- [Troubleshooting CLI](../troubleshooting-cli.md) — exit codes, imports, cache quirks
- [Model sources](../model-sources.md) — dataclass, `TypedDict`, Pydantic, attrs
- [API reference](../api-reference.md) — supported public symbols
