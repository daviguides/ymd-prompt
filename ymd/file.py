"""
ymd/file.py

Object-oriented loader for `.ymd` (YAML + Markdown + Jinja2) manifests.

Public API:
  - YmdFile.from_path(...)
  - YmdFile.from_raw(...)
  - ymd.join()           # optional convenience to combine sections into one MD

Implementation details (`_parse`, `_render`, `_build_parse_render`) are private.
"""

from pathlib import Path
from typing import Iterable

import yaml
from pydantic import BaseModel

from .models import DefaultMeta, DefaultSections
from .render import render as _engine_render


class YmdFile(BaseModel):
    """
    OO representation of a `.ymd` file.

    Fields:
      - raw       : original YAML text
      - prompt    : parsed `Prompt` model
      - rendered  : dict[str, str] of rendered sections
      - path      : on-disk path (optional)
      - base_dir  : primary search root for includes (usually file directory)
      - root      : optional extra root to append to search paths
      - context   : default render context (optional)
    """

    raw: str | None = None

    meta: DefaultMeta | None = None
    sections: DefaultSections | None = None

    rendered: dict[str, str] | None = None

    path: Path | None = None
    base_dir: Path | None = None
    root: Path | None = None
    context: dict[str, object] | None = None

    # ----------------- public convenience -----------------
    def join(self) -> str:
        """
        Combine rendered sections into a single Markdown document with H2 headers.
        """
        if not self.rendered:
            return ""
        parts: list[str] = []
        order = self.sections.keys()
        for key in order:
            if key in self.rendered:
                text = (self.rendered[key] or "").rstrip()
                parts.append(f"{text}\n")
        return "\n".join(parts).rstrip()

    # ----------------- public factories -------------------
    @classmethod
    def from_path(
        cls,
        path: str | Path,
        *,
        root: str | Path | None = None,
        context: dict[str, object] | None = None,
        include_paths: Iterable[str | Path] | None = None,
        strict_placeholders: bool = True,
    ) -> "YmdFile":
        """
        Read `.ymd` from disk, parse and render before returning.
        """
        p = Path(path)
        file = (Path(root) / p).resolve() if root else p.resolve()
        if not file.exists():
            raise FileNotFoundError(f"YMD file not found: {file}")

        text = file.read_text(encoding="utf-8")
        return cls._build_parse_render(
            raw=text,
            path=file,
            base_dir=file.parent.resolve(),
            root=Path(root).resolve() if root else None,
            context=context,
            include_paths=include_paths,
            strict_placeholders=strict_placeholders,
        )

    @classmethod
    def from_raw(
        cls,
        raw: str,
        *,
        base_dir: Path | None = None,
        root: Path | None = None,
        context: dict[str, object] | None = None,
        include_paths: Iterable[str | Path] | None = None,
        strict_placeholders: bool = True,
    ) -> "YmdFile":
        """
        Create from raw YAML string, parse and render before returning.
        """
        return cls._build_parse_render(
            raw=raw,
            path=None,
            base_dir=base_dir.resolve() if base_dir else None,
            root=root,
            context=context,
            include_paths=include_paths,
            strict_placeholders=strict_placeholders,
        )

    # ----------------- private internals ------------------
    def _parse(self) -> "YmdFile":
        """
        Parse `self.raw` as YAML into a Prompt and attach `_base_dir` for include resolution.
        """
        if self.raw is None:
            raise ValueError(
                "Nothing to parse: `raw` is empty. Provide `raw` or use from_path()."
            )

        try:
            data = yaml.safe_load(self.raw)
        except yaml.YAMLError as e:
            src = getattr(self, "_source", str(self.path) if self.path else "<string>")
            raise ValueError(f"Invalid YAML in {src}: {e}") from e

        if not isinstance(data, dict):
            raise ValueError("YMD root must be a YAML mapping (dict-like).")

        self.meta = DefaultMeta(**data.get("meta", None))
        self.sections = DefaultSections(**data)

        return self

    def _render(
        self,
        *,
        context: dict[str, object] | None = None,
        include_paths: Iterable[str | Path] | None = None,
        strict_placeholders: bool = True,
    ) -> "YmdFile":
        """
        Render the parsed Prompt sections and store in `.rendered`.
        """
        if self.sections is None:
            raise ValueError("Cannot render before parsing.")

        extra_paths: list[str | Path] = []
        if self.root:
            extra_paths.append(self.root)
        if include_paths:
            extra_paths.extend(include_paths)

        merged_ctx = dict(self.context or {})
        merged_ctx.update(context or {})

        self.rendered = _engine_render(
            self.sections,
            merged_ctx,
            strict_placeholders=strict_placeholders,
            searchpath=self.base_dir,
            include_paths=extra_paths or None,
        )

        self.sections = DefaultSections(**self.rendered)
        return self

    @classmethod
    def _build_parse_render(
        cls,
        *,
        raw: str,
        path: Path | None,
        base_dir: Path | None,
        root: Path | None,
        context: dict[str, object] | None,
        include_paths: Iterable[str | Path] | None,
        strict_placeholders: bool,
    ) -> "YmdFile":
        """
        Internal helper to construct an instance, then parse + render.
        """
        inst = cls(
            raw=raw,
            path=path,
            base_dir=base_dir,
            root=root,
            context=context or {},
        )._parse()

        return inst._render(
            context=inst.context,
            include_paths=include_paths,
            strict_placeholders=strict_placeholders,
        )
