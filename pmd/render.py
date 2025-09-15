"""
pmd/render.py

Render `.pmd` (Prompt Markdown + Jinja2) partial templates.

This module exposes a single main entry point:

    render(template_name=..., text=..., ...)

Features:
- If `template_name` is provided, the template is resolved via Jinja2's
  FileSystemLoader, with support for chained relative includes.
- If only `text` is provided, falls back to `from_string` (useful for tests).
- Supports strict or loose placeholder validation.
"""

from pathlib import Path
from typing import Iterable

from jinja2 import TemplateNotFound

from common.utils import _make_env


def render(
    *,
    template_name: str | None = None,
    text: str | None = None,
    context: dict | None = None,
    base_dir: str | Path | None = None,
    include_paths: Iterable[str | Path] | None = None,
    strict_placeholders: bool = True,
) -> str:
    """
    Render a PMD template (Markdown + Jinja2).

    Args:
        template_name: File name of the template to render (preferred for includes).
        text: Raw template string (used only when `template_name` is not provided).
        context: Dictionary of variables to inject into the template.
        base_dir: Base directory for resolving relative includes.
        include_paths: Additional directories to search for templates.
        strict_placeholders: If True, missing variables raise errors.

    Returns:
        The rendered text.
    """
    ctx = context or {}
    search_paths = _build_search_paths(base_dir, include_paths)
    env = _make_env(search_paths, strict_placeholders)

    if template_name:
        return _render_from_template(env, template_name, ctx, search_paths)
    return _render_from_string(env, text, ctx)


# ---------------------------------------------------------------------------
# Helpers (declared in order of call from render)
# ---------------------------------------------------------------------------


def _build_search_paths(
    base_dir: str | Path | None, include_paths: Iterable[str | Path] | None
) -> list[Path]:
    """
    Construct search paths for the Jinja2 FileSystemLoader.

    - Starts with the base_dir (default: current directory).
    - Appends any additional include paths.
    """
    base = Path(base_dir or ".").resolve()
    search: list[Path] = [base]
    if include_paths:
        search.extend(Path(p).resolve() for p in include_paths)
    return search


def _render_from_template(
    env, template_name: str, ctx: dict, search_paths: list[Path]
) -> str:
    """
    Render a template file by name, resolving includes relative to its location.

    Raises:
        TemplateNotFound: if the template cannot be resolved in the search paths.
    """
    try:
        tmpl = env.get_template(template_name)
    except TemplateNotFound as e:
        paths_str = ", ".join(str(p) for p in search_paths)
        raise TemplateNotFound(
            f"{template_name!r} not found. Search paths: {paths_str}"
        ) from e
    return tmpl.render(**ctx)


def _render_from_string(env, text: str | None, ctx: dict) -> str:
    """
    Render a raw string template (no include resolution guarantees).
    """
    tmpl = env.from_string(text or "")
    return tmpl.render(**ctx)
