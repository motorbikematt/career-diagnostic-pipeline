"""Deterministic score arithmetic from gapmap.yaml.

The model classifies each requirement (match/partial/none); Python computes the
weighted score. This eliminates LLM arithmetic errors and the tokens spent
"showing the math". "The score derives from the map."
"""
from __future__ import annotations

from pathlib import Path

import yaml

FACTOR = {"match": 1.0, "partial": 0.5, "none": 0.0}


def _weighted(items) -> float:
    total_weight = sum(r["weight"] for r in items)
    if total_weight == 0:
        return 0.0
    earned = sum(r["weight"] * FACTOR[r["classification"]] for r in items)
    return earned / total_weight


def compute(gapmap: dict) -> dict:
    reqs = gapmap.get("requirements", [])
    hard = [r for r in reqs if r.get("kind") == "hard"]
    pref = [r for r in reqs if r.get("kind") == "preferred"]

    counts = {c: sum(1 for r in reqs if r["classification"] == c) for c in FACTOR}
    recoverable_gaps = [
        r["id"] for r in reqs if r["classification"] == "none" and r.get("recoverable")
    ]
    unrecoverable_hard = [
        r["id"]
        for r in hard
        if r["classification"] == "none" and not r.get("recoverable")
    ]

    return {
        "paper_score": round(_weighted(reqs) * 100),
        "hard_score": round(_weighted(hard) * 100),
        "preferred_score": round(_weighted(pref) * 100),
        "counts": counts,
        "hard_total": len(hard),
        "preferred_total": len(pref),
        "recoverable_gaps": recoverable_gaps,
        "recoverable_gaps_count": len(recoverable_gaps),
        "unrecoverable_hard_gaps": unrecoverable_hard,
        "unrecoverable_hard_count": len(unrecoverable_hard),
    }


def compute_file(path) -> dict:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return compute(data)


if __name__ == "__main__":
    import json
    import sys

    print(json.dumps(compute_file(sys.argv[1]), indent=2))
