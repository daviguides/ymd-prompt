"""
ymd/load.py

Functional facade to load `.ymd` files into a `Prompt` model.
For OO usage, see `ymd/file.py` (YmdFile).
"""

from pathlib import Path

from .file import YmdFile


def load(path: str | Path) -> YmdFile:
    """
    Load a YMD file from disk and return a validated Prompt model.
    """
    # return YmdFile.from_path(path).sections  # type: ignore[return-value]
    return YmdFile.from_path(path)


def loads(text: str, *, source: str | None = None) -> YmdFile:
    """
    Load a YMD document from a raw string and return a validated Prompt model.
    """
    y = YmdFile.from_raw(text)
    if source:
        setattr(y, "_source", source)
    # return y.sections  # type: ignore[return-value]
    return y
