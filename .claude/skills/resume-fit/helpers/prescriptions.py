"""Enforce the mandatory prescriptions rule (v1 Stage 3, preserved verbatim):

"Every Recoverable Gap identified in Stage 1 (items that are None/Partial on
resume but present in Work History) must have a corresponding Add prescription
below, citing the specific Work History section. No Recoverable Gap may be left
unaddressed."

This turns that rule into a code guarantee, not a prompt request: the finishing
loop cannot proceed while a recoverable gap has no covering Add prescription.

It also rejects AMBIGUOUS targets. Each prescription's `target` must name one
location. A target offering alternatives ("under the Summary or as a new early
entry") forces the drafting step to guess, and a wrong guess once put an old
role at the top of a resume.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

# Words that signal a target is offering a choice of locations.
_AMBIGUOUS = re.compile(r"\b(or|either|alternatively)\b", re.IGNORECASE)


def recoverable_gap_ids(gapmap: dict) -> list:
    return [r["id"] for r in gapmap.get("requirements", []) if r.get("recoverable")]


def ambiguous_targets(prescriptions: dict) -> list:
    return [
        p.get("target", "")
        for p in prescriptions.get("prescriptions", [])
        if _AMBIGUOUS.search(p.get("target") or "")
    ]


def check_coverage(prescriptions: dict, gapmap: dict) -> dict:
    needed = recoverable_gap_ids(gapmap)
    adds = [p for p in prescriptions.get("prescriptions", []) if p.get("type") == "add"]
    covered, uncovered = [], []
    for gid in needed:
        ok = any(gid in (p.get("closes") or []) and p.get("source") for p in adds)
        (covered if ok else uncovered).append(gid)
    ambiguous = ambiguous_targets(prescriptions)
    return {
        "needed": needed,
        "covered": covered,
        "uncovered": uncovered,
        "ambiguous_targets": ambiguous,
        "ok": not uncovered and not ambiguous,
    }


def check_files(prescriptions_path, gapmap_path) -> dict:
    pres = yaml.safe_load(Path(prescriptions_path).read_text(encoding="utf-8"))
    gm = yaml.safe_load(Path(gapmap_path).read_text(encoding="utf-8"))
    return check_coverage(pres, gm)


if __name__ == "__main__":
    import json
    import sys

    result = check_files(sys.argv[1], sys.argv[2])
    print(json.dumps(result, indent=2))
    if result["uncovered"]:
        print(f"UNADDRESSED RECOVERABLE GAPS: {result['uncovered']}")
    if result["ambiguous_targets"]:
        print("AMBIGUOUS TARGETS (name exactly one location): "
              f"{result['ambiguous_targets']}")
    if not result["ok"]:
        sys.exit(1)
