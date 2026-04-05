"""Velotype: deterministic .pyi stub generation from Velarium (ModelSpec) IR."""

from velarium.annotations import annotation_to_typespec, type_to_typespec
from velarium.ir import (
    FieldSpec,
    ModelConfig,
    ModelMetadata,
    ModelSpec,
    TypeKind,
    TypeSpec,
)
from velarium.json_codec import (
    dumps_model_spec,
    loads_model_spec,
    model_spec_from_dict,
    model_spec_to_dict,
)
from velarium.model_metadata import metadata_for_class
from velarium.modelspec_attrs import modelspec_from_attrs_class
from velarium.modelspec_build import (
    modelspec_from_dataclass,
    modelspec_from_typed_dict,
    typespec_from_object,
)
from velarium.modelspec_pydantic import modelspec_from_pydantic_model
from velarium.normalize import normalize_typespec, normalize_union, optional_to_union
from velotype.stubgen import generate_pyi, render_typespec

__all__ = [
    "annotation_to_typespec",
    "type_to_typespec",
    "FieldSpec",
    "ModelConfig",
    "ModelMetadata",
    "ModelSpec",
    "TypeKind",
    "TypeSpec",
    "dumps_model_spec",
    "loads_model_spec",
    "model_spec_from_dict",
    "model_spec_to_dict",
    "metadata_for_class",
    "modelspec_from_attrs_class",
    "modelspec_from_dataclass",
    "modelspec_from_pydantic_model",
    "modelspec_from_typed_dict",
    "typespec_from_object",
    "normalize_typespec",
    "normalize_union",
    "optional_to_union",
    "generate_pyi",
    "render_typespec",
]

__version__ = "0.2.0"
