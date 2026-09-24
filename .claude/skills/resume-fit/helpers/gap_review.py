"""List the gap-map rows the user reviews before Gate 1 (Phase B.5).

The WHD only knows what the candidate remembered to write down. A requirement
can jog a memory, or reveal that something already in the WHD answers it once
reframed. So before Gate 1 counts anything, the user sees:

- EVERY None (recoverable or not), so each can be confirmed or contested.
  For a recoverable None, "confirm" means the WHD evidence stands and the
  mandatory Add prescription applies.
- Every Partial that is NOT recoverable (nothing stronger in the WHD).

Recoverable Partials are skipped: they already get a mandatory Add prescription.
Hard requirements come first. This helper only selects and orders rows; the
orchestrator asks, and the contract (SKILL.md Phase B.5) says how answers
change the gapmap. Requirement text comes from requirements.yaml when given.
"""
from __future__ import annotations

from pathlib import Path

import yaml

DECISIONS = ("real-gap", "new-evidence", "reframe", "confirm")


def rows(gapmap: dict, requirements: dict | None = None) -> list:
    text_by_id = {}
    for group in ("hard_requirements", "preferred_requirements"):
        for r in (requirements or {}).get(group, []) or []:
            text_by_id[r["id"]] = r.get("text")
    picked = [
        r for r in gapmap.get("requirements", [])
        if r["classification"] == "none"
        or (r["classification"] == "partial" and not r.get("recoverable"))
    ]
    picked.sort(key=lambda r: 0 if r.get("kind") == "hard" else 1)
    return [
        {
            "id": r["id"],
            "kind": r.get("kind"),
            "requirement": text_by_id.get(r["id"]),
            "classification": r["classification"],
            "recoverable": bool(r.get("recoverable")),
            "resume_evidence": r.get("resume_evidence"),
            "whd_evidence": r.get("whd_evidence"),
        }
        for r in picked
    ]


def review_violations(gapmap: dict) -> list:
    """Rows whose recorded review broke the resume-only invariant.

    A new-evidence or reframe answer is WHD evidence, so it must show up as
    `whd_evidence` + `recoverable: true` + a cited `review.anchor`, never as a
    changed `classification`. A row missing those is the signature of an
    upgrade that went into `classification` instead (which the WHD-blind screen
    would then see).
    """
    bad = []
    for r in gapmap.get("requirements", []):
        review = r.get("review") or {}
        if review.get("decision") not in ("new-evidence", "reframe"):
            continue
        missing = [
            f for f, ok in (
                ("recoverable: true", r.get("recoverable") is True),
                ("whd_evidence", bool(r.get("whd_evidence"))),
                ("review.anchor", bool(review.get("anchor"))),
            ) if not ok
        ]
        if missing:
            bad.append({"id": r["id"], "decision": review["decision"], "missing": missing})
    return bad


def rows_files(gapmap_path, requirements_path=None) -> list:
    gm = yaml.safe_load(Path(gapmap_path).read_text(encoding="utf-8"))
    req = (yaml.safe_load(Path(requirements_path).read_text(encoding="utf-8"))
           if requirements_path else None)
    return rows(gm, req)


if __name__ == "__main__":
    import json
    import sys

    from console import utf8_stdout

    utf8_stdout()
    result = rows_files(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(json.dumps({"review_count": len(result), "rows": result}, indent=2, ensure_ascii=False))
