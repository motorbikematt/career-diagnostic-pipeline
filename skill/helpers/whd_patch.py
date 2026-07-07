"""Apply approved WHD reconciliation patches to anchored sections + changelog.

The reconciliation loop PROPOSES; the user DISPOSES (plan section 6). Only patches
the user approved (status: approved) that are durable (whd_worthy: true) are
applied. Each applied patch appends its content to the target anchored section and
writes a date-stamped changelog entry. All other content and anchors are preserved
— the WHD's validation-pass ethos survives because the user ratifies every edit.
"""
from __future__ import annotations

from datetime import date as _date
from pathlib import Path

import yaml

from whd_anchors import ANCHOR_RE


def _section_end(lines, start_idx):
    for j in range(start_idx + 1, len(lines)):
        if ANCHOR_RE.match(lines[j]):
            return j
    return len(lines)


def _find_anchor(lines, anchor_id):
    for i, line in enumerate(lines):
        m = ANCHOR_RE.match(line)
        if m and m.group("id") == anchor_id:
            return i
    return None


def _insert_at_section_end(lines, anchor_idx, new_lines):
    end = _section_end(lines, anchor_idx)
    insert_at = end
    while insert_at - 1 > anchor_idx and lines[insert_at - 1].strip() == "":
        insert_at -= 1
    lines[insert_at:insert_at] = new_lines
    return lines


def _append_changelog(text: str, entry: str) -> str:
    lines = text.splitlines()
    cl = _find_anchor(lines, "changelog")
    bullet = f"- {entry}"
    if cl is None:
        lines += ["", "<!-- anchor: changelog -->", "# Changelog", "", bullet]
    else:
        lines = _insert_at_section_end(lines, cl, [bullet])
    return "\n".join(lines)


def apply_patch(text: str, anchor_id: str, content: str, changelog_note: str,
                on: str | None = None) -> str:
    on = on or _date.today().isoformat()
    lines = text.splitlines()
    target = _find_anchor(lines, anchor_id)
    if target is None:
        raise KeyError(f"anchor not found: {anchor_id}")
    lines = _insert_at_section_end(lines, target, content.splitlines() or [content])
    return _append_changelog("\n".join(lines), f"{on} - {changelog_note}")


def apply_patches(text: str, patches: list, on: str | None = None):
    applied = []
    for p in patches:
        if p.get("status") != "approved" or not p.get("whd_worthy"):
            continue
        text = apply_patch(text, p["target_anchor"], p["content"],
                           p.get("note", "reconciliation patch"), on)
        applied.append(p["target_anchor"])
    return text, applied


def apply_file(whd_path, patches_path, on: str | None = None):
    text = Path(whd_path).read_text(encoding="utf-8")
    patches = (yaml.safe_load(Path(patches_path).read_text(encoding="utf-8")) or {}).get("patches", [])
    new_text, applied = apply_patches(text, patches, on)
    Path(whd_path).write_text(new_text, encoding="utf-8")
    return applied


if __name__ == "__main__":
    import json
    import sys

    on = sys.argv[3] if len(sys.argv) > 3 else None
    applied = apply_file(sys.argv[1], sys.argv[2], on)
    print(json.dumps({"applied_to": applied}, indent=2))
