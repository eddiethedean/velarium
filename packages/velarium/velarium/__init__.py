"""Velarium: ModelSpec IR, normalization, JSON codec, and Python→IR extraction."""

from velarium.annotations import annotation_to_typespec, type_to_typespec
from velarium.ir import (
    FieldSpec,
    ModelConfig,
    ModelMetadata,
    ModelSpec,
    TypeKind,
    TypeSpec,
)
from velarium.json_codec import dumps_model_spec, loads_model_spec, model_spec_from_dict, model_spec_to_dict
from velarium.modelspec_build import modelspec_from_dataclass, modelspec_from_typed_dict, typespec_from_object
from velarium.normalize import normalize_typespec, normalize_union, optional_to_union

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
]

__version__ = "0.1.0"
