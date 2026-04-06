# Velotype CLI user guide

**`velotype`** is the command-line interface for **ModelSpec IR** export and **`.pyi`** stub generation. It lives in the [**velotype** PyPI package](https://pypi.org/project/velotype/); IR types and builders come from **`velarium`**.

Run **`velotype --help`**, **`velotype ir --help`**, etc., for the exact options on your version.

### Runnable example (Velarium clone)

From the repo root, with the fixture package on **`PYTHONPATH`**:

```bash
export PYTHONPATH="$(pwd)/tests"
velotype ir fixtures.batch_pkg:RootModel
```

That target is a real dataclass used in CI ([`tests/fixtures/batch_pkg`](https://github.com/eddiethedean/velarium/tree/main/tests/fixtures/batch_pkg)).

## Global behavior

- **Targets** are **`module:Class`** or **`module:Outer.Inner`** (nested class). The CLI **imports** the module and resolves attributes—same trust model as `python -c "import module"` (see [Security](../security.md)).
- **Alternative entry:** `python -m velotype …` (same commands).
- **`ir`** and **`stub`** use **`modelspec_from_dataclass`** today: the class should be a **dataclass** (or compatible). For other model kinds, use the **library** builders and **`dump_ir`**-style flows in Python (see [Velarium library](velarium-library.md)).

## `velotype ir`

Print **ModelSpec** JSON for one class.

```bash
velotype ir PACKAGE.MODULE:ClassName
velotype ir PACKAGE.MODULE:ClassName -o out.json
```

- **`--out` / `-o`** — write to a file instead of stdout.

## `velotype stub`

Emit a **`.pyi`** body for one class.

```bash
velotype stub PACKAGE.MODULE:ClassName
velotype stub PACKAGE.MODULE:ClassName -o model.pyi
```

## `velotype batch stub`

Scan an importable **package** (or module) for **dataclasses** and write one **`.pyi`** per class (default) or a single merged file.

```bash
velotype batch stub myapp.models --out-dir ./stubs
```

Common options:

| Option | Meaning |
|--------|---------|
| **`--out-dir` / `-o`** | Output directory (required). |
| **`--merge`** | Single **`merged.pyi`** instead of one file per class. |
| **`--exclude` / `-x`** | Extra [fnmatch](https://docs.python.org/3/library/fnmatch.html) patterns on source paths (repeatable). Built-in skips include typical `tests/` trees. |
| **`--fail-fast`** | Stop on the first error instead of collecting all failures. |
| **`--cache-dir DIR`** | Cache per-class **ModelSpec** JSON to skip unchanged sources (see [Performance](../performance.md)). |
| **`--no-cache`** | Ignore cache even if **`--cache-dir`** is set. |

## `velotype batch ir`

Same discovery as **`batch stub`**, but writes **JSON** (one file per model or **`merged.json`**).

```bash
velotype batch ir myapp.models --out-dir ./ir-json
```

Options align with **`batch stub`** (`--merge`, `--exclude`, `--cache-dir`, `--no-cache`, `--fail-fast`).

## `velotype watch stub`

Re-run **`batch stub`** when source files change. Requires the optional extra:

```bash
pip install 'velotype[watch]'
```

```bash
velotype watch stub myapp.models --out-dir ./stubs
```

Optional **`--debounce`** (seconds) controls how long to wait after a change before regenerating. Stop with **Ctrl+C**.

## Exit codes

Summarized in [Troubleshooting CLI](../troubleshooting-cli.md): usage/import problems vs build/write failures.

## See also

- [Getting started](getting-started.md)
- [Tutorial: stubs](../tutorial-stubs.md) — end-to-end with this repo’s fixtures
- [Performance](../performance.md) — cache, normalization backend
- [API reference](../api-reference.md) — batch helpers (`emit_batch_stubs`, `emit_batch_ir`) for scripts
