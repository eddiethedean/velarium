"""ModelSpec intermediate representation (see docs/modelspec-ir.md)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal


class TypeKind(str, Enum):
    # Primitives
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    STR = "str"
    BYTES = "bytes"

    # Complex
    LIST = "list"
    TUPLE = "tuple"
    DICT = "dict"
    SET = "set"

    # Special
    UNION = "union"
    LITERAL = "literal"
    ENUM = "enum"
    ANY = "any"
    NONE = "none"

    # Temporal
    DATETIME = "datetime"
    DATE = "date"
    TIME = "time"
    TIMESTAMP = "timestamp"

    # Advanced
    GENERIC = "generic"
    CALLABLE = "callable"
    TYPE_VAR = "typevar"
    PARAM_SPEC = "paramspec"
    TYPE_VAR_TUPLE = "typevartuple"
    PROTOCOL = "protocol"
    NOMINAL = "nominal"


@dataclass
class TypeSpec:
    kind: TypeKind
    args: list[TypeSpec] | None = None
    optional: bool = False
    nullable: bool = False
    default: Any | None = None
    # Phase 0.2: optional metadata (JSON-serializable strings)
    name: str | None = None  # TypeVar / ParamSpec / TypeVarTuple name
    qualname: str | None = None  # nominal class or Protocol
    module: str | None = None  # __module__ for nominal / protocol


@dataclass
class ModelConfig:
    frozen: bool = False
    extra: Literal["allow", "forbid", "ignore"] = "forbid"
    validate_assignment: bool = True
    from_attributes: bool = True
    strict: bool = False


@dataclass
class FieldSpec:
    name: str
    type: TypeSpec
    required: bool
    default: Any | None = None
    alias: str | None = None
    description: str | None = None
    deprecated: bool = False


@dataclass
class ModelMetadata:
    source_module: str | None = None
    source_file: str | None = None
    line_number: int | None = None
    generated_by: str = "velarium"
    version: str | None = None


@dataclass
class ModelSpec:
    name: str
    fields: dict[str, TypeSpec] = field(default_factory=dict)
    config: ModelConfig | None = None
    metadata: ModelMetadata | None = None
