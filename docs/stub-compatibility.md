# Stub compatibility (Phase 0.4)

Generated **`.pyi`** text from **`velotype.generate_pyi`** is meant to be **reviewable** and **usable** under common type checkers (**mypy**, **Pyright**), not only syntactically valid Python.

This page separates **guarantees** from **best-effort** behavior and describes how CI validates the in-repo corpus.

## Guarantees

| Area | Commitment |
|------|------------|
| **Syntax** | Output is valid Python stub text for the emitted module shape (`from __future__ import annotations`, `@dataclass`, field annotations). |
| **PEP 604 annotations** | Scalar and composite types render as union / builtin generics where applicable (`int \| str`, `list[T]`, …). |
| **Advanced / nominal IR** | Kinds that would require extra declarations in a stub (**`TypeVar`**, **`ParamSpec`**, **`Protocol`**, **`nominal`**, etc.) render as **`typing.Any`** so stubs stay **import-safe** without synthesizing declarations. The IR still carries **`name`**, **`qualname`**, and **`module`** for other tools. |
| **Determinism** | For a fixed **`ModelSpec`** and **`generate_pyi`** options, output is stable (golden tests in **`tests/fixtures/stub_corpus/`**). Each committed **`.pyi`** has a matching **`<name>.json`**; **`test_stubgen_corpus.py`** discovers cases from **`*.pyi`** so checker config JSON in the same folder is not mistaken for a model. |

## Best-effort

| Area | Notes |
|------|--------|
| **Imports** | **`import datetime`** is emitted only when a field’s **`TypeSpec`** needs **`datetime.*`** (including nested **`list`** / **`dict`** / unions). **`import typing`** and **`from dataclasses import dataclass`** are always included for the current emitter. |
| **Nominal / forward types** | Safe **`from module import Class`** lines are **not** inferred automatically when they might create cycles; **nominal** and similar kinds stay **`Any`** in stubs unless a future phase adds cycle-aware resolution. |
| **Formatting** | Default output is deterministic string assembly. Optional **`format_stub_text(..., backend="ruff")`** runs **`ruff format -`** when **`ruff`** is on **`PATH`**; failures fall back to the input text. |
| **Checker versions** | **mypy** and **Pyright** evolve; CI pins versions via **`uv.lock`**. Re-run **`uv lock`** when upgrading checkers and fix corpus or generator as needed. |

## `generate_pyi` options (summary)

| Parameter | Role |
|-----------|------|
| **`module_docstring`** | Inserts a module-level docstring after imports. |
| **`header` / `footer`** | Extra lines before / after the class (e.g. comments or tool banners). |
| **`include_all`** | When **`True`**, appends **`__all__ = ("ClassName",)`**. |
| **`style`** | **`"default"`** includes a short velotype banner; **`"minimal"`** omits it. |

## CI validation

The **`stub-check`** job in **`.github/workflows/ci.yml`** runs:

1. **`mypy`** with **`tests/fixtures/stub_corpus/mypy.ini`** on the golden **`.pyi`** files.
2. **`pyright`** with **`tests/fixtures/stub_corpus/pyrightconfig.json`** on the same files.

**Corpus cases (goldens)** include at least: a minimal int model (**`simple_int`**), date/time kinds including nested containers (**`with_datetime`**), and a frozen model mixing callable, union, and literal (**`mixed_kinds`**). Add **`name.json`** + **`name.pyi`** together and extend **`pyrightconfig.json`** **`include`** when adding cases.

Checker dependencies live in the **`stubcheck`** dependency group in **`pyproject.toml`** (installed with **`uv sync --group stubcheck`**). Versions are pinned in **`uv.lock`**.

Regenerating goldens after intentional stub changes: rebuild **`ModelSpec`** JSON, run **`generate_pyi`**, update the matching **`.pyi`** file under **`tests/fixtures/stub_corpus/`**, then ensure **`pytest`** and the **`stub-check`** job pass.

## See also

- [Supported annotations](supported-annotations.md) — IR matrix and stub fallbacks for advanced kinds.
- [Roadmap — Phase 0.4](ROADMAP.md#phase-04--stub-generation-quality) — phase exit criteria.
