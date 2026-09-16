"""WHD anchor resolution.

Anchors are HTML comments the WHD restructure inserts:
    <!-- anchor: role-2 -->
    <!-- anchor: role-2.project-1 -->
    <!-- anchor: voice-sample -->
Lets subagents and patches retrieve a section by id without reading the whole
document, and lets prescriptions cite machine-resolvable locations.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

ANCHOR_RE = re.compile(r"^<!--\s*anchor:\s*(?P<id>[A-Za-z0-9_.\-]+)\s*-->\s*$")


def parse_front_matter(text: str) -> dict:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}
    return yaml.safe_load("\n".join(lines[1:end])) or {}


def role_index(text: str) -> list:
    return parse_front_matter(text).get("roles", [])


def list_anchors(text: str) -> list:
    out = []
    for line in text.splitlines():
        m = ANCHOR_RE.match(line)
        if m:
            out.append(m.group("id"))
    return out


def resolve_anchor(text: str, anchor_id: str) -> str:
    """Return the section body from the given anchor up to (not including) the
    next anchor marker. Raises KeyError if the anchor is absent."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        m = ANCHOR_RE.match(line)
        if m and m.group("id") == anchor_id:
            start = i + 1
            break
    if start is None:
        raise KeyError(f"anchor not found: {anchor_id}")
    end = len(lines)
    for j in range(start, len(lines)):
        if ANCHOR_RE.match(lines[j]):
            end = j
            break
    return "\n".join(lines[start:end]).strip("\n")


def resolve_file(path, anchor_id: str) -> str:
    return resolve_anchor(Path(path).read_text(encoding="utf-8"), anchor_id)


if __name__ == "__main__":
    import sys

    print(resolve_file(sys.argv[1], sys.argv[2]))
