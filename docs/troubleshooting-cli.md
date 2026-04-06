# Troubleshooting the `velotype` CLI

## Exit codes

| Code | Meaning |
|------|--------|
| **0** | Success. |
| **1** | **Build** failure: target is not a dataclass, builder raised `TypeError`, batch emission reported errors, or a batch write failed. |
| **2** | **Usage / import**: bad `module:Class` syntax, module import failed, unresolved attribute path, target not a class, no dataclass targets after discovery, or **`velotype watch`** without `pip install velotype[watch]`. |

Single-target commands (`velotype ir`, `velotype stub`) use the same conventions. Batch mode prints lines like `[build] module:Class: …` or `[write] …` on stderr for each failure; the process exits **1** if any item failed.

## “Cannot import module”

- Ensure the package is **installed** or on **`PYTHONPATH`** (e.g. `export PYTHONPATH=src` for a `src/` layout).
- Use dotted imports: `myapp.models:User`, not filesystem paths.

## “… is not a dataclass” / exit **1**

- **`ir`** and **`stub`** (and batch) currently build from **`modelspec_from_dataclass`**. Use a `@dataclass` class, or call the **velarium** builders in Python for Pydantic / attrs / `TypedDict` and pass a `ModelSpec` to **`generate_pyi`** / **`dumps_model_spec`**.

## Batch: “No dataclass targets found” (exit **2**)

- The package imported, but discovery found no dataclasses. Common causes:
  - Only non-dataclass types or re-exports (re-exports are skipped when `__module__` does not match the scanned module).
  - Everything lived under a path treated as tests (see **velotype** `batch` discovery rules in source: library `pkg/tests/` trees are skipped; repo **`tests/fixtures/`** is allowed for fixture packages).

## Pre-commit hooks

- Point **`entry`** at the same Python that has **`velotype`** installed (`which velotype` / `uv run velotype`).
- If the hook runs in a minimal env, install **`velotype`** there or use `language: system` with `uv run velotype …`.
- Ensure **`PYTHONPATH`** includes your package root if you do not install the project as a package.

## Watch mode

- Requires **`velotype[watch]`** (pulls in **watchfiles**).
- Not intended for CI; use **`batch stub`** in pipelines.
- Does **not** use **`--cache-dir`**; each regeneration runs a full batch (see [performance.md](performance.md)).

## Batch cache (`--cache-dir`)

- **Stale outputs after edits:** The cache keys off **file content** (SHA-256 of the module file). If you change a class without saving, or edit a different file than the one `inspect.getfile` reports, clear the cache directory or use **`--no-cache`** once.
- **Version bumps:** Upgrading **`velarium`** or **`velotype`** changes the cache key; old entries are ignored (leftover files in `DIR` are harmless but can be deleted to save disk).
- **Corrupt JSON:** If a cache file is truncated or edited by hand, the run **rebuilds** IR for that class and overwrites the entry when possible.

## Filing issues

Use the repository **CLI failure** issue template and include: **`velotype --version`**, full command line, `PYTHONPATH`, and the traceback or stderr output.
