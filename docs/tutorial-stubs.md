# Tutorial: from clone to generated stubs

This walkthrough uses the **Velarium** repo itself. You generate `.pyi` stubs for dataclasses under an importable package using **`velotype batch stub`**.

## Prerequisites

- Python **3.10+**
- [uv](https://docs.astral.sh/uv/) (recommended) or `pip`

## 1. Clone and install

```bash
git clone https://github.com/eddiethedean/velarium.git
cd velarium
uv sync --group dev
```

This installs workspace members **`velarium`** and **`velotype`** into the environment.

## 2. Pick a package on `PYTHONPATH`

Batch mode imports a **root package** by name. The test fixture package `fixtures.batch_pkg` ships with this repo (under `tests/fixtures/`). Put **`tests`** on `PYTHONPATH` so `fixtures.batch_pkg` imports:

```bash
export PYTHONPATH="$(pwd)/tests"
```

## 3. Generate stubs into a directory

```bash
uv run velotype batch stub fixtures.batch_pkg --out-dir /tmp/velotype-stubs
```

You should see `Wrote …` lines and one `.pyi` file per discovered dataclass (file names encode the module and class, e.g. `fixtures_batch_pkg__RootModel.pyi`).

Optional flags:

- **`--merge`** — emit a single `merged.pyi` instead of one file per class.
- **`--exclude PATTERN`** — repeat to add [fnmatch](https://docs.python.org/3/library/fnmatch.html) patterns against source file paths (in addition to built-in skips for library `tests/` trees).
- **`--fail-fast`** — stop on the first build/write error instead of collecting all failures.
- **`--cache-dir DIR`** — store per-class **ModelSpec** JSON so unchanged sources skip rebuilding IR (invalidated when **`velarium`** / **`velotype`** versions change or source bytes change). See [performance.md](performance.md).
- **`--no-cache`** — do not read or write the batch cache, even if **`--cache-dir`** is set.

## 4. Batch IR (JSON) instead of stubs

To dump **ModelSpec** JSON for every dataclass in the tree:

```bash
uv run velotype batch ir fixtures.batch_pkg --out-dir /tmp/velotype-ir
```

Use **`--merge`** to write `merged.json` (a JSON array of model objects).

## 5. Pre-commit (optional)

To regenerate stubs on commit, see [`.pre-commit-hooks.yaml`](../.pre-commit-hooks.yaml) at the repo root and the [Troubleshooting](troubleshooting-cli.md) doc for hook setup notes.

## 6. Watch mode (dev only)

Install the optional extra and re-run batch stub when files change:

```bash
uv sync --group dev   # includes velotype[watch] in this workspace
uv run velotype watch stub fixtures.batch_pkg --out-dir /tmp/velotype-stubs
```

Stop with **Ctrl+C**. New classes may require a new process if Python has already imported the package (normal import caching).

## Next steps

- [Performance](performance.md) — batch cache, normalization hook, benchmark scripts.
- [Stub compatibility](stub-compatibility.md) — what we guarantee for generated `.pyi` files.
- [Troubleshooting CLI](troubleshooting-cli.md) — exit codes, cache behavior, optional JSON limits.
- [Security](security.md) — what the CLI imports and executes; trust boundaries.
- [Interchange: IR JSON](interchange-ir-json.md) — using IR outside Python.
