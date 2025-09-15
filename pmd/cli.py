# pmd/cli.py
import json
from pathlib import Path
import typer
from .load import load as load_pmd
from .render import render as render_pmd

app = typer.Typer(help="Render PMD (Prompt Markdown + Jinja2) files")


def _parse_vars(values: list[str] | None) -> dict[str, str]:
    ctx: dict[str, str] = {}
    for item in values or []:
        if "=" not in item:
            raise typer.Exit(code=2)
        k, v = item.split("=", 1)
        ctx[k] = Path(v[1:]).read_text(encoding="utf-8") if v.startswith("@") else v
    return ctx


@app.command("render")
def render_cmd(
    file: Path = typer.Argument(..., exists=True, resolve_path=True),
    var: list[str] = typer.Option([], "--var", "-v"),
    vars_json: Path | None = typer.Option(None, "--vars-json"),
    include: list[Path] = typer.Option(
        [], "--include", "-I", help="Additional include paths"
    ),
    no_strict: bool = typer.Option(
        False, "--no-strict", help="Allow missing placeholders"
    ),
    out: Path | None = typer.Option(
        None, "--out", help="Write rendered output to a file"
    ),
):
    """
    Render a .pmd file. If --include or --no-strict are provided, we render explicitly
    to honor those options; otherwise we rely on pmd.load() which already renders.
    """
    ctx: dict[str, str] = {}
    if vars_json:
        ctx.update(json.loads(vars_json.read_text(encoding="utf-8")))
    ctx.update(_parse_vars(var))

    if include or no_strict:
        # explicit path to honor flags
        text = file.read_text(encoding="utf-8")
        result = render_pmd(
            text=text,
            context=ctx,
            base_dir=file.parent,
            include_paths=include,
            strict_placeholders=not no_strict,
        )
    else:
        pmd = load_pmd(file, context=ctx)
        result = pmd.content or render_pmd(
            text=pmd.raw or "", context=ctx, base_dir=pmd.base_dir
        )

    if out:
        out.write_text(result, encoding="utf-8")
        typer.echo(f"Wrote: {out}")
    else:
        typer.echo(result)


if __name__ == "__main__":
    app()
