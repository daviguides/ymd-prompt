"""
pmd/load.py

Object-oriented loader for `.pmd` (Prompt Markdown + Jinja2) files.

You can:
- Create from disk: PmdFile.from_path(path, root, context)
- Create from raw text: PmdFile.from_raw(raw, base_dir, root, context)
- Or instantiate directly: PmdFile(path, root, context).load()
"""

from pathlib import Path
from typing import Self

from pydantic import BaseModel

from .render import render


class PmdFile(BaseModel):
    """Representation of a PMD file: raw + rendered content + location info."""

    raw: str | None = None
    content: str | None = None
    path: Path | None = None
    base_dir: Path | None = None
    root: Path | None = None
    context: dict | None = None

    # ----------------------------
    # Constructors
    # ----------------------------
    @classmethod
    def from_path(
        cls,
        path: str | Path,
        *,
        root: str | Path | None = None,
        context: dict | None = None,
    ) -> Self:
        """
        Factory: load a .pmd file from disk and render immediately.
        """
        p = Path(path)
        if root:
            file = (Path(root) / p).resolve()
        else:
            file = p.resolve()

        root_dir = Path(root).resolve() if root else file.parent
        raw = file.read_text(encoding="utf-8")

        return cls(
            raw=raw,
            path=file,
            base_dir=file.parent,
            root=root_dir,
            context=context,
        ).load()

    @classmethod
    def from_raw(
        cls,
        raw: str,
        *,
        base_dir: Path | None = None,
        root: Path | None = None,
        context: dict | None = None,
    ) -> Self:
        """
        Factory: create from raw text and render immediately.
        """
        return cls(
            raw=raw,
            base_dir=base_dir,
            root=root,
            context=context,
        ).load()

    # ----------------------------
    # Instance method
    # ----------------------------
    def load(self) -> Self:
        """
        Render the file (from self.raw) with Jinja2 and store in `self.content`.
        """
        if self.raw is None:
            if not self.path:
                raise ValueError("No raw text or path available to load PMD file.")
            self.raw = self.path.read_text(encoding="utf-8")

        self.content = render(
            text=self.raw,
            base_dir=self.base_dir,
            include_paths=[self.root] if self.root else None,
            context=self.context,
        )
        return self
