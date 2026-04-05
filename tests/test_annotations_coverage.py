"""Broad coverage for stubber.annotations.type_to_typespec and annotation_to_typespec."""

from __future__ import annotations

import datetime
import typing
from collections.abc import Callable
from enum import Enum
from typing import Any, Literal, Optional, TypeVar, Union, get_args

import pytest

from stubber.annotations import annotation_to_typespec, type_to_typespec
from stubber.ir import TypeKind


class Color(Enum):
    RED = "r"
    BLUE = "b"


T = TypeVar("T")


@pytest.mark.parametrize(
    ("anno", "kind"),
    [
        (None, TypeKind.NONE),
        (typing.Any, TypeKind.ANY),
        (int, TypeKind.INT),
        (float, TypeKind.FLOAT),
        (bool, TypeKind.BOOL),
        (str, TypeKind.STR),
        (bytes, TypeKind.BYTES),
        (datetime.datetime, TypeKind.DATETIME),
        (datetime.date, TypeKind.DATE),
        (datetime.time, TypeKind.TIME),
    ],
)
def test_primitive_kinds(anno: Any, kind: TypeKind) -> None:
    ts = type_to_typespec(anno, optional=False)
    assert ts.kind == kind


def test_forward_ref_and_str_any() -> None:
    ts = type_to_typespec(typing.ForwardRef("X"), optional=False)
    assert ts.kind == TypeKind.ANY
    ts2 = type_to_typespec("not_evaluated", optional=False)
    assert ts2.kind == TypeKind.ANY


def test_literal_single_and_multi() -> None:
    ts = type_to_typespec(Literal[1], optional=False)
    assert ts.kind == TypeKind.LITERAL
    ts2 = type_to_typespec(Literal[1, 2], optional=False)
    assert ts2.kind == TypeKind.UNION
    ts3 = type_to_typespec(Literal[1, 2, 3], optional=False)
    assert ts3.kind == TypeKind.UNION


def test_enum_as_origin() -> None:
    ts = type_to_typespec(Literal[Color.RED, Color.BLUE], optional=False)
    assert ts.kind in (TypeKind.UNION, TypeKind.LITERAL)


def test_enum_class_as_type() -> None:
    ts = type_to_typespec(Color, optional=False)
    assert ts.kind == TypeKind.ENUM


def test_union_pep604_and_optional() -> None:
    ts = type_to_typespec(int | None, optional=False)
    assert ts.kind == TypeKind.UNION
    ts2 = type_to_typespec(Optional[str], optional=False)
    assert ts2.kind == TypeKind.UNION


def test_union_typing_union() -> None:
    ts = type_to_typespec(Union[int, str], optional=False)
    assert ts.kind == TypeKind.UNION


def test_list_dict_set_tuple() -> None:
    assert type_to_typespec(list[int], optional=False).kind == TypeKind.LIST
    assert type_to_typespec(dict[str, int], optional=False).kind == TypeKind.DICT
    assert type_to_typespec(set[bool], optional=False).kind == TypeKind.SET
    assert type_to_typespec(tuple[int, str], optional=False).kind == TypeKind.TUPLE


def test_list_dict_set_bare_builtins_are_any() -> None:
    """Bare `list` / `dict` / `set` resolve as plain types → ANY in MVP."""
    assert type_to_typespec(list, optional=False).kind == TypeKind.ANY
    assert type_to_typespec(dict, optional=False).kind == TypeKind.ANY
    assert type_to_typespec(set, optional=False).kind == TypeKind.ANY


def test_tuple_empty_and_ellipsis() -> None:
    ts = type_to_typespec(tuple[()], optional=False)
    assert ts.kind == TypeKind.TUPLE
    ts2 = type_to_typespec(tuple[int, ...], optional=False)
    assert ts2.kind == TypeKind.TUPLE


def test_type_and_generic() -> None:
    ts = type_to_typespec(type[int], optional=False)
    assert ts.kind == TypeKind.GENERIC
    assert type_to_typespec(list[int], optional=False).kind == TypeKind.LIST


def test_callable_variants() -> None:
    ts = type_to_typespec(Callable[[int, str], bool], optional=False)
    assert ts.kind == TypeKind.CALLABLE
    assert type_to_typespec(Callable, optional=False).kind == TypeKind.ANY


def test_callable_non_list_first_arg() -> None:
    # Use a Callable whose first get_args element is not a list-of-types (ellipsis form)
    ts = type_to_typespec(Callable[..., int], optional=False)
    assert ts.kind == TypeKind.CALLABLE


def test_typevar_branch() -> None:
    ts = type_to_typespec(T, optional=False)
    assert ts.kind == TypeKind.TYPE_VAR


def test_unknown_class_falls_back_any() -> None:
    class Plain:
        pass

    ts = type_to_typespec(Plain, optional=False)
    assert ts.kind == TypeKind.ANY


def test_annotation_to_typespec_str_without_globalns() -> None:
    ts = annotation_to_typespec("int", globalns=None)
    assert ts.kind == TypeKind.ANY


def test_annotation_to_typespec_str_eval_ok() -> None:
    ts = annotation_to_typespec("int", globalns={"int": int})
    assert ts.kind == TypeKind.INT


def test_annotation_to_typespec_str_eval_fails() -> None:
    ts = annotation_to_typespec("undefined_name_xyz", globalns={})
    assert ts.kind == TypeKind.ANY


def test_fully_unknown_type_object() -> None:
    ts = type_to_typespec(42, optional=False)
    assert ts.kind == TypeKind.ANY


def test_empty_enum_is_any() -> None:
    E = Enum("E", {})
    ts = type_to_typespec(E, optional=False)
    assert ts.kind == TypeKind.ANY


def test_callable_unsubscripted() -> None:
    from typing import Callable as TypingCallable

    ts = type_to_typespec(TypingCallable, optional=False)
    assert ts.kind == TypeKind.CALLABLE
    assert ts.args is None


def test_tuple_no_args_uses_any() -> None:
    ts = type_to_typespec(tuple[()], optional=False)
    assert ts.kind == TypeKind.TUPLE


def test_type_subscription_and_generic_alias() -> None:
    ts = type_to_typespec(type[int], optional=False)
    assert ts.kind == TypeKind.GENERIC


def test_generic_origin_no_parameters() -> None:
    import typing

    ts = type_to_typespec(typing.Generic, optional=False)
    assert ts.kind == TypeKind.GENERIC
    assert ts.args == []
