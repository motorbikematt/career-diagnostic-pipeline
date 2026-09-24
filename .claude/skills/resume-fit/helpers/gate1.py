"""Gate 1: unrecoverable-gap tally, location check, and categorical trip rules.

An *unrecoverable gap* is a hard requirement that is None on the resume AND
absent from the WHD (recoverable=False). A *weak Partial* is a hard requirement
that is Partial on the resume with nothing stronger in the WHD; it counts as
half an unrecoverable gap, matching the 0.5 weight score.py gives a Partial.
The gate PROPOSES a Gap Brief; the user DISPOSES via the fixed three-option
interrogation (plan section 2, Phase C). The numeric score is never the
decision rule: the reasoning is the gate.

Trip rules are CATEGORICAL, not a score threshold. The gap rules use the
weighted tally (None = 1, weak Partial = 0.5). A location trip
(location_gate.py) fires on its own, whatever the gap tally; a location
open-question never trips but must reach the report's Open Questions, which is
why the result is written to the run folder with --out.
"""
from __future__ import annotations

from pathlib import Path

import yaml

DEFAULT_TRIP_RULES = {
    "min_unrecoverable_hard": 2,          # weighted tally >= this trips
    "unrecoverable_hard_fraction": 1 / 3,  # OR weighted tally > this fraction of hard reqs
}
WEAK_PARTIAL_WEIGHT = 0.5


def evaluate(gapmap: dict, trip_rules: dict | None = None, location: dict | None = None) -> dict:
    rules = {**DEFAULT_TRIP_RULES, **(trip_rules or {})}
    from gap_review import review_violations

    violations = review_violations(gapmap)
    if violations:
        raise ValueError(
            "gap-review upgrades must set whd_evidence + recoverable + review.anchor, "
            f"never change classification: {violations}"
        )
    reqs = gapmap.get("requirements", [])
    hard = [r for r in reqs if r.get("kind") == "hard"]
    unrecoverable = [
        r for r in hard
        if r["classification"] == "none" and not r.get("recoverable")
    ]
    weak_partial = [
        r for r in hard
        if r["classification"] == "partial" and not r.get("recoverable")
    ]
    n = len(unrecoverable)
    tally = n + WEAK_PARTIAL_WEIGHT * len(weak_partial)
    hard_total = len(hard)

    reasons = []
    if tally >= rules["min_unrecoverable_hard"]:
        reasons.append(
            f"{tally:g} weighted unrecoverable hard gaps (>= {rules['min_unrecoverable_hard']}): "
            f"{n} None, {len(weak_partial)} weak Partial"
        )
    if hard_total and tally > hard_total * rules["unrecoverable_hard_fraction"]:
        reasons.append(
            f"{tally:g}/{hard_total} hard requirements unrecoverable "
            f"(> {rules['unrecoverable_hard_fraction']:.0%})"
        )
    if location and location["result"] == "trip":
        reasons.append(f"location: {location['reason']}")

    out = {
        "unrecoverable_hard_gaps": [r["id"] for r in unrecoverable],
        "unrecoverable_hard_count": n,
        "weak_partial_hard_gaps": [r["id"] for r in weak_partial],
        "weighted_unrecoverable": tally,
        "hard_total": hard_total,
        "tripped": bool(reasons),
        "reasons": reasons,
    }
    if location is not None:
        out["location"] = location
    return out


def _load(path):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) if path else None


def evaluate_files(gapmap_path, requirements_path=None, location_path=None,
                   preferences_path=None, trip_rules: dict | None = None) -> dict:
    location = None
    if requirements_path:
        import location_gate

        location = location_gate.evaluate(
            _load(requirements_path), _load(location_path), _load(preferences_path)
        )
    return evaluate(_load(gapmap_path), trip_rules, location)


def evaluate_file(path, trip_rules: dict | None = None) -> dict:
    return evaluate(_load(path), trip_rules)


if __name__ == "__main__":
    import argparse
    import json

    ap = argparse.ArgumentParser(description="Gate 1 tally + location check.")
    ap.add_argument("gapmap")
    ap.add_argument("--requirements", help="run requirements.yaml (enables the location check)")
    ap.add_argument("--location", help="run location.yaml (needed unless the role is remote)")
    ap.add_argument("--preferences", help="preferences.yaml; omitted -> location not-evaluated")
    ap.add_argument("--out", help="also write the result to this YAML file")
    args = ap.parse_args()

    result = evaluate_files(args.gapmap, args.requirements, args.location, args.preferences)
    if args.out:
        Path(args.out).write_text(yaml.safe_dump(result, sort_keys=False, allow_unicode=True),
                                  encoding="utf-8")
    print(json.dumps(result, indent=2))
