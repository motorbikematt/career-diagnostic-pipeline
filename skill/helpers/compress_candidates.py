"""List-compression candidate detector (deterministic pattern, NOT a rewriter).

Detects a mechanical PATTERN: a claim element containing a comma/and-separated
list of 3+ items (e.g. "China, Australia, and US/Europe/Korea" or "Aerospace,
Automotive, and Toys"). Compressing such a list to a count + category phrase
(e.g. "3 trans-continental" / "3 verticals") is a common, safe space-saving move
-- but choosing an ACCURATE category word requires understanding what the listed
items ARE, which is semantic judgment, not pattern matching.

So this helper only finds candidates and reports the item count + estimated
lines freed if compressed to "N <category>". It never proposes the category
word itself -- that's the model's job, surfaced in the finishing loop's length
round, with the user ratifying before it's applied (same "Python meters, model
proposes, user decides" split as relevance.py and length_budget.py).

Restricted to 3+ item lists (2-item lists rarely benefit: "2 things" reads worse
than "X and Y" and saves almost nothing).
"""
from __future__ import annotations

import re
from pathlib import Path

from length_budget import _classify, _strip_md

_SCORED_KINDS = {"bullet", "para"}

# A list item: split on ", " optionally followed by "and "/"& " before the last
# item. Matches "A, B, and C" / "A, B and C" / "A, B, C".
_LIST_RE = re.compile(
    r"(?:[A-Za-z0-9][\w/&.\-]*(?:\s+[A-Za-z0-9][\w/&.\-]*){0,3})"
    r"(?:,\s*(?:and\s+)?[A-Za-z0-9][\w/&.\-]*(?:\s+[A-Za-z0-9][\w/&.\-]*){0,3}){2,}"
)


def _find_list(text: str):
    """Return the longest comma/and-joined list of 3+ items in text, or None."""
    best = None
    for m in re.finditer(_LIST_RE, text):
        segment = m.group(0)
        items = [s.strip() for s in re.split(r",\s*(?:and\s+)?|\s+and\s+", segment) if s.strip()]
        if len(items) >= 3 and (best is None or len(items) > len(best["items"])):
            best = {"span": m.span(), "segment": segment, "items": items}
    return best


def analyze(resume_md: str) -> dict:
    candidates = []
    for raw in resume_md.splitlines():
        c = _classify(raw)
        if c is None:
            continue
        kind, vis, _pt = c
        if kind not in _SCORED_KINDS:
            continue
        vis = _strip_md(vis)
        found = _find_list(vis)
        if found is None:
            continue
        item_count = len(found["items"])
        # Rough chars-freed estimate: list text minus a generic "N <category>"
        # placeholder (~12 chars) -- advisory only, not used for a hard decision.
        chars_freed = max(0, len(found["segment"]) - 12)
        candidates.append({
            "text": vis,
            "list_segment": found["segment"],
            "items": found["items"],
            "item_count": item_count,
            "est_chars_freed": chars_freed,
        })
    return {"candidate_count": len(candidates), "candidates": candidates}


def analyze_file(path) -> dict:
    return analyze(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    import json
    import sys

    result = analyze_file(sys.argv[1])
    print(json.dumps(result, indent=2, ensure_ascii=False))
