from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Literal, Optional

from stubber.annotations import type_to_typespec
from stubber.ir import TypeKind
from stubber.json_codec import dumps_model_spec, loads_model_spec
from stubber.modelspec_build import modelspec_from_dataclass
from stubber.stubgen import generate_pyi, render_typespec


class Color(Enum):
    RED = "red"
    BLUE = "blue"


@dataclasses.dataclass
class Sample:
    id: int
    label: str | None = None
    tags: list[str] = dataclasses.field(default_factory=list)
    lit: Literal["a", "b"] = "a"
    opt: Optional[int] = None
    col: Color = Color.RED


def test_modelspec_from_dataclass() -> None:
    spec = modelspec_from_dataclass(Sample)
    assert spec.name == "Sample"
    assert spec.fields["id"].kind == TypeKind.INT
    assert spec.fields["label"].kind == TypeKind.UNION
    assert spec.fields["lit"].kind == TypeKind.UNION
    s = dumps_model_spec(spec)
    spec2 = loads_model_spec(s)
    assert spec2.fields["id"].kind == TypeKind.INT


def test_stub_contains_class() -> None:
    spec = modelspec_from_dataclass(Sample)
    text = generate_pyi(spec)
    assert "class Sample" in text
    assert "id: int" in text


def test_render_optional_union() -> None:
    ts = type_to_typespec(str | None, optional=False)
    r = render_typespec(ts)
    assert "None" in r
    assert "str" in r
