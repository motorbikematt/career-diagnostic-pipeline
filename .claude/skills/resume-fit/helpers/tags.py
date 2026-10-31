"""Finishing-loop tag scan and exit check (deterministic).

The silent draft carries inline tags that are the finishing loop's worklist. The
loop cannot terminate until zero tags remain (plan section 4, exit criteria).
This helper counts tags by type and reports whether the draft is clean.

Tags (from the v1 ghost-editor, preserved):
  [CHANGED] [REMOVED] [CANDIDATE TO SUPPLY] [NOT INTEGRATED]  and  VOICE NOTE
[CHANGED]/[REMOVED] are informational review markers; the BLOCKING tags that must
reach zero before render are CANDIDATE TO SUPPLY, NOT INTEGRATED, and VOICE NOTE.
"""
from __future__ import annotations

import re
from pathlib import Path

BLOCKING = ["CANDIDATE TO SUPPLY", "NOT INTEGRATED", "VOICE NOTE"]
INFO = ["CHANGED", "REMOVED"]
ALL = BLOCKING + INFO


_REMOVED = re.compile(r"\[REMOVED\b")
_INFO_TAG = re.compile(r"\[(?:" + "|".join(map(re.escape, INFO)) + r")\b[^\]]*\][ \t]?")


def live_text(text: str) -> str:
    """The draft as the rendered resume will read: the measuring helpers' input.

    A line tagged [REMOVED] is dead and becomes an empty line (so line numbers
    still match the file); the informational tags are stripped from the rest.
    Blocking tags are left alone: the exit check owns them.
    """
    return "\n".join("" if _REMOVED.search(line) else _INFO_TAG.sub("", line)
                     for line in text.splitlines())


def scan(text: str) -> dict:
    counts = {}
    for tag in ALL:
        # match [TAG ...] or bare VOICE NOTE:
        pattern = r"\[" + re.escape(tag) + r"\b" + r"|" + r"\b" + re.escape(tag) + r"\b"
        counts[tag] = len(re.findall(pattern, text))
    blocking_total = sum(counts[t] for t in BLOCKING)
    return {
        "counts": counts,
        "blocking_total": blocking_total,
        "clean": blocking_total == 0,
    }


def scan_file(path) -> dict:
    return scan(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    import json
    import sys

    result = scan_file(sys.argv[1])
    print(json.dumps(result, indent=2))
    if not result["clean"]:
        print(f"NOT SUBMITTABLE: {result['blocking_total']} blocking tag(s) remain")
        sys.exit(1)
