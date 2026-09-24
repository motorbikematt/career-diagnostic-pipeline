"""WHD file I/O shared by every helper that rewrites the WHD.

Two jobs, kept in one place so no writer gets them subtly different:

1. Preserve line endings. The real WHD uses CRLF; Path.read_text() hands back
   "\n" and Path.write_text() on Windows writes os.linesep. A writer that ignores
   this silently converts the whole file on its first edit. `read_whd` returns
   the text plus the file's EOL, and `write_whd` restores it.
2. Set a front-matter key (`canary`, `hard_no_reviewed`) by rewriting only that
   line, so comments and key order in the front-matter survive.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml


def read_whd(path) -> tuple[str, str]:
    raw = Path(path).read_bytes().decode("utf-8")
    eol = "\r\n" if "\r\n" in raw else "\n"
    return raw.replace("\r\n", "\n"), eol


def write_whd(path, text: str, eol: str = "\n") -> None:
    Path(path).write_bytes(text.replace("\n", eol).encode("utf-8"))


def front_matter_end(lines: list) -> int:
    """Index of the closing '---' line; raises if there is no front-matter."""
    if not lines or lines[0].strip() != "---":
        raise ValueError("WHD has no front-matter")
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return i
    raise ValueError("WHD front-matter is not closed")


def read_front_matter(text: str) -> dict:
    lines = text.split("\n")
    end = front_matter_end(lines)
    return yaml.safe_load("\n".join(lines[1:end])) or {}


def set_front_matter_key(text: str, key: str, value: str) -> str:
    """Replace `key: ...` in the front-matter, or append it before the closing
    '---'. `value` is written double-quoted."""
    lines = text.split("\n")
    end = front_matter_end(lines)
    new_line = f'{key}: "{value}"'
    pattern = re.compile(rf"^{re.escape(key)}:")
    for i in range(1, end):
        if pattern.match(lines[i]):
            lines[i] = new_line
            return "\n".join(lines)
    lines.insert(end, new_line)
    return "\n".join(lines)
