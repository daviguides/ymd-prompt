from __future__ import annotations
from typing import Dict, Iterable, Set, Mapping
import re
from jinja2 import Environment, BaseLoader, StrictUndefined

_PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_\.:-]*)\s*\}\}")

def list_placeholders(source: str | Mapping[str, str] | Iterable[str]) -> Set[str]:
    def scan_one(s: str) -> Set[str]:
        return set(m.group(1) for m in _PLACEHOLDER_RE.finditer(s or ""))

    names: Set[str] = set()
    if isinstance(source, str):
        names |= scan_one(source)
    elif isinstance(source, Mapping):
        for v in source.values():
            if isinstance(v, str):
                names |= scan_one(v)
    else:
        for v in source:
            if isinstance(v, str):
                names |= scan_one(v)
    return names

def render(prompt, context: Dict[str, object], *, strict_placeholders: bool = True) -> Dict[str, str]:
    sections = prompt.sections() if hasattr(prompt, "sections") else dict(source=prompt)
    needed = list_placeholders(sections)

    if strict_placeholders and not needed.issubset(context.keys()):
        missing = sorted(needed - set(context.keys()))
        raise KeyError(f"Missing placeholders: {missing}")

    env = Environment(loader=BaseLoader(), undefined=StrictUndefined if strict_placeholders else None,
                      autoescape=False, trim_blocks=True, lstrip_blocks=True)
    rendered: Dict[str, str] = {}
    for key, text in sections.items():
        template = env.from_string(text)
        rendered[key] = template.render(**context)
    return rendered
