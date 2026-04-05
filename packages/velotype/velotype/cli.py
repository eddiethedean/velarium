"""Thin Typer CLI over ModelSpec IR (see docs/design.md)."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

import typer

from velarium.json_codec import dumps_model_spec
from velarium.modelspec_build import modelspec_from_dataclass
from velotype.batch import (
    discover_dataclass_targets,
    emit_batch_ir,
    emit_batch_stubs,
)
from velotype.cli_support import EXIT_BUILD, EXIT_USAGE, format_batch_error
from velotype.stubgen import generate_pyi

app = typer.Typer(no_args_is_help=True, add_completion=False)
batch_app = typer.Typer(no_args_is_help=True, add_completion=False)
app.add_typer(batch_app, name="batch")


def _load_class(path: str) -> type:
    if ":" not in path:
        typer.echo("Target must be module:Class", err=True)
        raise typer.Exit(code=EXIT_USAGE)
    mod_name, _, qual = path.partition(":")
    if not mod_name or not qual:
        typer.echo("Target must be module:Class", err=True)
        raise typer.Exit(code=EXIT_USAGE)
    try:
        mod = importlib.import_module(mod_name)
    except ImportError as e:
        typer.echo(f"Cannot import module {mod_name!r}: {e}", err=True)
        raise typer.Exit(code=EXIT_USAGE) from e
    obj: Any = mod
    try:
        for part in qual.split("."):
            obj = getattr(obj, part)
    except AttributeError as e:
        typer.echo(f"Cannot resolve import path {path!r}: {e}", err=True)
        raise typer.Exit(code=EXIT_USAGE) from e
    if not isinstance(obj, type):
        typer.echo(f"{path!r} is not a class", err=True)
        raise typer.Exit(code=EXIT_USAGE)
    return obj


@app.command("ir")
def dump_ir(
    target: str = typer.Argument(
        ..., help="Import path: module:Class or module:Outer.Inner"
    ),
    out: str | None = typer.Option(None, "--out", "-o", help="Write JSON to this file"),
) -> None:
    """Print ModelSpec IR as JSON for a dataclass."""
    cls = _load_class(target)
    try:
        spec = modelspec_from_dataclass(cls)
    except TypeError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=EXIT_BUILD) from e
    text = dumps_model_spec(spec)
    if out:
        with open(out, "w", encoding="utf-8") as f:
            f.write(text)
        typer.echo(f"Wrote IR to {out}")
    else:
        typer.echo(text)


@app.command("stub")
def dump_stub(
    target: str = typer.Argument(..., help="Import path: module:Class"),
    out: str | None = typer.Option(None, "--out", "-o", help="Write .pyi to this file"),
) -> None:
    """Emit a .pyi stub for a dataclass ModelSpec."""
    cls = _load_class(target)
    try:
        spec = modelspec_from_dataclass(cls)
    except TypeError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=EXIT_BUILD) from e
    text = generate_pyi(spec)
    if out:
        with open(out, "w", encoding="utf-8") as f:
            f.write(text)
        typer.echo(f"Wrote stub to {out}")
    else:
        typer.echo(text)


def _run_batch(
    *,
    package: str,
    out_dir: Path,
    exclude: list[str],
    merge: bool,
    fail_fast: bool,
    emit_ir: bool,
) -> None:
    extra = tuple(exclude)
    try:
        targets = discover_dataclass_targets(package, extra_excludes=extra)
    except ImportError as e:
        typer.echo(f"Cannot import package {package!r}: {e}", err=True)
        raise typer.Exit(code=EXIT_USAGE) from e

    if not targets:
        typer.echo(
            f"No dataclass targets found under {package!r} (after excludes).",
            err=True,
        )
        raise typer.Exit(code=EXIT_USAGE)

    if emit_ir:
        result = emit_batch_ir(
            targets,
            out_dir,
            merge=merge,
            fail_fast=fail_fast,
        )
    else:
        result = emit_batch_stubs(
            targets,
            out_dir,
            merge=merge,
            fail_fast=fail_fast,
        )

    for p in result.written:
        typer.echo(f"Wrote {p}")
    for err in result.errors:
        typer.echo(format_batch_error(err), err=True)

    if result.errors:
        raise typer.Exit(code=EXIT_BUILD)


@batch_app.command("stub")
def batch_stub(
    package: str = typer.Argument(
        ...,
        help="Root package or module to scan (importable), e.g. myapp.models",
    ),
    out_dir: Path = typer.Option(
        ...,
        "--out-dir",
        "-o",
        help="Output directory for .pyi files (or merged.pyi)",
        exists=False,
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True,
    ),
    exclude: list[str] | None = typer.Option(
        None,
        "--exclude",
        "-x",
        help="Extra fnmatch patterns for source file paths (repeatable)",
    ),
    merge: bool = typer.Option(
        False,
        "--merge",
        help="Emit a single merged.pyi instead of one file per class",
    ),
    fail_fast: bool = typer.Option(
        False,
        "--fail-fast",
        help="Stop on first error instead of collecting failures",
    ),
) -> None:
    """Batch-generate .pyi stubs for dataclasses under a package tree."""
    _run_batch(
        package=package,
        out_dir=out_dir,
        exclude=list(exclude or ()),
        merge=merge,
        fail_fast=fail_fast,
        emit_ir=False,
    )


@batch_app.command("ir")
def batch_ir(
    package: str = typer.Argument(
        ...,
        help="Root package or module to scan (importable)",
    ),
    out_dir: Path = typer.Option(
        ...,
        "--out-dir",
        "-o",
        help="Output directory for JSON files (or merged.json)",
        exists=False,
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True,
    ),
    exclude: list[str] | None = typer.Option(
        None,
        "--exclude",
        "-x",
        help="Extra fnmatch patterns for source file paths (repeatable)",
    ),
    merge: bool = typer.Option(
        False,
        "--merge",
        help="Emit merged.json (array of ModelSpec objects)",
    ),
    fail_fast: bool = typer.Option(
        False,
        "--fail-fast",
        help="Stop on first error instead of collecting failures",
    ),
) -> None:
    """Batch-dump ModelSpec IR JSON for dataclasses under a package tree."""
    _run_batch(
        package=package,
        out_dir=out_dir,
        exclude=list(exclude or ()),
        merge=merge,
        fail_fast=fail_fast,
        emit_ir=True,
    )


watch_app = typer.Typer(no_args_is_help=True, add_completion=False)
app.add_typer(watch_app, name="watch")


@watch_app.command("stub")
def watch_stub(
    package: str = typer.Argument(..., help="Package to scan (same as batch stub)"),
    out_dir: Path = typer.Option(
        ...,
        "--out-dir",
        "-o",
        help="Output directory",
        exists=False,
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True,
    ),
    exclude: list[str] | None = typer.Option(None, "--exclude", "-x"),
    merge: bool = typer.Option(False, "--merge"),
    debounce: float = typer.Option(
        0.5, "--debounce", help="Seconds to wait after a change"
    ),
) -> None:
    """Re-run batch stub when source files change (install velotype[watch])."""
    try:
        from watchfiles import watch as watch_paths
    except ImportError as e:  # pragma: no cover — exercised when watchfiles missing
        typer.echo(
            "watch requires: pip install velotype[watch] (watchfiles)",
            err=True,
        )
        raise typer.Exit(EXIT_USAGE) from e

    root_mod = importlib.import_module(package)
    paths: list[Path] = []
    if hasattr(root_mod, "__file__") and root_mod.__file__:
        paths.append(Path(root_mod.__file__).resolve().parent)
    if hasattr(root_mod, "__path__"):
        for p in root_mod.__path__:
            paths.append(Path(p).resolve())

    if not paths:
        typer.echo(f"Cannot locate source paths for {package!r}", err=True)
        raise typer.Exit(EXIT_USAGE)

    def _regen() -> None:
        _run_batch(
            package=package,
            out_dir=out_dir,
            exclude=list(exclude or ()),
            merge=merge,
            fail_fast=False,
            emit_ir=False,
        )

    _regen()
    typer.echo(f"Watching {paths} — Ctrl+C to stop.")
    debounce_ms = max(50, int(debounce * 1000))
    for _changes in watch_paths(
        *paths,
        debounce=debounce_ms,
        step=100,
    ):
        _regen()


def main() -> None:
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
