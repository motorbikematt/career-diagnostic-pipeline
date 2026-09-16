"""Build a screening-safe summary of the gapmap.

The screening subagent must be WHD-blind. The full gapmap carries WHD-derived
fields (whd_evidence, recoverable); those are STRIPPED so the screening input
reflects only what the resume alone supports. This is the dispatch-construction
layer of screening-blindness enforcement (plan section 9, layer 1).
"""
from __future__ import annotations

from pathlib import Path

import yaml

# Fields safe to show screening: derived from the resume/JD, never the WHD.
SAFE_REQ_FIELDS = ("id", "kind", "classification", "resume_evidence")


def summarize(gapmap: dict) -> dict:
    reqs = [
        {k: r.get(k) for k in SAFE_REQ_FIELDS}
        for r in gapmap.get("requirements", [])
    ]
    return {
        "requirements": reqs,
        "seeker_archetype": gapmap.get("seeker_archetype"),
        "jd_archetype": gapmap.get("jd_archetype"),
        "ats": gapmap.get("ats"),
    }


def summarize_file(path) -> dict:
    return summarize(yaml.safe_load(Path(path).read_text(encoding="utf-8")))


if __name__ == "__main__":
    import sys

    print(yaml.safe_dump(summarize_file(sys.argv[1]), sort_keys=False, allow_unicode=True))
