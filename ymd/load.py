from __future__ import annotations
from pathlib import Path
from typing import Union
import yaml
from .models import Prompt

PathLike = Union[str, Path]

def load(path: PathLike) -> Prompt:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"YMD file not found: {p}")
    text = p.read_text(encoding="utf-8")
    return loads(text, source=str(p))

def loads(text: str, *, source: str | None = None) -> Prompt:
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        msg = f"Invalid YAML in {source or '<string>'}: {e}"
        raise ValueError(msg) from e

    if not isinstance(data, dict):
        raise ValueError("YMD root must be a YAML mapping (dict-like).")

    return Prompt(**data)
