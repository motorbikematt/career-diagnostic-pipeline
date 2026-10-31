"""Density lint: flags the parts of a resume that make it slow to scan (advisory).

Basis (docs/research/resume-fit-guidance.md, density section): a recruiter's
first pass covers the top two-thirds of page one [W2], and the 2026-10-22
LinkedIn makeover cut content rather than squeezing it. Every threshold below is
a project rule set by the owner, not a documented ATS or recruiter limit.

Input is resume markdown, the same input as `summary_lint.py` and
`chrono_check.py`. Layout geometry is shared with `length_budget.py`, so the scan
zone is measured on the same estimated page as the length round.

FLAGS (advisory: always exit 0; the user decides every cut)
  bullet-long       a bullet over MAX_BULLET_WORDS words. A ceiling only: there is
                    no floor and no target, because uniform bullet length is
                    itself an AI-writing tell.
  bullet-metrics    a bullet carrying more than MAX_BULLET_NUMBERS numbers.
                    Keep the one that matters; the rest stay in the WHD.
  role-bullets      an Experience role with more bullets than its recency budget
                    (ROLE_BULLET_BUDGET: newest role first, the last value
                    applies to every older role)
  role-intro-long   a role's intro paragraph over MAX_INTRO_WORDS words
  summary-repeats   a number in the summary that also appears in a bullet
  scan-zone-words   more than MAX_SCAN_ZONE_WORDS words in the first
                    SCAN_ZONE_FRACTION of page one
  total-words       the whole resume over MAX_TOTAL_WORDS words

With `--screen <screen.yaml>` it also locates the screen's `escalation_quote`
(the words that earn a call) on the estimated page:
  escalation-below-scan-zone  the quote starts below the scan zone
  escalation-missing          the screen has no quote, or it is not on this resume
A draft may have reworded the line the seed resume carried, so when the exact
words are gone it falls back to the line holding the quote's figures.

Finishing-loop tags are not content: [REMOVED] lines are skipped and [CHANGED]
is stripped before measuring (tags.live_text).

Bullets under a Skills or Education heading are lists, not claims, so the
bullet rules skip them. VALUE-BLIND: it reports cost, never what to cut, and
never rewrites the resume.
"""
from __future__ import annotations

import re
import statistics
from pathlib import Path

import chrono_check
import length_budget
import summary_lint
import tags
import verbatim

# Owner-set 2026-10-23 from six past runs (expect retuning). Past-run ranges:
# bullets 15-101 words (median ~35), scan zone 298-379 words, total 998-1,254.
MAX_BULLET_WORDS = 40
MAX_BULLET_NUMBERS = 2
ROLE_BULLET_BUDGET = (5, 4, 2)
MAX_INTRO_WORDS = 40
MAX_SCAN_ZONE_WORDS = 300
MAX_TOTAL_WORDS = 1000
SCAN_ZONE_FRACTION = 2 / 3

DATE_LINE_MAX_WORDS = 16  # 13 tokens:"Remote (Dayton, OH; HQ San Mateo, CA) | Dec 2022 - Apr 2025"

_BULLET = re.compile(r"^[-*] ")
_LIST_SECTIONS = re.compile(r"skill|education", re.IGNORECASE)
# One number: optional ~ and $, digits with thousands commas or a decimal, an
# optional range ("10-20x" is one figure), then an optional unit. A bare year is
# not a metric.
_FIGURE = r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"
_NUMBER = re.compile(
    rf"(?<![\w.])~?\$?{_FIGURE}(?:\s?[-–]\s?{_FIGURE})?(?:\s?%|[KMBkx]\b)?\+?"
)
_YEAR = re.compile(r"^(?:19|20)\d{2}$")


def _visible(text: str) -> str:
    return length_budget._strip_md(text).strip()


def _words(text: str) -> int:
    return len(_visible(text).split())


def numbers(text: str) -> list:
    """The metric-like numbers in `text`, with bare years left out."""
    return [m.group(0).strip() for m in _NUMBER.finditer(_visible(text))
            if not _YEAR.match(m.group(0).strip())]


def _norm(num: str) -> str:
    return num.lstrip("~$").rstrip("+").replace(",", "").replace(" ", "")


def _significant(num: str) -> bool:
    """Worth matching across sections: two or more digits, or a unit."""
    n = _norm(num)
    return sum(c.isdigit() for c in n) >= 2 or bool(re.search(r"[%KMBkx$]", num))


def _parse(md_text: str) -> dict:
    """Bullets (with section and role) and Experience roles, in document order."""
    md_text = tags.live_text(md_text)
    entry_lines = {e["line"]: e["entry"] for e in chrono_check._entries(md_text)}
    bullets, roles = [], []
    section, role = "(top)", None

    for i, raw in enumerate(md_text.splitlines(), start=1):
        s = raw.strip()
        if s.startswith("## "):
            section, role = s[3:].strip(), None
            continue
        if i in entry_lines:
            role = None
            if "experience" in section.lower():
                role = {"entry": entry_lines[i], "line": i, "bullets": 0, "intro": "",
                        "prose_lines": 0}
                roles.append(role)
            continue
        if _BULLET.match(s):
            bullets.append({"line": i, "text": s[2:].strip(), "section": section,
                            "role": role["entry"] if role else None})
            if role is not None:
                role["bullets"] += 1
            continue
        if not s or s.startswith("#") or role is None or role["bullets"]:
            continue
        # Each line renders as its own paragraph (length_budget.py). A role's
        # intro is the prose between its title and first bullet, less the short
        # location/date line that usually sits directly under the title.
        role["prose_lines"] += 1
        date_line = (role["prose_lines"] == 1 and _words(s) <= DATE_LINE_MAX_WORDS
                     and chrono_check._dates(s) is not None)
        if not date_line:
            role["intro"] = (role["intro"] + " " + s).strip()
    return {"bullets": bullets, "roles": roles}


def _scan_zone_words(md_text: str, margin_in: float, body_pt: float) -> int:
    """Words in the elements that start inside the scan zone of page one."""
    limit = length_budget.usable_page_height_in(margin_in) * SCAN_ZONE_FRACTION
    top, words = 0.0, 0
    for e in length_budget.elements(md_text, margin_in, body_pt):
        if top >= limit:
            break
        words += len(e["text"].split())
        top += e["height_in"]
    return words


def _budget(rank: int) -> int:
    return ROLE_BULLET_BUDGET[min(rank, len(ROLE_BULLET_BUDGET) - 1)]


def locate_quote(md_text: str, quote: str, margin_in: float = length_budget.DEFAULT_MARGIN_IN,
                 body_pt: float = length_budget.BODY_PT) -> dict:
    """Where the quote starts on the estimated page: inches from the top margin.

    Exact words first (see verbatim.py); else the first line that holds every
    significant figure in the quote, for a draft that reworded the line.
    """
    scan_limit = length_budget.usable_page_height_in(margin_in) * SCAN_ZONE_FRACTION
    out = {"match": None, "top_in": None, "scan_zone_ends_in": round(scan_limit, 2),
           "in_scan_zone": False}
    elements = length_budget.elements(md_text, margin_in, body_pt)
    figures = {_norm(n) for n in numbers(quote) if _significant(n)}
    for mode in ("exact", "figures"):
        if mode == "figures" and not figures:
            break
        top = 0.0
        for e in elements:
            if mode == "exact":
                hit = verbatim.in_text(quote, e["text"])
            else:
                hit = figures <= {_norm(n) for n in numbers(e["text"])}
            if hit:
                out.update(match=mode, top_in=round(top, 2), in_scan_zone=top < scan_limit)
                return out
            top += e["height_in"]
    return out


def check(md_text: str, margin_in: float = length_budget.DEFAULT_MARGIN_IN,
          body_pt: float = length_budget.BODY_PT, screen: dict | None = None) -> dict:
    md_text = tags.live_text(md_text)
    parsed = _parse(md_text)
    flags = []

    claims = [b for b in parsed["bullets"] if not _LIST_SECTIONS.search(b["section"])]
    lengths = []
    for b in claims:
        n = _words(b["text"])
        lengths.append(n)
        if n > MAX_BULLET_WORDS:
            flags.append({"rule": "bullet-long", "line": b["line"], "role": b["role"],
                          "detail": f"{n} words (ceiling {MAX_BULLET_WORDS})"})
        nums = numbers(b["text"])
        if len(nums) > MAX_BULLET_NUMBERS:
            flags.append({"rule": "bullet-metrics", "line": b["line"], "role": b["role"],
                          "detail": f"{len(nums)} numbers ({', '.join(nums)}); "
                                    f"limit {MAX_BULLET_NUMBERS}"})

    roles_out = []
    for rank, r in enumerate(parsed["roles"]):
        budget = _budget(rank)
        intro_words = _words(r["intro"]) if r["intro"] else 0
        roles_out.append({"entry": r["entry"], "line": r["line"], "bullets": r["bullets"],
                          "budget": budget, "intro_words": intro_words})
        if r["bullets"] > budget:
            flags.append({"rule": "role-bullets", "line": r["line"], "role": r["entry"],
                          "detail": f"{r['bullets']} bullets (budget {budget} for role "
                                    f"{rank + 1} by recency)"})
        if intro_words > MAX_INTRO_WORDS:
            flags.append({"rule": "role-intro-long", "line": r["line"], "role": r["entry"],
                          "detail": f"intro is {intro_words} words (ceiling {MAX_INTRO_WORDS})"})

    summary = summary_lint.extract_summary(md_text)
    bullet_nums = {_norm(n) for b in claims for n in numbers(b["text"]) if _significant(n)}
    repeated = sorted({n for n in numbers(summary) if _significant(n) and _norm(n) in bullet_nums})
    if repeated:
        flags.append({"rule": "summary-repeats", "line": None, "role": None,
                      "detail": "in both the summary and a bullet: " + ", ".join(repeated)})

    zone_words = _scan_zone_words(md_text, margin_in, body_pt)
    if zone_words > MAX_SCAN_ZONE_WORDS:
        flags.append({"rule": "scan-zone-words", "line": None, "role": None,
                      "detail": f"{zone_words} words in the first "
                                f"{SCAN_ZONE_FRACTION:.0%} of page one "
                                f"(ceiling {MAX_SCAN_ZONE_WORDS})"})

    total = sum(len(_visible(line).lstrip("#-* ").split())
                for line in md_text.splitlines() if line.strip())
    if total > MAX_TOTAL_WORDS:
        flags.append({"rule": "total-words", "line": None, "role": None,
                      "detail": f"{total} words (ceiling {MAX_TOTAL_WORDS})"})

    stats = {
        "total_words": total,
        "scan_zone_words": zone_words,
        "bullets": len(claims),
        "bullet_words_median": statistics.median(lengths) if lengths else 0,
        "bullet_words_max": max(lengths) if lengths else 0,
        "roles": roles_out,
    }

    if screen is not None:
        quote = (screen.get("escalation_quote") or "").strip()
        loc = locate_quote(md_text, quote, margin_in, body_pt) if quote else None
        stats["escalation"] = loc
        if not quote:
            flags.append({"rule": "escalation-missing", "line": None, "role": None,
                          "detail": "the screen has no escalation_quote, so the key metric's "
                                    "position cannot be checked"})
        elif loc["match"] is None:
            flags.append({"rule": "escalation-missing", "line": None, "role": None,
                          "detail": f"the screen's escalation quote is not on this resume: {quote!r}"})
        elif not loc["in_scan_zone"]:
            flags.append({"rule": "escalation-below-scan-zone", "line": None, "role": None,
                          "detail": f"the line that earns a call starts {loc['top_in']} in down "
                                    f"the page; the scan zone ends at {loc['scan_zone_ends_in']} in "
                                    f"(match: {loc['match']})"})
    return {"clean": not flags, "flags": flags, "stats": stats}


def check_file(path, margin_in: float = length_budget.DEFAULT_MARGIN_IN,
               body_pt: float = length_budget.BODY_PT, screen_path=None) -> dict:
    screen = None
    if screen_path:
        import yaml
        screen = yaml.safe_load(Path(screen_path).read_text(encoding="utf-8")) or {}
    return check(Path(path).read_text(encoding="utf-8"), margin_in, body_pt, screen)


if __name__ == "__main__":
    import argparse
    import json

    from console import utf8_stdout

    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("resume", help="resume markdown")
    ap.add_argument("--margin", type=float, default=length_budget.DEFAULT_MARGIN_IN,
                    help="page margin in inches, as passed to render_docx.py")
    ap.add_argument("--body-pt", type=float, default=length_budget.BODY_PT,
                    help="body text size, as passed to render_docx.py")
    ap.add_argument("--screen", help="screen.yaml: also locate its escalation_quote on the page")
    args = ap.parse_args()
    result = check_file(args.resume, args.margin, args.body_pt, args.screen)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result["flags"]:
        print(f"DENSITY LINT: {len(result['flags'])} advisory flag(s)")
