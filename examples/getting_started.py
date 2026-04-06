"""Minimal runnable example: dataclass → ModelSpec → JSON + .pyi text.

Run from the repo root (with dev env)::

    uv run python examples/getting_started.py

Or after ``pip install velarium velotype`` from any directory::

    python path/to/examples/getting_started.py
"""

from __future__ import annotations

from dataclasses import dataclass

from velarium import dumps_model_spec, loads_model_spec, modelspec_from_dataclass
from velarium import normalize_typespec, type_to_typespec
from velotype import generate_pyi


@dataclass
class User:
    name: str
    age: int


def main() -> None:
    spec = modelspec_from_dataclass(User)
    text = dumps_model_spec(spec)
    spec2 = loads_model_spec(text)
    assert spec2 == spec

    assert normalize_typespec(spec.fields["name"]).kind.value == "str"
    assert type_to_typespec(int).kind.value == "int"

    pyi = generate_pyi(spec)
    assert "User" in pyi or "name" in pyi
    print("OK:", len(text), "bytes JSON,", len(pyi), "chars stub preview")


if __name__ == "__main__":
    main()
