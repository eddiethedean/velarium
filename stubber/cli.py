"""Thin Typer CLI over ModelSpec IR (see docs/design.md)."""

from __future__ import annotations

import importlib
from typing import Any

import typer

from stubber.json_codec import dumps_model_spec
from stubber.modelspec_build import modelspec_from_dataclass
from stubber.stubgen import generate_pyi

app = typer.Typer(no_args_is_help=True, add_completion=False)


def _load_class(path: str) -> type:
    if ":" not in path:
        typer.echo("Target must be module:Class", err=True)
        raise typer.Exit(code=2)
    mod_name, _, qual = path.partition(":")
    if not mod_name or not qual:
        typer.echo("Target must be module:Class", err=True)
        raise typer.Exit(code=2)
    mod = importlib.import_module(mod_name)
    obj: Any = mod
    for part in qual.split("."):
        obj = getattr(obj, part)
    if not isinstance(obj, type):
        typer.echo(f"{path!r} is not a class", err=True)
        raise typer.Exit(code=2)
    return obj


@app.command("ir")
def dump_ir(
    target: str = typer.Argument(..., help="Import path: module:Class or module:Outer.Inner"),
    out: str | None = typer.Option(None, "--out", "-o", help="Write JSON to this file"),
) -> None:
    """Print ModelSpec IR as JSON for a dataclass."""
    cls = _load_class(target)
    try:
        spec = modelspec_from_dataclass(cls)
    except TypeError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=1) from e
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
        raise typer.Exit(code=1) from e
    text = generate_pyi(spec)
    if out:
        with open(out, "w", encoding="utf-8") as f:
            f.write(text)
        typer.echo(f"Wrote stub to {out}")
    else:
        typer.echo(text)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
