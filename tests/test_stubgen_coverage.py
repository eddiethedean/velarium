"""Coverage for velotype.stubgen render_typespec and generate_pyi."""

from __future__ import annotations

import subprocess

import pytest

from velotype.ir import ModelConfig, ModelSpec, TypeKind, TypeSpec
from velotype.stubgen import format_stub_text, generate_pyi, render_typespec


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
        TypeKind.PARAM_SPEC,
        TypeKind.TYPE_VAR_TUPLE,
        TypeKind.PROTOCOL,
        TypeKind.NOMINAL,
    ],
)
def test_render_primitives_and_time(kind: TypeKind) -> None:
    s = render_typespec(TypeSpec(kind=kind))
    assert isinstance(s, str) and len(s) > 0
    if kind in (
        TypeKind.TYPE_VAR,
        TypeKind.PARAM_SPEC,
        TypeKind.TYPE_VAR_TUPLE,
        TypeKind.PROTOCOL,
        TypeKind.NOMINAL,
    ):
        assert s == "typing.Any"


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


def test_default_repr_non_str_uses_fallback_branch() -> None:
    """Covers ``_default_repr`` non-string path (same ``repr`` outcome, distinct line)."""
    text = generate_pyi(
        ModelSpec(
            name="J",
            fields={"n": TypeSpec(kind=TypeKind.INT, default=42)},
        )
    )
    assert "n: int = 42" in text


def test_generate_pyi_nested_datetime_in_list_triggers_import() -> None:
    """Recursive ``_typespec_needs_datetime`` covers nested ``args``."""
    spec = ModelSpec(
        name="N",
        fields={
            "xs": TypeSpec(
                kind=TypeKind.LIST,
                args=[TypeSpec(kind=TypeKind.DATETIME)],
            )
        },
    )
    text = generate_pyi(spec)
    assert "import datetime" in text


def test_generate_pyi_header_footer_include_all_minimal() -> None:
    spec = ModelSpec(name="X", fields={"a": TypeSpec(kind=TypeKind.INT)})
    text = generate_pyi(
        spec,
        header="# extra",
        footer="# end",
        include_all=True,
        style="minimal",
    )
    assert "Stub generated by velotype" not in text
    assert "# extra" in text
    assert "# end" in text
    assert '__all__ = ("X",)' in text


def test_format_stub_text_none() -> None:
    s = "x = 1\n"
    assert format_stub_text(s, backend="none") is s


def test_format_stub_text_ruff_success(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*_a: object, **_k: object) -> subprocess.CompletedProcess[bytes]:
        return subprocess.CompletedProcess([], 0, b"formatted\n", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert format_stub_text("a", backend="ruff") == "formatted\n"


def test_format_stub_text_ruff_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(*_a: object, **_k: object):
        raise OSError("nope")

    monkeypatch.setattr(subprocess, "run", boom)
    assert format_stub_text("keep", backend="ruff") == "keep"


def test_format_stub_text_ruff_nonzero_exit(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*_a: object, **_k: object):
        raise subprocess.CalledProcessError(1, ["ruff"], b"", b"err")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert format_stub_text("keep", backend="ruff") == "keep"


def test_format_stub_text_ruff_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*_a: object, **_k: object):
        raise subprocess.TimeoutExpired(cmd=["ruff"], timeout=60)

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert format_stub_text("keep", backend="ruff") == "keep"


def test_generate_pyi_datetime_nested_in_dict_triggers_import() -> None:
    """``_typespec_needs_datetime`` walks into ``dict`` value position."""
    spec = ModelSpec(
        name="D",
        fields={
            "m": TypeSpec(
                kind=TypeKind.DICT,
                args=[
                    TypeSpec(kind=TypeKind.STR),
                    TypeSpec(kind=TypeKind.DATETIME),
                ],
            )
        },
    )
    text = generate_pyi(spec)
    assert "import datetime" in text


def test_generate_pyi_union_containing_date_triggers_import() -> None:
    spec = ModelSpec(
        name="U",
        fields={
            "x": TypeSpec(
                kind=TypeKind.UNION,
                args=[
                    TypeSpec(kind=TypeKind.INT),
                    TypeSpec(kind=TypeKind.DATE),
                ],
            )
        },
    )
    assert "import datetime" in generate_pyi(spec)


def test_generate_pyi_include_all_with_default_style_keeps_banner() -> None:
    spec = ModelSpec(name="Z", fields={"a": TypeSpec(kind=TypeKind.INT)})
    text = generate_pyi(spec, include_all=True, style="default")
    assert "Stub generated by velotype" in text
    assert '__all__ = ("Z",)' in text
