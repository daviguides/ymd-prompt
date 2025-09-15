"""
common/utils.py

Utility functions for working with Jinja2 templates in `.pmd` and `.ymd` formats.

This module provides:
- A custom Jinja2 `Environment` (`RelEnv`) that resolves relative includes/imports
  correctly based on the parent template path.
- Functions to create consistent Jinja2 environments with strict or non-strict
  placeholder resolution.
- Functions to statically analyze templates to collect all undeclared variables
  ("placeholders") across a template and its recursive includes/imports.
- Support for multi-root search paths so that templates can import from multiple directories.

Intended usage:
    from common.utils import collect_placeholders_deep_from_template

    placeholders = collect_placeholders_deep_from_template(
        "example.pmd",
        root=Path("prompts/pmd"),
    )
"""

import re
from pathlib import Path
from typing import Iterable

from jinja2 import DebugUndefined, Environment, FileSystemLoader, StrictUndefined
from jinja2.meta import find_undeclared_variables

# ---------------------------------------------------------------------------
# Environment setup
# ---------------------------------------------------------------------------


class RelEnv(Environment):
    """
    Custom Jinja2 Environment that makes `join_path` resolve includes relative
    to the parent template path instead of only the search root.

    This ensures that `{% include "./other.pmd" %}` inside `subdir/main.pmd`
    will correctly resolve to `subdir/other.pmd`.
    """

    def join_path(self, template: str, parent: str) -> str:  # type: ignore[override]
        parent_dir = Path(parent).parent
        return (parent_dir / template).as_posix()


def _make_env(search_paths: Iterable[str | Path], strict: bool = True) -> Environment:
    """
    Create a Jinja2 Environment with relative include support.

    Args:
        search_paths: Iterable of filesystem paths where templates will be searched.
        strict: If True, undefined placeholders raise an error. If False, they are allowed.

    Returns:
        Configured RelEnv instance.
    """
    sp = [str(Path(p)) for p in search_paths]
    return RelEnv(
        loader=FileSystemLoader(sp, followlinks=True),
        undefined=StrictUndefined if strict else DebugUndefined,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


# ---------------------------------------------------------------------------
# Static include/import scanning
# ---------------------------------------------------------------------------

# Regex to detect template dependencies:
# - {% include "path" %}
# - {% from "path" import x %}
# - {% import "path" as m %}
_INCLUDE_LIKE = re.compile(
    r'{%\s*(?:include|from|import)\s+["\']([^"\']+)["\']',
    re.IGNORECASE,
)


def _read_template_text(search_roots: list[Path], name: str) -> str | None:
    """
    Attempt to read a template file given its logical name across multiple roots.

    Args:
        search_roots: List of root directories to search within.
        name: Relative path of the template.

    Returns:
        Template text if found, else None.
    """
    normalized = Path(name)
    for root in search_roots:
        f = (root / normalized).resolve()
        try:
            # Ensure the resolved file is still inside the root (prevent escapes via ../)
            f.relative_to(root.resolve())
        except ValueError:
            continue
        if f.is_file():
            return f.read_text(encoding="utf-8")
    return None


def _resolve_child_name(parent_name: str, child_spec: str) -> str:
    """
    Resolve a child include/import path relative to its parent template name.

    Args:
        parent_name: Path/name of the parent template.
        child_spec: Include/import path as specified in the template.

    Returns:
        Normalized child path as string.
    """
    base = Path(parent_name).parent
    return (base / child_spec).as_posix()


# ---------------------------------------------------------------------------
# Placeholder collection (deep scan)
# ---------------------------------------------------------------------------


def collect_placeholders_deep_from_text(
    text: str,
    *,
    template_name: str = "inline.pmd",
    search_roots: list[Path],
    visited: set[str] | None = None,
) -> set[str]:
    """
    Collect undeclared placeholders from template text, following includes/imports recursively.

    Args:
        text: Template source text.
        template_name: Logical name of the template (used for resolving relative includes).
        search_roots: Directories where included templates will be searched.
        visited: Set of template names already visited (to avoid infinite recursion).

    Returns:
        Set of placeholder names discovered in the template and all its includes/imports.
    """
    env = _make_env(search_roots, strict=False)
    ast = env.parse(text or "")
    names = set(find_undeclared_variables(ast))

    visited = visited or set()
    if template_name in visited:
        return names
    visited.add(template_name)

    # Look for child templates in include/from/import statements
    for m in _INCLUDE_LIKE.finditer(text or ""):
        child = m.group(1)
        # Resolve relative to parent
        child_name = _resolve_child_name(template_name, child)
        # Try to read the child template
        child_text = _read_template_text(search_roots, child_name)
        if child_text is None:
            # Try as absolute logical path (relative to search root)
            child_text = _read_template_text(search_roots, child)
            if child_text is None:
                continue
            child_name = child

        # Recursively scan child
        names |= collect_placeholders_deep_from_text(
            child_text,
            template_name=child_name,
            search_roots=search_roots,
            visited=visited,
        )
    return names


def collect_placeholders_deep_from_template(
    template_name: str,
    *,
    root: Path,
    include_paths: Iterable[str | Path] = (),
) -> set[str]:
    """
    Entry point for collecting placeholders from a template file.

    Args:
        template_name: Relative path of the template to analyze.
        root: Root directory where the template lives.
        include_paths: Additional directories to search for includes/imports.

    Returns:
        Set of placeholder names discovered in the template and all its includes/imports.
    """
    roots = [root.resolve(), *(Path(p).resolve() for p in include_paths)]
    text = _read_template_text(roots, template_name)
    if text is None:
        return set()
    return collect_placeholders_deep_from_text(
        text,
        template_name=template_name,
        search_roots=roots,
        visited=set(),
    )
