# stubber

[![CI](https://github.com/eddiethedean/stubber/actions/workflows/ci.yml/badge.svg)](https://github.com/eddiethedean/stubber/actions/workflows/ci.yml)

**stubber** implements the **ModelSpec IR** (intermediate representation) for portable typing: normalize annotations, serialize to JSON, and emit minimal `.pyi` stubs. Background and schema live in the **[documentation](docs/README.md)** (`docs/design.md`, `docs/modelspec-ir.md`, **[roadmap](docs/ROADMAP.md)**).

Requires **Python 3.10+**.

## Install

```bash
pip install stubber
```

Once [published to PyPI](https://pypi.org/project/stubber/), the above works. Until then, install from Git:

```bash
pip install git+https://github.com/eddiethedean/stubber.git
```

From a clone (editable, with dev tools):

```bash
pip install -e ".[dev]"
```

## CLI

Commands use Typer. Import paths look like `package.module:Class` (nested classes use `Outer.Inner`).

```bash
# Print ModelSpec IR as JSON for a dataclass
stubber ir myapp.models:User

stubber ir myapp.models:User -o user.ir.json

# Emit a stub module body (dataclass-oriented)
stubber stub myapp.models:User -o user.pyi

python -m stubber ir myapp.models:User
```

## Library

```python
from stubber import (
    dumps_model_spec,
    generate_pyi,
    loads_model_spec,
    modelspec_from_dataclass,
    type_to_typespec,
)

spec = modelspec_from_dataclass(MyModel)
print(dumps_model_spec(spec))
print(generate_pyi(spec))
```

- **`modelspec_from_typed_dict`** is available for `TypedDict` classes.
- **`normalize_typespec`** / **`optional_to_union`** apply IR normalization rules (unions, optional encoding).

## Development

Release version is set in **`stubber/__init__.py`** as `__version__` (Hatch reads it for packages—do not duplicate in `pyproject.toml`).

```bash
pytest                    # runs with coverage; stubber must stay at 100% line coverage
mypy stubber
python -m build   # sdist + wheel (requires `pip install build` or `.[dev]`)
```

## Documentation

- [Design & philosophy](docs/design.md)
- [ModelSpec IR specification](docs/modelspec-ir.md)
- [Roadmap to 1.0.0](docs/ROADMAP.md)
- [Changelog](CHANGELOG.md)
- [Installing & releasing](docs/releasing.md)

## Implementation notes

- IR types live in `stubber.ir`; JSON helpers in `stubber.json_codec`.
- The MVP focuses on dataclasses and common `typing` shapes; unresolved or exotic annotations may map to `any` in the IR.

## License

MIT (see `LICENSE`).
