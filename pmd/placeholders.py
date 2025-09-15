from __future__ import annotations
import re
from typing import Set

_VAR = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_\.]*)")

def list_placeholders(text: str) -> Set[str]:
    """
    Return a set of variable names referenced with {{ var }} (best-effort).
    """
    return set(m.group(1) for m in _VAR.finditer(text or ""))
