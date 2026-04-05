"""Broad coverage for velotype.annotations.type_to_typespec and annotation_to_typespec."""

from __future__ import annotations

import datetime
import typing
from collections.abc import Callable
from enum import Enum
from typing import Any, ClassVar, Final, Literal, Optional, Protocol, TypeVar, Union

import pytest
from typing_extensions import Annotated, NotRequired, ParamSpec, Required, TypeVarTuple

from velotype.annotations import annotation_to_typespec, type_to_typespec
from velotype.ir import TypeKind


class Color(Enum):
    RED = "r"
    BLUE = "b"


class _PlainNominal:
    """Module-level class for nominal TypeSpec tests."""

    pass


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


def test_forward_ref_resolves_with_globalns() -> None:
    g = {"int": int, "__name__": "test"}
    ts = type_to_typespec(typing.ForwardRef("int"), optional=False, globalns=g)
    assert ts.kind == TypeKind.INT


def test_str_annotation_resolves_with_globalns() -> None:
    g = {"int": int, "__name__": "test"}
    ts = type_to_typespec("int", optional=False, globalns=g)
    assert ts.kind == TypeKind.INT


def test_annotated_final_classvar_stripped() -> None:
    assert type_to_typespec(Annotated[int, "m"], optional=False).kind == TypeKind.INT
    assert type_to_typespec(Final[str], optional=False).kind == TypeKind.STR
    assert type_to_typespec(ClassVar[bool], optional=False).kind == TypeKind.BOOL


def test_not_required_required_unwrap() -> None:
    inner = type_to_typespec(NotRequired[int], optional=False)
    assert inner.optional is True
    assert inner.kind == TypeKind.UNION
    assert any(a.kind == TypeKind.INT for a in (inner.args or []))
    req = type_to_typespec(Required[str], optional=False)
    assert req.kind == TypeKind.STR


def test_typevar_with_bound() -> None:
    TB = TypeVar("TB", bound=int)
    ts = type_to_typespec(TB, optional=False)
    assert ts.kind == TypeKind.TYPE_VAR and ts.name == "TB"
    assert ts.args is not None and ts.args[0].kind == TypeKind.INT


def test_param_spec_and_typevar_tuple() -> None:
    P = ParamSpec("P")
    Ts = TypeVarTuple("Ts")
    assert type_to_typespec(P, optional=False).kind == TypeKind.PARAM_SPEC
    assert type_to_typespec(Ts, optional=False).kind == TypeKind.TYPE_VAR_TUPLE


class _Proto(Protocol):
    def m(self) -> int: ...


def test_protocol_and_plain_nominal() -> None:
    p = type_to_typespec(_Proto, optional=False)
    assert p.kind == TypeKind.PROTOCOL
    assert p.qualname == "_Proto"
    class Plain:
        pass

    n = type_to_typespec(Plain, optional=False)
    assert n.kind == TypeKind.NOMINAL


def test_annotation_to_typespec_eval_fallback_after_forward_ref_fails() -> None:
    """`(int)` is not a valid standalone ForwardRef form; eval path produces int."""
    ts = annotation_to_typespec("(int)", globalns={"int": int})
    assert ts.kind == TypeKind.INT


def test_annotation_to_typespec_eval_when_evaluate_forward_ref_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def boom(*_a: object, **_k: object) -> None:
        raise RuntimeError("no forward ref")

    monkeypatch.setattr("velarium.annotations.evaluate_forward_ref", boom)
    ts = annotation_to_typespec("int", globalns={"int": int})
    assert ts.kind == TypeKind.INT


def test_type_to_typespec_forward_ref_exception_is_any(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("velarium.annotations.evaluate_forward_ref", lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError()))
    ts = type_to_typespec(typing.ForwardRef("int"), optional=False, globalns={"int": int})
    assert ts.kind == TypeKind.ANY


def test_type_to_typespec_str_annotation_exception_is_any(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("velarium.annotations.evaluate_forward_ref", lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError()))
    ts = type_to_typespec("int", optional=False, globalns={"int": int})
    assert ts.kind == TypeKind.ANY


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
    # Bare Callable: unparameterized alias → callable with no args (same as typing.Callable)
    assert type_to_typespec(Callable, optional=False).kind == TypeKind.CALLABLE
    assert type_to_typespec(Callable, optional=False).args is None


def test_callable_non_list_first_arg() -> None:
    # Use a Callable whose first get_args element is not a list-of-types (ellipsis form)
    ts = type_to_typespec(Callable[..., int], optional=False)
    assert ts.kind == TypeKind.CALLABLE


def test_typevar_branch() -> None:
    ts = type_to_typespec(T, optional=False)
    assert ts.kind == TypeKind.TYPE_VAR


def test_unknown_class_is_nominal_phase02() -> None:
    ts = type_to_typespec(_PlainNominal, optional=False)
    assert ts.kind == TypeKind.NOMINAL
    assert ts.qualname == "_PlainNominal"
    assert ts.module == __name__


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
