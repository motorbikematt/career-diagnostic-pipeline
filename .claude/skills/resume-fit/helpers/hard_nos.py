"""List the WHD's hard-no markers with their age (deterministic, zero tokens).

A hard-no marker records something the candidate confirmed they cannot honestly
claim, so future runs do not re-litigate it. Format (written by Phase H):

    - hard-no: <what> (confirmed YYYY-MM-DD)

Markers never expire on their own. Two consumers:
- The hard-no REVIEW MODE walks every marker (still true / now have evidence /
  remove). Nobody can be expected to remember them, so this helper lists them.
- Synthesis, when a JD touches a marker older than --stale-days (default 365),
  raises an Open Question asking whether it still holds.

Any line mentioning "hard-no" that does NOT parse is reported under `unparsed`,
so a typo cannot silently drop a marker from review.

`hard_no_reviewed: YYYY-MM-DD` in the WHD front-matter records the last full
review; `review_due` is true when markers exist and that date is missing or
older than --review-days (default 183). `mark-reviewed` sets it to today.
"""
from __future__ import annotations

import re
from datetime import date

from whd_anchors import ANCHOR_RE
from whd_io import read_front_matter, read_whd, set_front_matter_key, write_whd

_MARKER = re.compile(r"hard-no:\s*(?P<what>.+?)\s*\(confirmed (?P<on>\d{4}-\d{2}-\d{2})\)")
# Any spelling of the marker ("hard-no", "hard no", "hard_no"), so a typo is caught.
_MENTION = re.compile(r"\bhard[\s_-]?no\b", re.IGNORECASE)
REVIEW_KEY = "hard_no_reviewed"


def _age(on: str, today: date) -> int:
    return (today - date.fromisoformat(on)).days


def scan(text: str, today: date | None = None, stale_days: int = 365,
         review_days: int = 183) -> dict:
    today = today or date.today()
    lines = text.split("\n")
    try:
        fm = read_front_matter(text)
        body_start = next(i for i in range(1, len(lines)) if lines[i].strip() == "---") + 1
    except ValueError:
        fm, body_start = {}, 0

    markers, unparsed = [], []
    anchor = None
    for i in range(body_start, len(lines)):
        line = lines[i]
        m = ANCHOR_RE.match(line)
        if m:
            anchor = m.group("id")
            continue
        if anchor == "changelog" or not _MENTION.search(line):
            continue
        mk = _MARKER.search(line)
        if mk:
            markers.append({
                "what": mk.group("what"),
                "confirmed": mk.group("on"),
                "age_days": _age(mk.group("on"), today),
                "anchor": anchor,
                "line": i + 1,
            })
        else:
            unparsed.append({"text": line.strip(), "anchor": anchor, "line": i + 1})

    reviewed = fm.get(REVIEW_KEY)
    reviewed = str(reviewed) if reviewed else None
    review_due = bool(markers) and (reviewed is None or _age(reviewed, today) > review_days)
    return {
        "marker_count": len(markers),
        "markers": markers,
        "stale": [m for m in markers if m["age_days"] > stale_days],
        "unparsed": unparsed,
        "last_review": reviewed,
        "review_due": review_due,
    }


def mark_reviewed(whd_path, on: str | None = None) -> str:
    on = on or date.today().isoformat()
    text, eol = read_whd(whd_path)
    write_whd(whd_path, set_front_matter_key(text, REVIEW_KEY, on), eol)
    return on


if __name__ == "__main__":
    import argparse
    import json

    from console import utf8_stdout

    utf8_stdout()
    ap = argparse.ArgumentParser(description="List WHD hard-no markers.")
    ap.add_argument("whd", nargs="+", help="<whd.md>, or: mark-reviewed <whd.md>")
    ap.add_argument("--stale-days", type=int, default=365)
    ap.add_argument("--review-days", type=int, default=183)
    args = ap.parse_args()

    if args.whd[0] == "mark-reviewed":
        print(f"{REVIEW_KEY} set to {mark_reviewed(args.whd[1])}")
    else:
        text, _ = read_whd(args.whd[0])
        print(json.dumps(scan(text, stale_days=args.stale_days, review_days=args.review_days),
                         indent=2, ensure_ascii=False))
