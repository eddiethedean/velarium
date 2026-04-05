# Supported annotations (Phase 0.2)

This document lists how Python typing constructs map to **ModelSpec IR** (`TypeSpec` / `TypeKind`) in **`velarium`**. It is the **support matrix** referenced by the [roadmap](ROADMAP.md) Phase **0.2.\*** exit criteria. For schema details see [modelspec-ir.md](modelspec-ir.md). For **which Python class kinds** can be turned into `ModelSpec` (dataclass, `TypedDict`, Pydantic, attrs) and install extras, see [model-sources.md](model-sources.md).

## Conventions

- **Lossy** means we preserve structure where practical; otherwise we emit `any` or a documented placeholder.
- **PEP 563** (`from __future__ import annotations`): string annotations are resolved via `get_type_hints` with the declaring class’s module namespace where possible.
- **Forward references**: Unresolvable forward refs become `kind: "any"` (not an error at IR extraction time).

### TypedDict and PEP 563

If a **`TypedDict`** class body is parsed with **`from __future__ import annotations`** enabled, member annotations are stored as **strings**. Runtime `TypedDict` machinery may then compute empty or incorrect **`__required_keys__` / `__optional_keys__`** for `Required[...]` / `NotRequired[...]`. For reliable key optionality, define `TypedDict` subclasses in a module **without** that future import, or use `get_type_hints`-compatible runtime forms. The **`velarium`** tests use a dedicated `tests/td_fixtures.py` module for this reason.

## Summary table

| Construct | IR shape | Notes |
|-----------|----------|--------|
| `int`, `float`, `bool`, `str`, `bytes` | primitives | |
| `None` / `type(None)` | `none` | |
| `Any` | `any` | |
| `Union[A, B]`, `A \| B`, `Optional[T]` | `union` + normalization | `Optional` → union with `none`, `optional` flag |
| `list[T]`, `dict[K, V]`, `set[T]`, `tuple[...]` | `list`, `dict`, `set`, `tuple` | |
| `Literal[...]` | `literal` / `union` of literals | Nested `Literal` allowed |
| `Callable[[...], R]` | `callable` | |
| `Enum` subclasses | `enum` with literal args | |
| `typing.Annotated[T, ...]` | **Inner `T` only** | Metadata **dropped** in IR (not JSON-stable) |
| `typing.Final[T]` | **Inner `T`** | |
| `typing.ClassVar[T]` | **Inner `T`** | For dataclass **fields**, `ClassVar` is unwrapped for the field’s type |
| `TypeVar` | `typevar` | **`name`** set when available; **bound** as `args[0]` when present |
| `ParamSpec` | `paramspec` | **Lossy**: name only when available |
| `TypeVarTuple` | `typevartuple` | **Lossy**: name only when available |
| `Protocol` (subclass) | `protocol` | **`qualname`** + **`module`**; structural members not expanded |
| User-defined `type` (non-enum, non-primitive) | `nominal` | **`qualname`** + **`module`** |
| `ForwardRef` / unresolvable string | `any` | Resolved when `globalns` allows |
| `TypedDict` (as model source) | `ModelSpec` fields | Required vs optional keys via `__required_keys__` / `__optional_keys__`; optional fields get `optional: true` on `TypeSpec` |
| `NotRequired[T]` / `Required[T]` | inner type | `NotRequired` → field optional; `Required` forces required in `total=False` dicts |

## Known gaps (future work)

- **Recursive / self-referential** models: same rules as forward refs; may require manual resolution.
- **ParamSpec** / **TypeVarTuple** in **generic aliases** (`list[T]` with TVT): may still collapse to `generic` / `any` in edge cases.
- **`Annotated` metadata**: not preserved; use **`velarium`** APIs directly if you need runtime metadata alongside IR.
- **Protocol** members: we store the **protocol type**, not per-method IR (that would be **viperis**-class work).

## Stub generation (`velotype`)

`render_typespec` maps **`protocol`**, **`nominal`**, **`paramspec`**, **`typevartuple`**, and **`typevar`** field types to **`typing.Any`** in emitted `.pyi` text so stubs stay import-safe without synthesizing `TypeVar` / `ParamSpec` declarations. The IR still carries **`name`**, **`qualname`**, and **`module`** for other consumers.

## Changelog

IR mapping changes are **versioned** in [CHANGELOG.md](../CHANGELOG.md); compare JSON output when upgrading.
