"""
ymd/render.py

Render `.ymd` (YAML + Markdown + Jinja2) prompt manifests.

This module exposes a single main entry point:

    render(prompt, context, ...)

which takes a parsed `prompt` object (with `.sections()`), applies Jinja2
rendering with proper include resolution, and returns a dictionary of rendered
sections.

Features:
- Supports chained relative includes (`A -> B -> ./C`) using a custom Jinja2 environment.
- Provides `include_section(path, section)` global function to pull only one section
  from another `.ymd` file.
- Supports strict or loose placeholder validation.
"""

from pathlib import Path
from typing import Iterable

from jinja2 import TemplateNotFound

from common.utils import _make_env


def render(
    prompt,
    context: dict[str, object],
    *,
    strict_placeholders: bool = True,
    searchpath: Path | None = None,
    include_paths: Iterable[str | Path] | None = None,
) -> dict[str, str]:
    """
    Render all sections of a YMD prompt using Jinja2.

    Args:
        prompt: An object exposing `.sections()` or a plain string.
        context: Mapping of variables to inject into templates.
        strict_placeholders: If True, missing variables raise errors.
        searchpath: Root directory for template includes (defaults to prompt._base_dir).
        include_paths: Additional directories to search for templates.

    Returns:
        A dict mapping section names (system, instructions, etc.) to rendered text.
    """
    sections = _get_sections(prompt)
    base_dir = _resolve_base_dir(prompt, searchpath)
    search_paths = _build_search_paths(base_dir, include_paths)

    env = _make_env(search_paths, strict_placeholders)
    _register_include_section(env, base_dir)

    return _render_sections(env, sections, context)


# ---------------------------------------------------------------------------
# Helpers (declared in order of call from render)
# ---------------------------------------------------------------------------


def _get_sections(prompt) -> dict[str, str]:
    """
    Extract sections from the given prompt object.

    - If the object has `.sections()`, call it.
    - Otherwise, treat it as a plain string under the key "source".
    """
    return (
        prompt.model_dump()
        #   if hasattr(prompt, "sections") else {"source": str(prompt)}
    )


def _resolve_base_dir(prompt, searchpath: Path | None) -> Path | None:
    """
    Determine the base directory for relative includes.

    Priority:
    1. Explicit `searchpath` argument.
    2. `prompt._base_dir` if available.
    3. None if neither is provided.
    """
    if searchpath:
        return Path(searchpath).resolve()
    if hasattr(prompt, "_base_dir") and getattr(prompt, "_base_dir", None):
        return Path(prompt._base_dir).resolve()
    return None


def _build_search_paths(
    base_dir: Path | None, include_paths: Iterable[str | Path] | None
) -> list[Path]:
    """
    Build the list of search paths for Jinja2 FileSystemLoader.

    Includes:
    - The base directory if provided.
    - Any additional include paths.
    """
    search: list[Path] = []
    if base_dir:
        search.append(base_dir)
    if include_paths:
        search.extend(Path(p).resolve() for p in include_paths)
    return search


def _register_include_section(env, base_dir: Path | None) -> None:
    """
    Register the `include_section` helper in the Jinja2 environment.

    Usage in templates:
        {{ include_section("other.ymd", "system") }}

    Args:
        env: Jinja2 environment.
        base_dir: Base directory for resolving relative paths.
    """

    def _include_section(path: str, section: str) -> str:
        target = Path(path)
        if base_dir and not target.is_absolute():
            target = (base_dir / target).resolve()

        from .load import load as _load  # Local import to avoid circular dependency

        try:
            other = _load(target)
        except FileNotFoundError as e:
            raise TemplateNotFound(
                f"YMD not found for include_section: {target}"
            ) from e
        return other.sections().get(section, "")

    env.globals["include_section"] = _include_section


def _render_sections(
    env, sections: dict[str, str], context: dict[str, object]
) -> dict[str, str]:
    """
    Render all sections with the given environment and context.

    Each section string is compiled separately with `from_string`.
    """
    rendered: dict[str, str] = {}
    for key, text in sections.items():
        template = env.from_string(text or "")
        rendered[key] = template.render(**(context or {}))
    return rendered
