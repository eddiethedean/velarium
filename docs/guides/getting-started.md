# Getting started

**Goal:** Install **Velarium** tooling and produce either **ModelSpec JSON** or a **`.pyi` stub** from a dataclass you can import.

**Requirements:** Python **3.10+**.

## 1. Install

From PyPI:

```bash
pip install velarium velotype
```

Only the core IR library:

```bash
pip install velarium
```

## 2. Pick an importable target

The **`velotype`** CLI loads your class with **`importlib`**. You pass a string:

```text
module.path:ClassName
```

Nested classes use dots:

```text
myapp.models:Outer.Inner
```

Your package must be on **`PYTHONPATH`** (installed `pip install -e .`, a virtualenv, or `export PYTHONPATH=/path/to/project`).

### Runnable example (this repository)

If you cloned **Velarium**, the test fixture package **`fixtures.batch_pkg`** is importable when **`tests`** is on the path (same setup as [Tutorial: stubs](../tutorial-stubs.md)):

```bash
cd /path/to/velarium
export PYTHONPATH="$(pwd)/tests"
velotype ir fixtures.batch_pkg:RootModel
velotype stub fixtures.batch_pkg:RootModel -o /tmp/root.pyi
```

That uses a real dataclass (`RootModel` in `tests/fixtures/batch_pkg/__init__.py`).

## 3. Print IR JSON (your project)

Replace **`myapp.models`** with your importable package:

```bash
velotype ir myapp.models:User
```

Writes JSON to stdout. To save:

```bash
velotype ir myapp.models:User -o user.ir.json
```

JSON includes a top-level **`format_version`** field (see [migration-ir.md](../migration-ir.md)).

## 4. Generate a stub (`.pyi`)

```bash
velotype stub myapp.models:User -o user.pyi
```

Or stdout:

```bash
velotype stub myapp.models:User
```

## 5. Use the library

The snippet below is the same logic as the checked-in script **[`examples/getting_started.py`](https://github.com/eddiethedean/velarium/blob/main/examples/getting_started.py)** (run with `uv run python examples/getting_started.py` from a clone).

```python
from dataclasses import dataclass

from velarium import dumps_model_spec, modelspec_from_dataclass
from velotype import generate_pyi


@dataclass
class User:
    name: str


spec = modelspec_from_dataclass(User)
print(dumps_model_spec(spec))
print(generate_pyi(spec))
```

Prefer **`from velarium import …`** when you only need IR; use **`velotype`** for **`generate_pyi`**, **`format_stub_text`**, etc.

## 6. Scale to a whole package

For many dataclasses under one import root, use **batch** mode:

```bash
velotype batch stub myapp.models --out-dir stubs/
```

For **`PYTHONPATH`**, **`--merge`**, type checkers, and non-dataclass models, see **[Stubs for a whole package](package-stubs.md)**. Also [Velotype CLI](velotype-cli.md) and [Tutorial: stubs](../tutorial-stubs.md).

## Next steps

- [Model sources](../model-sources.md) — `TypedDict`, Pydantic, attrs, extras
- [Stub compatibility](../stub-compatibility.md) — what generated stubs guarantee
- [Security](../security.md) — the CLI imports your code; trust boundaries
