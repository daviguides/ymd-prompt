"""
pmd/load.py

Load `.pmd` (Prompt Markdown + Jinja2) files.

Exposes:
- load(path, context, root): load from disk and render immediately.
- loads(raw, base_dir, root, context): load from raw string.

Returns a PmdFile containing both raw and rendered text.
"""

from __future__ import annotations
from pathlib import Path

from pydantic import BaseModel
from .render import render


class PmdFile(BaseModel):
    """Representation of a PMD file: both raw and rendered content."""

    raw: str | None = None
    content: str | None = None
    base_dir: Path | None = None
    root: Path | None = None


def load(
    path: str | Path,
    context: dict | None = None,
    *,
    root: str | Path | None = None,
) -> PmdFile:
    """
    Load a .pmd file from disk, render it, and return a PmdFile.

    Args:
        path: Path to the .pmd file.
        context: Variables to pass into the Jinja2 render.
        root: Optional root directory for resolving includes. If not provided,
              defaults to the file's parent directory.
    """
    if root:
        normalized = Path(path)
        file = (root / normalized).resolve()
    else:
        file = Path(path).resolve()

    root_dir = Path(root).resolve() if root else file.parent

    raw = file.read_text(encoding="utf-8")

    return loads(
        raw=raw,
        base_dir=file.parent,
        root=root_dir,
        context=context,
    )


def loads(
    raw: str,
    base_dir: Path | None = None,
    *,
    root: Path | None = None,
    context: dict | None = None,
) -> PmdFile:
    """
    Load a .pmd file from raw text and render it.

    Args:
        raw: Raw template string.
        base_dir: Directory of the file (for relative includes).
        root: Root directory for resolving templates (higher-level search path).
        context: Variables to inject.

    Returns:
        A PmdFile with raw and rendered content.
    """
    content = render(
        text=raw,
        base_dir=base_dir,
        include_paths=[root] if root else None,
        context=context,
    )

    return PmdFile(
        raw=raw,
        content=content,
        base_dir=base_dir,
        root=root,
    )
