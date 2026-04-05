"""Stubber: ModelSpec IR, normalization, and stub generation."""

from stubber.annotations import annotation_to_typespec, type_to_typespec
from stubber.ir import (
    FieldSpec,
    ModelConfig,
    ModelMetadata,
    ModelSpec,
    TypeKind,
    TypeSpec,
)
from stubber.json_codec import dumps_model_spec, loads_model_spec, model_spec_from_dict, model_spec_to_dict
from stubber.modelspec_build import modelspec_from_dataclass, modelspec_from_typed_dict, typespec_from_object
from stubber.normalize import normalize_typespec, normalize_union, optional_to_union
from stubber.stubgen import generate_pyi, render_typespec

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
    "modelspec_from_dataclass",
    "modelspec_from_typed_dict",
    "typespec_from_object",
    "normalize_typespec",
    "normalize_union",
    "optional_to_union",
    "generate_pyi",
    "render_typespec",
]

__version__ = "0.1.0"
