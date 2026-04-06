# Stubs for a whole Python package

This guide ties together **`velotype batch stub`**, how discovery works, and where to go next for type checkers, CI, and non-dataclass models.

## What “whole package” means here

**`velotype batch stub`** walks an **importable package** (or module) and finds **`@dataclass`** classes. For each one it builds a **`ModelSpec`** and writes a **`.pyi`** file (or a single merged file). It does **not** automatically discover Pydantic models, attrs classes, or `TypedDict` definitions as separate entry points—those use different **`velarium`** builders (see [Model sources](../model-sources.md) and [Velarium library](velarium-library.md)).

So in practice, “stub out my whole package” means: **every dataclass you want stubs for must live under a package root you pass to the CLI**, and you use **batch** mode instead of calling **`velotype stub module:Class`** dozens of times.

## Prerequisites

1. **Install** **`velotype`** (pulls in **`velarium`**):

   ```bash
   pip install velotype
   ```

2. **Your package must import cleanly** the same way you would run `python -c "import myproject.models"`. Typical setups:

   - Editable install: `pip install -e .` from your project root.
   - Or set **`PYTHONPATH`** to the directory that contains your top-level package directory (the folder that has `__init__.py`).

3. **Pick the import root** you want to scan—often the subpackage that holds models, e.g. **`myproject.models`**, or **`myproject`** if dataclasses are spread under it.

## Generate stubs in one command

```bash
velotype batch stub myproject.models --out-dir stubs/
```

- **`myproject.models`** — import path to the package (or module) to scan.
- **`--out-dir`** — directory to write **`.pyi`** files (required).

Default behavior is **one file per discovered class** (file names encode module and class). For a **single** stub file:

```bash
velotype batch stub myproject.models --out-dir stubs/ --merge
```

That writes **`merged.pyi`** under **`stubs/`** (see [Velotype CLI](velotype-cli.md) for all flags).

## Options you will use on real repos

| Need | Flag / doc |
|------|------------|
| Faster repeat runs | **`--cache-dir .velotype-cache`** — [Performance](../performance.md) |
| Skip paths (tests, vendored code) | **`--exclude '*/tests/*'`** (repeat **`-x`**); patterns are [fnmatch](https://docs.python.org/3/library/fnmatch.html) on file paths |
| Stop on first failure | **`--fail-fast`** |
| IR JSON instead of `.pyi` | **`velotype batch ir`** — same discovery, JSON output |
| Regenerate on save (dev) | **`velotype watch stub`** — optional **`velotype[watch]`** — [Velotype CLI](velotype-cli.md) |

## Point type checkers at the output

Generated files are normal **`.pyi`** stub text. How **mypy** / **Pyright** pick them up depends on your layout (`stubPath`, `mypy_path`, `PYTHONPATH`, etc.). Guarantees, imports, and checker behavior are covered in **[Stub compatibility](../stub-compatibility.md)**—read that before treating output as a semver promise for consumers.

## Automation and CI

- Run **`velotype batch stub`** in CI or a **pre-commit** hook after changing models; keep the output committed or generated in a build step, per your policy.
- This repo’s **stub-check** pattern (mypy + Pyright on a corpus) is described in **stub-compatibility** and the root **Development** section of the README; adapt paths to your package.

## Trust and security

Batch mode **imports** your package tree (like **`python -m`**). Only run it on **trusted** code. See **[Security](../security.md)**.

## If you also have Pydantic, attrs, or `TypedDict`

Use **`velarium`** builders (`modelspec_from_pydantic_model`, `modelspec_from_attrs_class`, `modelspec_from_typed_dict`, …) and **`velotype.generate_pyi`** in **your own** script or loop, or mix **batch** (dataclasses) with custom generation for other types. Policies and extras: **[Model sources](../model-sources.md)**.

## See also

| Doc | Why |
|-----|-----|
| [Getting started](getting-started.md) | Install + first **`ir`** / **`stub`** |
| [Velotype CLI](velotype-cli.md) | Full CLI reference (**`batch`**, **`watch`**, exit codes) |
| [Tutorial: stubs](../tutorial-stubs.md) | Step-by-step with this repo’s **`fixtures.batch_pkg`** |
| [Stub compatibility](../stub-compatibility.md) | Checker guarantees and CI patterns |
| [Troubleshooting CLI](../troubleshooting-cli.md) | **`PYTHONPATH`**, import errors, exit codes |
| [examples/README.md](https://github.com/eddiethedean/velarium/blob/main/examples/README.md) | Runnable **`PYTHONPATH`** + fixture commands |
