"""Batch discovery of dataclass models and IR / stub emission."""

from __future__ import annotations

import dataclasses
import hashlib
import importlib
import inspect
import json
import pkgutil
import re
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Literal

from velarium.ir import ModelSpec
from velarium.json_codec import (
    dumps_model_spec,
    json_input_byte_limit,
    loads_model_spec,
)
from velarium.modelspec_build import modelspec_from_dataclass
from velotype.cli_support import BatchItemError
from velotype.stubgen import generate_pyi

# ``.../tests/foo`` under a *package* (not ``.../tests/fixtures/...`` for repo data)
_TESTS_DIR = re.compile(r"/tests/(?!fixtures/)")

# User-supplied extras only by default; built-in rules are in ``path_matches_excludes``.
DEFAULT_EXCLUDE_PATTERNS: tuple[str, ...] = ()


def path_matches_excludes(file_path: str | None, patterns: tuple[str, ...]) -> bool:
    """Return True if ``file_path`` should be skipped (tests / user patterns).

    Skips library ``pkg/tests/`` trees; does not skip ``.../tests/fixtures/...``
    (fixture packages used from the Velarium test suite).
    """
    if not file_path:
        return False
    norm = Path(file_path).as_posix()
    name = Path(file_path).name
    if _TESTS_DIR.search(norm):
        return True
    if "/test/" in norm or "/testing/" in norm:
        return True
    if name.startswith("test_") and name.endswith(".py"):
        return True
    if name == "tests.py":
        return True
    for pat in patterns:
        if fnmatch(norm, pat) or fnmatch(name, pat):
            return True
    return False


def _class_import_path(cls: type) -> str:
    return f"{cls.__module__}:{cls.__qualname__}"


def _safe_stub_basename(cls: type) -> str:
    """Filesystem-safe name: ``pkg_mod_QualName`` with dots replaced."""
    mod = cls.__module__.replace(".", "_")
    qual = cls.__qualname__.replace(".", "_")
    return f"{mod}__{qual}"


def _class_source_sha256(cls: type) -> str | None:
    """SHA-256 of the defining module file bytes, or ``None`` if unavailable."""
    try:
        path = Path(inspect.getfile(cls)).resolve()
    except TypeError:
        return None
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _batch_cache_stem(
    cls: type,
    *,
    mode: Literal["ir", "stub"],
    merge: bool,
    stub_style: str,
) -> str | None:
    """Hex digest used as cache filename stem, or ``None`` when caching is not possible."""
    sh = _class_source_sha256(cls)
    if sh is None:
        return None
    import velarium
    import velotype

    key = {
        "class_path": _class_import_path(cls),
        "merge": merge,
        "mode": mode,
        "source_sha256": sh,
        "stub_style": stub_style,
        "velarium": velarium.__version__,
        "velotype": velotype.__version__,
    }
    raw = json.dumps(key, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def _load_model_spec_cache(cache_dir: Path, stem: str) -> ModelSpec | None:
    path = cache_dir / f"{stem}.json"
    if not path.is_file():
        return None
    try:
        limit = json_input_byte_limit()
        if limit is not None and path.stat().st_size > limit:
            return None
        text = path.read_text(encoding="utf-8")
        return loads_model_spec(text)
    except (OSError, UnicodeDecodeError, ValueError, TypeError, KeyError):
        return None


def _save_model_spec_cache(cache_dir: Path, stem: str, spec: ModelSpec) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / f"{stem}.json"
    path.write_text(dumps_model_spec(spec), encoding="utf-8")


def _modelspec_for_class(
    cls: type,
    *,
    cache_dir: Path | None,
    use_cache: bool,
    mode: Literal["ir", "stub"],
    merge: bool,
    stub_style: str,
) -> ModelSpec:
    stem = _batch_cache_stem(cls, mode=mode, merge=merge, stub_style=stub_style)
    if cache_dir is not None and use_cache and stem is not None:
        cached = _load_model_spec_cache(cache_dir, stem)
        if cached is not None:
            return cached
    spec = modelspec_from_dataclass(cls)
    if cache_dir is not None and use_cache and stem is not None:
        try:
            _save_model_spec_cache(cache_dir, stem, spec)
        except OSError:
            pass
    return spec


def discover_dataclass_targets(
    package: str,
    *,
    extra_excludes: tuple[str, ...] = (),
) -> list[type]:
    """Import ``package`` (module or package), walk submodules, list dataclass types defined there.

    Only classes with ``cls.__module__`` equal to the defining module are included
    (avoids re-exported types). Modules whose ``__file__`` matches an exclude pattern are skipped.
    """
    patterns = tuple(DEFAULT_EXCLUDE_PATTERNS) + tuple(extra_excludes)
    root = importlib.import_module(package)
    names: list[str] = [package]
    if hasattr(root, "__path__"):
        prefix = root.__name__ + "."
        for _finder, name, _ispkg in pkgutil.walk_packages(
            root.__path__,
            prefix,
        ):
            names.append(name)

    seen: set[type] = set()
    out: list[type] = []

    for modname in names:
        try:
            mod = importlib.import_module(modname)
        except ImportError:
            continue
        try:
            file = inspect.getfile(mod)
        except TypeError:
            file = None
        if path_matches_excludes(file, patterns):
            continue

        for attr_name in dir(mod):
            if attr_name.startswith("_"):
                continue
            obj: Any = getattr(mod, attr_name)
            if not isinstance(obj, type):
                continue
            if not dataclasses.is_dataclass(obj):
                continue
            if obj.__module__ != mod.__name__:
                continue
            if obj in seen:
                continue
            seen.add(obj)
            try:
                cls_file = inspect.getfile(obj)
            except TypeError:
                cls_file = None
            if path_matches_excludes(cls_file, patterns):
                continue
            out.append(obj)

    return out


@dataclass
class BatchEmitResult:
    written: list[Path]
    errors: list[BatchItemError]


def emit_batch_stubs(
    targets: list[type],
    out_dir: Path,
    *,
    merge: bool = False,
    fail_fast: bool = False,
    cache_dir: Path | None = None,
    use_cache: bool = True,
    stub_style: Literal["default", "minimal"] = "minimal",
) -> BatchEmitResult:
    """Write one ``.pyi`` per class, or a single merged file if ``merge`` is True.

    When ``cache_dir`` is set and ``use_cache`` is True, ``ModelSpec`` JSON is cached
    keyed by source file hash and package versions (see ``docs/performance.md``).
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    errors: list[BatchItemError] = []
    merged_chunks: list[str] = []

    for cls in targets:
        path = _class_import_path(cls)
        try:
            spec = _modelspec_for_class(
                cls,
                cache_dir=cache_dir,
                use_cache=use_cache,
                mode="stub",
                merge=merge,
                stub_style=stub_style,
            )
        except TypeError as e:
            err = BatchItemError(target=path, phase="build", message=str(e))
            errors.append(err)
            if fail_fast:
                return BatchEmitResult(written=written, errors=errors)
            continue
        text = generate_pyi(spec, style=stub_style)
        if merge:
            merged_chunks.append(f"# --- {path} ---\n{text}")
        else:
            name = _safe_stub_basename(cls) + ".pyi"
            dest = out_dir / name
            try:
                dest.write_text(text, encoding="utf-8")
                written.append(dest)
            except OSError as e:
                err = BatchItemError(target=path, phase="write", message=str(e))
                errors.append(err)
                if fail_fast:
                    return BatchEmitResult(written=written, errors=errors)

    if merge and merged_chunks:
        try:
            merged = (
                '"""Merged stubs generated by velotype batch — ModelSpec IR."""\n\n'
                + "\n\n".join(merged_chunks)
            )
            dest = out_dir / "merged.pyi"
            dest.write_text(merged, encoding="utf-8")
            written.append(dest)
        except OSError as e:
            errors.append(
                BatchItemError(
                    target="(merge)",
                    phase="write",
                    message=str(e),
                )
            )

    return BatchEmitResult(written=written, errors=errors)


def emit_batch_ir(
    targets: list[type],
    out_dir: Path,
    *,
    merge: bool = False,
    fail_fast: bool = False,
    cache_dir: Path | None = None,
    use_cache: bool = True,
) -> BatchEmitResult:
    """Write one JSON file per class, or ``merged.json`` if ``merge`` is True.

    Caching uses the same rules as :func:`emit_batch_stubs` when ``cache_dir`` is set.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    errors: list[BatchItemError] = []

    merged_objects: list[str] = []

    for cls in targets:
        path = _class_import_path(cls)
        try:
            spec = _modelspec_for_class(
                cls,
                cache_dir=cache_dir,
                use_cache=use_cache,
                mode="ir",
                merge=merge,
                stub_style="minimal",
            )
        except TypeError as e:
            errors.append(BatchItemError(target=path, phase="build", message=str(e)))
            if fail_fast:
                return BatchEmitResult(written=written, errors=errors)
            continue
        text = dumps_model_spec(spec)
        if merge:
            merged_objects.append(text.strip())
        else:
            name = _safe_stub_basename(cls) + ".json"
            dest = out_dir / name
            try:
                dest.write_text(text + "\n", encoding="utf-8")
                written.append(dest)
            except OSError as e:
                errors.append(
                    BatchItemError(target=path, phase="write", message=str(e))
                )
                if fail_fast:
                    return BatchEmitResult(written=written, errors=errors)

    if merge and merged_objects:
        try:
            arr = [json.loads(s) for s in merged_objects]
            merged_text = json.dumps(arr, indent=2) + "\n"
            dest = out_dir / "merged.json"
            dest.write_text(merged_text, encoding="utf-8")
            written.append(dest)
        except (json.JSONDecodeError, OSError) as e:
            errors.append(
                BatchItemError(target="(merge)", phase="write", message=str(e))
            )

    return BatchEmitResult(written=written, errors=errors)
