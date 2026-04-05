"""Coverage for stubber.stubgen render_typespec and generate_pyi."""

from __future__ import annotations

import pytest

from stubber.ir import ModelConfig, ModelSpec, TypeKind, TypeSpec
from stubber.stubgen import generate_pyi, render_typespec


@pytest.mark.parametrize(
    "kind",
    [
        TypeKind.NONE,
        TypeKind.ANY,
        TypeKind.INT,
        TypeKind.FLOAT,
        TypeKind.BOOL,
        TypeKind.STR,
        TypeKind.BYTES,
        TypeKind.DATETIME,
        TypeKind.DATE,
        TypeKind.TIME,
        TypeKind.TIMESTAMP,
        TypeKind.TYPE_VAR,
    ],
)
def test_render_primitives_and_time(kind: TypeKind) -> None:
    s = render_typespec(TypeSpec(kind=kind))
    assert isinstance(s, str) and len(s) > 0


def test_render_literal_with_and_without_default() -> None:
    assert "Literal" in render_typespec(TypeSpec(kind=TypeKind.LITERAL, default="a"))
    assert (
        render_typespec(TypeSpec(kind=TypeKind.LITERAL, default=None)) == "typing.Any"
    )


def test_render_list_set_dict_tuple() -> None:
    assert "list[" in render_typespec(
        TypeSpec(kind=TypeKind.LIST, args=[TypeSpec(kind=TypeKind.INT)])
    )
    assert "set[" in render_typespec(
        TypeSpec(kind=TypeKind.SET, args=[TypeSpec(kind=TypeKind.INT)])
    )
    assert "dict[" in render_typespec(
        TypeSpec(
            kind=TypeKind.DICT,
            args=[TypeSpec(kind=TypeKind.STR), TypeSpec(kind=TypeKind.INT)],
        )
    )
    assert "tuple[()]" in render_typespec(TypeSpec(kind=TypeKind.TUPLE, args=[]))
    assert "tuple[int, str]" in render_typespec(
        TypeSpec(
            kind=TypeKind.TUPLE,
            args=[TypeSpec(kind=TypeKind.INT), TypeSpec(kind=TypeKind.STR)],
        )
    )


def test_render_union_empty_and_enum() -> None:
    assert render_typespec(TypeSpec(kind=TypeKind.UNION, args=[])) == "typing.Any"
    assert "|" in render_typespec(
        TypeSpec(
            kind=TypeKind.UNION,
            args=[TypeSpec(kind=TypeKind.INT), TypeSpec(kind=TypeKind.NONE)],
        )
    )


def test_render_enum_literal_and_fallback() -> None:
    s = render_typespec(
        TypeSpec(
            kind=TypeKind.ENUM,
            args=[
                TypeSpec(kind=TypeKind.LITERAL, default=1),
                TypeSpec(kind=TypeKind.INT),
            ],
        )
    )
    assert "Literal" in s
    assert render_typespec(TypeSpec(kind=TypeKind.ENUM, args=[])) == "typing.Any"


def test_render_callable_branches() -> None:
    assert "typing.Callable[..., typing.Any]" in render_typespec(
        TypeSpec(kind=TypeKind.CALLABLE, args=None)
    )
    plist = TypeSpec(
        kind=TypeKind.LIST,
        args=[TypeSpec(kind=TypeKind.INT), TypeSpec(kind=TypeKind.STR)],
    )
    s = render_typespec(
        TypeSpec(kind=TypeKind.CALLABLE, args=[plist, TypeSpec(kind=TypeKind.BOOL)])
    )
    assert "Callable" in s and "bool" in s
    s2 = render_typespec(
        TypeSpec(
            kind=TypeKind.CALLABLE,
            args=[TypeSpec(kind=TypeKind.INT), TypeSpec(kind=TypeKind.STR)],
        )
    )
    assert "Callable" in s2


def test_render_generic_any() -> None:
    assert render_typespec(TypeSpec(kind=TypeKind.GENERIC, args=[])) == "typing.Any"


def test_generate_pyi_variants() -> None:
    empty = generate_pyi(ModelSpec(name="E", fields={}))
    assert "class E" in empty and "..." in empty

    frozen = generate_pyi(
        ModelSpec(
            name="F",
            fields={"a": TypeSpec(kind=TypeKind.INT)},
            config=ModelConfig(frozen=True),
        )
    )
    assert "frozen=True" in frozen

    doc = generate_pyi(
        ModelSpec(name="G", fields={"x": TypeSpec(kind=TypeKind.STR)}),
        module_docstring="hello",
    )
    assert "hello" in doc


def test_render_literal_bool_and_sequence_defaults() -> None:
    assert "True" in render_typespec(TypeSpec(kind=TypeKind.LITERAL, default=True))
    s = render_typespec(TypeSpec(kind=TypeKind.LITERAL, default=[1, 2]))
    assert "[" in s


def test_default_repr_str() -> None:
    text = generate_pyi(
        ModelSpec(
            name="H",
            fields={"s": TypeSpec(kind=TypeKind.STR, default="hi")},
        )
    )
    assert "'hi'" in text or '"hi"' in text
