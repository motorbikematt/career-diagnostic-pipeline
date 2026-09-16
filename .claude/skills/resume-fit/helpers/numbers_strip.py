"""Deterministic numbers strip for the report headline (never spend a token).

Assembles the four headline numbers from the run's artifacts so the report can
never drift from the math (plan section 3, "Numbers strip"):
  paper_score, recoverable_gaps_count (from gapmap via score.py),
  escalation_likelihood (from screen.yaml), evidence_confidence (from scd.yaml).
"""
from __future__ import annotations

from pathlib import Path

import yaml

import score


def assemble(run_dir) -> dict:
    run = Path(run_dir)
    gm = yaml.safe_load((run / "gapmap.yaml").read_text(encoding="utf-8"))
    s = score.compute(gm)
    out = {
        "paper_score": s["paper_score"],
        "recoverable_gaps_count": s["recoverable_gaps_count"],
        "escalation_likelihood": None,
        "evidence_confidence": None,
    }
    screen_p = run / "screen.yaml"
    if screen_p.exists():
        screen = yaml.safe_load(screen_p.read_text(encoding="utf-8"))
        out["escalation_likelihood"] = screen.get("escalation_likelihood")
    scd_p = run / "scd.yaml"
    if scd_p.exists():
        scd = yaml.safe_load(scd_p.read_text(encoding="utf-8"))
        out["evidence_confidence"] = scd.get("evidence_confidence")
    return out


if __name__ == "__main__":
    import json
    import sys

    print(json.dumps(assemble(sys.argv[1]), indent=2))
