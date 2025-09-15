import json
from pathlib import Path
from typing import Dict, List, Optional, Literal

import typer
from typer import Option, Argument

from .load import load
from .render import render, list_placeholders

app = typer.Typer(
    help="Render YMD (.ymd/.yamd) prompt files using Jinja2 placeholders."
)


def _parse_vars(values: Optional[List[str]]) -> Dict[str, str]:
    """
    Parse KEY=VALUE items; if VALUE startswith '@', load from file.
    """
    ctx: Dict[str, str] = {}
    for item in values or []:
        if "=" not in item:
            typer.secho(f"--var expects KEY=VALUE, got: {item}", fg=typer.colors.RED)
            raise typer.Exit(code=2)
        key, value = item.split("=", 1)
        if value.startswith("@"):
            path = Path(value[1:])
            try:
                ctx[key] = path.read_text(encoding="utf-8")
            except OSError as e:
                typer.secho(f"Failed to read @{path}: {e}", fg=typer.colors.RED)
                raise typer.Exit(code=2)
        else:
            ctx[key] = value
    return ctx


@app.command("render")
def render_cmd(
    file: Path = Argument(
        ...,
        exists=True,
        readable=True,
        resolve_path=True,
        help="Path to .ymd/.yamd file",
    ),
    var: List[str] = Option(
        [], "--var", "-v", help="KEY=VALUE; use @file to read VALUE from file."
    ),
    vars_json: Optional[Path] = Option(
        None, "--vars-json", help="Path to a JSON file with variables."
    ),
    section: Optional[
        Literal["system", "instructions", "developer", "expected_output", "user"]
    ] = Option(None, "--section", "-s", help="Only print a single section."),
    outdir: Optional[Path] = Option(
        None,
        "--outdir",
        "-o",
        help="Write rendered sections as NAME.md into this directory.",
    ),
    fmt: Literal["json", "md"] = Option(
        "json", "--format", "-f", help="Output format when printing to stdout."
    ),
    no_strict: bool = Option(
        False, "--no-strict", help="Allow missing placeholders (render empty values)."
    ),
):
    """
    Render a YMD prompt file and either print the result or write to files.
    """
    # Load prompt
    try:
        prompt = load(file)
    except Exception as e:
        typer.secho(f"Failed to load {file}: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=2)

    # Build context
    ctx: Dict[str, str] = {}
    if vars_json:
        try:
            ctx.update(json.loads(vars_json.read_text(encoding="utf-8")))
        except Exception as e:
            typer.secho(
                f"Failed to read --vars-json {vars_json}: {e}", fg=typer.colors.RED
            )
            raise typer.Exit(code=2)

    ctx.update(_parse_vars(var))

    # Render
    try:
        rendered = render(prompt, ctx, strict_placeholders=not no_strict)
    except KeyError as e:
        # Missing placeholders in strict mode
        typer.secho(str(e), fg=typer.colors.RED)
        raise typer.Exit(code=2)
    except Exception as e:
        typer.secho(f"Render error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Write to files if requested
    if outdir:
        try:
            outdir.mkdir(parents=True, exist_ok=True)
            keys = [section] if section else list(rendered.keys())
            for key in keys:
                if key not in rendered:
                    # Skip silently if the section doesn't exist on this prompt
                    continue
                (outdir / f"{key}.md").write_text(rendered[key], encoding="utf-8")
            typer.secho(f"Wrote rendered sections to {outdir}", fg=typer.colors.GREEN)
        except Exception as e:
            typer.secho(f"Failed writing to {outdir}: {e}", fg=typer.colors.RED)
            raise typer.Exit(code=2)
        raise typer.Exit(code=0)

    # Print to stdout
    if section:
        typer.echo(rendered.get(section, ""))
        raise typer.Exit(code=0)

    if fmt == "json":
        typer.echo(json.dumps(rendered, ensure_ascii=False, indent=2))
    else:  # md
        # Combine Markdown with H2 headers in a stable order
        parts = []
        order = ["system", "instructions", "developer", "expected_output", "user"]
        for key in order:
            if key in rendered:
                text = rendered[key].rstrip()
                parts.append(f"## {key}\n\n{text}\n")
        typer.echo("\n".join(parts).rstrip())


@app.command("placeholders")
def placeholders_cmd(
    file: Path = Argument(
        ...,
        exists=True,
        readable=True,
        resolve_path=True,
        help="Path to .ymd/.yamd file",
    ),
):
    """
    List all {{placeholders}} referenced in the prompt sections.
    """
    try:
        prompt = load(file)
    except Exception as e:
        typer.secho(f"Failed to load {file}: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=2)

    names = list_placeholders(prompt.sections())
    if names:
        typer.echo(json.dumps(sorted(names), ensure_ascii=False))
    else:
        typer.echo("[]")


# If someone still expects a callable "main", keep a thin wrapper:
def main() -> None:  # pragma: no cover
    app()  # delegates to Typer


if __name__ == "__main__":  # pragma: no cover
    app()
