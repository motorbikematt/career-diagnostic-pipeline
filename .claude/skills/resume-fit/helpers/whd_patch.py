"""Apply approved WHD reconciliation patches to anchored sections + changelog.

The reconciliation loop PROPOSES; the user DISPOSES (plan section 6). Only patches
the user approved (status: approved) that are durable (whd_worthy: true) are
applied. All other content and anchors are preserved; the WHD's
validation-pass ethos survives because the user ratifies every edit.

Two ways a patch lands:
- fact | evidence | hard-no: APPEND `content` to the end of the target section.
- correction: REPLACE `old` with `content` inside the target section. `old` must
  occur exactly once in that section, or the patch fails loudly (naming where
  the text does occur). The body keeps only current facts; the changelog entry
  records the old and new text, since the data plane has no other history.
  After a replace, any remaining copies of `old` elsewhere in the WHD are
  reported so the user can correct them too.

A section runs from its anchor to the NEXT anchor, so `nimbus-labs` ends where
`nimbus-labs.p1` begins. The Voice Sample and the changelog are never
patch targets.
"""
from __future__ import annotations

from datetime import date as _date

from whd_anchors import ANCHOR_RE
from whd_io import read_whd, write_whd

PROTECTED_ANCHORS = {"voice-sample", "changelog"}


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


def _check_target(lines, anchor_id):
    if anchor_id in PROTECTED_ANCHORS:
        raise ValueError(f"anchor {anchor_id!r} is protected and is never a patch target")
    target = _find_anchor(lines, anchor_id)
    if target is None:
        raise KeyError(f"anchor not found: {anchor_id}")
    return target


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


def _sections(lines):
    """Yield (anchor_id, start, end) for every anchored section."""
    for i, line in enumerate(lines):
        m = ANCHOR_RE.match(line)
        if m:
            yield m.group("id"), i, _section_end(lines, i)


def anchors_containing(text: str, needle: str, skip=("changelog",)) -> list:
    lines = text.splitlines()
    return [
        aid for aid, s, e in _sections(lines)
        if aid not in skip and needle in "\n".join(lines[s:e])
    ]


def apply_patch(text: str, anchor_id: str, content: str, changelog_note: str,
                on: str | None = None) -> str:
    on = on or _date.today().isoformat()
    lines = text.splitlines()
    target = _check_target(lines, anchor_id)
    lines = _insert_at_section_end(lines, target, content.splitlines() or [content])
    return _append_changelog("\n".join(lines), f"{on} - {changelog_note}")


def apply_correction(text: str, anchor_id: str, old: str, new: str,
                     changelog_note: str, on: str | None = None,
                     prompted_by: str | None = None) -> tuple[str, list]:
    """Replace `old` with `new` inside one section. Returns (text, anchors that
    still contain `old` elsewhere)."""
    if not old:
        raise ValueError("a correction patch needs a non-empty `old`")
    on = on or _date.today().isoformat()
    lines = text.splitlines()
    target = _check_target(lines, anchor_id)
    end = _section_end(lines, target)
    section = "\n".join(lines[target:end])
    count = section.count(old)
    if count != 1:
        found_in = anchors_containing(text, old)
        raise ValueError(
            f"correction `old` text matched {count} times in {anchor_id!r} (must be exactly 1); "
            f"it occurs in: {found_in or 'no section'}"
        )
    lines[target:end] = section.replace(old, new, 1).split("\n")
    run = f"; run: {prompted_by}" if prompted_by else ""
    entry = f"{on} - {changelog_note} (corrected in {anchor_id}: was \"{old}\", now \"{new}\"{run})"
    out = _append_changelog("\n".join(lines), entry)
    return out, anchors_containing(out, old)


def apply_patches(text: str, patches: list, on: str | None = None):
    """Apply approved + durable patches. Returns (text, applied, leftovers) where
    leftovers maps a correction's target anchor to other anchors still holding
    its old text. Each applied patch dict is marked `status: applied` in place,
    so a later pass (Phase B.5 / Gate 1 apply immediately, Phase H applies the
    whole queue) never writes it twice."""
    applied, leftovers = [], {}
    for p in patches:
        if p.get("status") != "approved" or not p.get("whd_worthy"):
            continue
        note = p.get("note", "reconciliation patch")
        if p.get("kind") == "correction":
            text, remaining = apply_correction(
                text, p["target_anchor"], p.get("old", ""), p["content"], note, on,
                p.get("prompted_by"),
            )
            if remaining:
                leftovers[p["target_anchor"]] = remaining
        else:
            text = apply_patch(text, p["target_anchor"], p["content"], note, on)
        applied.append(p["target_anchor"])
    for p in patches:
        if p.get("status") == "approved" and p.get("whd_worthy"):
            p["status"] = "applied"
    return text, applied, leftovers


def apply_file(whd_path, patches_path, on: str | None = None):
    import yaml
    from pathlib import Path

    text, eol = read_whd(whd_path)
    doc = yaml.safe_load(Path(patches_path).read_text(encoding="utf-8")) or {}
    patches = doc.get("patches", [])
    new_text, applied, leftovers = apply_patches(text, patches, on)
    if not applied:
        return applied, leftovers
    write_whd(whd_path, new_text + ("\n" if text.endswith("\n") else ""), eol)
    # Only after the WHD write succeeds: record which patches landed.
    Path(patches_path).write_text(
        yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return applied, leftovers


if __name__ == "__main__":
    import json
    import sys

    on = sys.argv[3] if len(sys.argv) > 3 else None
    applied, leftovers = apply_file(sys.argv[1], sys.argv[2], on)
    print(json.dumps({"applied_to": applied, "old_text_still_in": leftovers}, indent=2))
    if leftovers:
        print("CHECK: corrected text still appears in other sections; propose corrections there too.")
