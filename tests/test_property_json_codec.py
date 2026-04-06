"""Property tests: JSON round-trip and normalization idempotence (Phase 0.7)."""

from __future__ import annotations

import json

import hypothesis.strategies as st
from hypothesis import HealthCheck, given, settings

from velarium.json_codec import (
    MODEL_SPEC_FORMAT_VERSION,
    dumps_model_spec,
    loads_model_spec,
    model_spec_from_dict,
    typespec_from_dict,
    typespec_to_dict,
)
from velarium.normalize import normalize_typespec
from velotype.ir import ModelConfig, ModelMetadata, ModelSpec, TypeKind, TypeSpec

_primitive = st.sampled_from(
    [
        TypeSpec(kind=TypeKind.INT),
        TypeSpec(kind=TypeKind.STR),
        TypeSpec(kind=TypeKind.FLOAT),
        TypeSpec(kind=TypeKind.BOOL),
        TypeSpec(kind=TypeKind.NONE),
        TypeSpec(kind=TypeKind.ANY),
        TypeSpec(kind=TypeKind.BYTES),
    ]
)


def _extend(children: st.SearchStrategy[TypeSpec]) -> st.SearchStrategy[TypeSpec]:
    return st.one_of(
        st.builds(lambda c: TypeSpec(kind=TypeKind.LIST, args=[c]), children),
        st.builds(lambda c: TypeSpec(kind=TypeKind.SET, args=[c]), children),
        st.builds(
            lambda a, b: TypeSpec(kind=TypeKind.UNION, args=[a, b]), children, children
        ),
        st.builds(
            lambda a, b: TypeSpec(kind=TypeKind.DICT, args=[a, b]), children, children
        ),
        st.builds(
            lambda xs: TypeSpec(kind=TypeKind.TUPLE, args=list(xs)),
            st.lists(children, min_size=1, max_size=3),
        ),
    )


_typespec_strategy = st.recursive(_primitive, _extend, max_leaves=50)

_model_name = st.text(
    alphabet=st.characters(min_codepoint=0x41, max_codepoint=0x5A),
    min_size=1,
    max_size=24,
)

_config_strategy = st.builds(
    ModelConfig,
    frozen=st.booleans(),
    extra=st.sampled_from(["allow", "forbid", "ignore"]),
    validate_assignment=st.booleans(),
    from_attributes=st.booleans(),
    strict=st.booleans(),
)

_metadata_strategy = st.builds(
    ModelMetadata,
    source_module=st.none()
    | st.text(alphabet=st.characters(min_codepoint=97, max_codepoint=122), max_size=12),
    source_file=st.none() | st.just("/src/models.py"),
    line_number=st.none() | st.integers(min_value=1, max_value=9999),
    generated_by=st.text(
        alphabet=st.characters(min_codepoint=0x61, max_codepoint=0x7A),
        min_size=1,
        max_size=12,
    ),
    version=st.none() | st.text(max_size=8),
)


@st.composite
def _model_spec_strategy(draw) -> ModelSpec:
    name = draw(_model_name)
    n = draw(st.integers(min_value=0, max_value=6))
    fields: dict[str, TypeSpec] = {}
    for i in range(n):
        fields[f"f{i}"] = draw(_typespec_strategy)
    use_cfg = draw(st.booleans())
    use_meta = draw(st.booleans())
    config = draw(_config_strategy) if use_cfg else None
    metadata = draw(_metadata_strategy) if use_meta else None
    return ModelSpec(name=name, fields=fields, config=config, metadata=metadata)


_ci_settings = settings(
    max_examples=25,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)


@_ci_settings
@given(_model_spec_strategy())
def test_model_spec_json_roundtrip(m: ModelSpec) -> None:
    text = dumps_model_spec(m, indent=None)
    m2 = loads_model_spec(text)
    assert m2 == m


@_ci_settings
@given(_model_spec_strategy())
def test_model_spec_dumped_json_always_has_format_version(m: ModelSpec) -> None:
    data = json.loads(dumps_model_spec(m, indent=None))
    assert data["format_version"] == MODEL_SPEC_FORMAT_VERSION


@_ci_settings
@given(_model_spec_strategy())
def test_model_spec_loads_after_stripping_format_version_from_dict(
    m: ModelSpec,
) -> None:
    """Wire JSON may omit ``format_version``; dict round-trip without it must match."""
    data = json.loads(dumps_model_spec(m, indent=None))
    assert data.pop("format_version") == MODEL_SPEC_FORMAT_VERSION
    m2 = model_spec_from_dict(data)
    assert m2 == m


@_ci_settings
@given(_model_spec_strategy())
def test_model_spec_double_json_roundtrip(m: ModelSpec) -> None:
    t1 = dumps_model_spec(m, indent=None)
    m1 = loads_model_spec(t1)
    t2 = dumps_model_spec(m1, indent=None)
    assert loads_model_spec(t2) == m1 == m


@_ci_settings
@given(_typespec_strategy)
def test_typespec_to_dict_roundtrip(ts: TypeSpec) -> None:
    assert typespec_from_dict(typespec_to_dict(ts)) == ts


@_ci_settings
@given(_typespec_strategy)
def test_normalize_typespec_idempotent(ts: TypeSpec) -> None:
    once = normalize_typespec(ts)
    twice = normalize_typespec(once)
    assert once == twice
