from __future__ import annotations

from stubber.ir import ModelSpec, TypeKind, TypeSpec
from stubber.json_codec import dumps_model_spec, loads_model_spec
from stubber.normalize import normalize_union


def test_typespec_roundtrip_json() -> None:
    m = ModelSpec(
        name="X",
        fields={
            "a": TypeSpec(kind=TypeKind.INT),
            "b": TypeSpec(
                kind=TypeKind.UNION,
                args=[TypeSpec(kind=TypeKind.STR), TypeSpec(kind=TypeKind.NONE)],
                optional=True,
            ),
        },
    )
    s = dumps_model_spec(m)
    m2 = loads_model_spec(s)
    assert m2.name == "X"
    assert m2.fields["a"].kind == TypeKind.INT
    assert m2.fields["b"].kind == TypeKind.UNION


def test_normalize_union_flattens() -> None:
    inner = TypeSpec(
        kind=TypeKind.UNION,
        args=[TypeSpec(kind=TypeKind.INT), TypeSpec(kind=TypeKind.FLOAT)],
    )
    top = TypeSpec(kind=TypeKind.UNION, args=[inner, TypeSpec(kind=TypeKind.STR)])
    out = normalize_union(top)
    assert out.kind == TypeKind.UNION
    assert out.args is not None
    assert len(out.args) == 3
