# Performance and scale

Velarium (**`velarium`**) and the stub backend (**`velotype`**) are designed for **large** codebases: predictable IR, optional **incremental batch caching**, and a path toward **optional native** normalization without changing JSON meaning.

## Where time goes

Typical costs in a **`velotype batch stub`** / **`velotype batch ir`** run:

1. **Importing** the target package and walking modules (`discover_dataclass_targets`).
2. **Building IR** per dataclass (`modelspec_from_dataclass` → annotations, normalization).
3. **Emitting** output (`.pyi` text or JSON).

Normalization and JSON serialization are usually smaller than import + class introspection on big trees, but union-heavy models can spend noticeable time in **`normalize_typespec`** / **`normalize_union`**. Use profiling (below) to confirm hotspots in your project.

## Batch incremental cache

When you pass **`--cache-dir DIR`** to **`velotype batch stub`** or **`velotype batch ir`**, **`velotype`** stores a **per-class** JSON cache of `ModelSpec` (same format as **`dumps_model_spec`**) under `DIR`.

A cache entry is used only when all of the following match:

- **SHA-256** of the defining module’s **source file bytes** (see `inspect.getfile` on the class).
- **`velarium.__version__`** and **`velotype.__version__`** (bump invalidates entries when tooling changes).
- **Mode** (`stub` vs `ir`), **`merge`** flag, and **`stub_style`** (library API; CLI batch uses **`minimal`** stubs today).

If the class has **no readable source file** (e.g. some dynamic or interactive definitions), caching is **skipped** for that class; IR is always rebuilt.

Use **`--no-cache`** to ignore the cache for a single run (read and write disabled).

**`velotype watch stub`** does not use this cache; it re-runs full batch on each change. For interactive work, **watch** is often enough; for CI or large trees, prefer **batch** with **`--cache-dir`** (and optionally commit the cache directory only if your workflow benefits).

## Normalization backend hook

Set **`VELARIUM_NORMALIZE_BACKEND=native`** to request a **future** optional native implementation of **`normalize_typespec`** (e.g. a compiled extension shipped as **`velarium._native`**). If **`velarium._native`** is not installed or does not expose **`normalize_typespec`**, **`velarium`** **falls back to pure Python** behavior.

The default is **`VELARIUM_NORMALIZE_BACKEND=python`** (or unset).

**Semantic rule:** native and Python backends must produce the **same** normalized IR for the same inputs; the repo’s golden and integration tests enforce JSON IR stability.

A shipped **Rust** (or other) wheel is **not** required for **0.6.0**; the hook is documented so optional accelerators can land in a later **0.6.x** without API changes.

## Pure Python improvements

Union deduplication uses a stable **`typespec_dedupe_key`** (`velarium.json_codec`) aligned with JSON serialization, so behavior stays consistent with earlier releases while avoiding redundant work.

## Profiling locally

From the repo root (with **`uv sync --group dev`**):

```bash
uv run python scripts/profile_velotype_batch.py
```

This writes **`.velotype_profile.stats`** (gitignored). Inspect with:

```bash
python -m pstats .velotype_profile.stats
```

## Benchmark script (cold vs cache)

```bash
uv run python scripts/benchmark_velotype_batch.py
```

Runs a small **timeit** comparison: batch **without** a cache directory vs **with** a populated **`--cache-dir`**. Numbers are environment-dependent; use them for **regression** checks, not absolute SLAs.

An optional GitHub Actions workflow **Benchmark** (`workflow_dispatch`) runs the same script in CI.

## Related

- [ROADMAP.md](ROADMAP.md) — Phase **0.6** exit criteria
- [tutorial-stubs.md](tutorial-stubs.md) — batch CLI flags
- [troubleshooting-cli.md](troubleshooting-cli.md) — cache pitfalls
