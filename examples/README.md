# Examples

Runnable scripts you can copy or execute locally.

| Script | What it does |
|--------|----------------|
| [`getting_started.py`](getting_started.py) | Dataclass → `ModelSpec`, JSON round-trip, normalization, `generate_pyi` (matches the [Getting started](../docs/guides/getting-started.md) / root README library snippet). |

From a clone of this repo (recommended):

```bash
uv sync --group dev
uv run python examples/getting_started.py
```

With only PyPI installs:

```bash
pip install velarium velotype
python examples/getting_started.py
```

**CLI tryout** using the repo’s batch fixture package (dataclasses under `tests/fixtures/batch_pkg/`):

```bash
cd /path/to/velarium
export PYTHONPATH="$(pwd)/tests"
uv run velotype ir fixtures.batch_pkg:RootModel
uv run velotype stub fixtures.batch_pkg:RootModel -o /tmp/root.pyi
```

Same pattern is documented in [Getting started](../docs/guides/getting-started.md) and [Tutorial: stubs](../docs/tutorial-stubs.md).
