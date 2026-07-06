"""Gate 1: unrecoverable-gap tally and categorical trip-rule evaluation.

An *unrecoverable gap* is a hard requirement that is None on the resume AND
absent from the WHD (recoverable=False). The gate PROPOSES a Gap Brief; the
user DISPOSES via the fixed three-option interrogation (plan section 2, Phase C).
The numeric score is never the decision rule — the reasoning is the gate.

Trip rules are CATEGORICAL (how many unrecoverable hard gaps), not a score
threshold. Start permissive (plan section 9); tighten once real Gap Briefs are seen.
"""
from __future__ import annotations

from pathlib import Path

import yaml

DEFAULT_TRIP_RULES = {
    "min_unrecoverable_hard": 2,          # >= this many unrecoverable hard gaps trips
    "unrecoverable_hard_fraction": 1 / 3,  # OR more than this fraction of hard reqs
}


def evaluate(gapmap: dict, trip_rules: dict | None = None) -> dict:
    rules = {**DEFAULT_TRIP_RULES, **(trip_rules or {})}
    reqs = gapmap.get("requirements", [])
    hard = [r for r in reqs if r.get("kind") == "hard"]
    unrecoverable = [
        r for r in hard
        if r["classification"] == "none" and not r.get("recoverable")
    ]
    n = len(unrecoverable)
    hard_total = len(hard)

    reasons = []
    if n >= rules["min_unrecoverable_hard"]:
        reasons.append(
            f"{n} unrecoverable hard gaps (>= {rules['min_unrecoverable_hard']})"
        )
    if hard_total and n > hard_total * rules["unrecoverable_hard_fraction"]:
        reasons.append(
            f"{n}/{hard_total} hard requirements unrecoverable "
            f"(> {rules['unrecoverable_hard_fraction']:.0%})"
        )

    return {
        "unrecoverable_hard_gaps": [r["id"] for r in unrecoverable],
        "unrecoverable_hard_count": n,
        "hard_total": hard_total,
        "tripped": bool(reasons),
        "reasons": reasons,
    }


def evaluate_file(path, trip_rules: dict | None = None) -> dict:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return evaluate(data, trip_rules)


if __name__ == "__main__":
    import json
    import sys

    print(json.dumps(evaluate_file(sys.argv[1]), indent=2))
