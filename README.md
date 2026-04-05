# Velarium

[![CI](https://github.com/eddiethedean/valarium/actions/workflows/ci.yml/badge.svg)](https://github.com/eddiethedean/valarium/actions/workflows/ci.yml)

**Velarium** is a monorepo of Python packages around a shared **ModelSpec IR** (Velarium): normalized types, JSON codec, and pluggable backends (stubs today; Pydantic, Spark, and a unified CLI are planned).

| Package | Role |
|--------|------|
| [**velarium**](packages/velarium/README.md) | Core IR (`velarium` on PyPI): types, normalization, JSON, dataclass/TypedDict → IR |
| [**stubber**](packages/stubber/README.md) | IR → `.pyi`; **`stubber`** CLI (`ir`, `stub`) |
| [**viperis**](packages/viperis/README.md) | Python source → IR (scaffold) |
| [**morphra**](packages/morphra/README.md) | IR → Pydantic (scaffold) |
| [**granitus**](packages/granitus/README.md) | IR → Spark-like schemas (scaffold) |
| [**clarion**](packages/clarion/README.md) | Ecosystem CLI (scaffold; use **`stubber`** for now) |

**Documentation index:** [docs/README.md](docs/README.md). Ecosystem architecture: [docs/valarium.md](docs/valarium.md). IR schema: [docs/modelspec-ir.md](docs/modelspec-ir.md). Design: [docs/design.md](docs/design.md). Roadmap: [docs/ROADMAP.md](docs/ROADMAP.md).

Requires **Python 3.10+**.

## Install

Published wheels (when available):

```bash
pip install velarium stubber
```

From a Git clone (recommended: [uv](https://docs.astral.sh/uv/)):

```bash
uv sync --group dev
```

Or editable installs without uv:

```bash
pip install -e packages/velarium -e "packages/stubber[dev]"
```

## CLI (`stubber`)

```bash
stubber ir myapp.models:User
stubber stub myapp.models:User -o user.pyi
python -m stubber ir myapp.models:User
```

## Library

IR and JSON live in **`velarium`**; stub emission in **`stubber`**. For compatibility, **`stubber`** still re-exports the same public symbols as before (import `stubber` or import from `velarium` directly).

```python
from velarium import dumps_model_spec, modelspec_from_dataclass, type_to_typespec
from stubber import generate_pyi

spec = modelspec_from_dataclass(MyModel)
print(dumps_model_spec(spec))
print(generate_pyi(spec))
```

## Development

- **stubber** version: `packages/stubber/stubber/__init__.py` (`__version__`).
- **velarium** version: `packages/velarium/velarium/__init__.py`.

```bash
uv sync --group dev
uv run pytest
uv run python -m ty check
# Build wheels for each package:
for d in packages/*/; do (cd "$d" && python -m build); done
```

## Documentation

- [Velarium ecosystem spec](docs/valarium.md)
- [ModelSpec IR specification](docs/modelspec-ir.md)
- [Roadmap](docs/ROADMAP.md)
- [Changelog](CHANGELOG.md)
- [Installing & releasing](docs/releasing.md)

## License

MIT (see `LICENSE`).
