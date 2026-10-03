"""Resume structure lint: titles, section headings, date format (deterministic).

Evidence (docs/research/resume-fit-guidance.md section 1): Greenhouse documents
that abbreviated titles ("Sr.") and company names without a legal identifier
parse poorly [S1]; missing or inconsistent sections cause partial parses [S1];
nonstandard headings were flagged in a direct test [S93].

Input is resume markdown, the same input as `chrono_check.py`, whose entry
detection is reused. Rules and severity:

  FAILURES (exit 1)
    abbreviated-title   an entry line uses an abbreviation such as "Sr." or "Mgr"
    mixed-date-format   entries mix date formats (YYYY, Mon YYYY, Month YYYY,
                        MM/YYYY), or one entry mixes them internally
    missing-experience  no "Experience" section

  ADVISORIES (reported, never fail)
    nonstandard-heading a `##` heading outside the allowlist (default Summary,
                        Experience, Education, Skills; extend with --allow)
    missing-section     Summary, Education or Skills heading absent
    no-legal-identifier an Experience entry shows no Inc., LLC, Corp., Ltd. and
                        the like. Many employers legitimately have none, and this
                        helper cannot know a legal name, so it never suggests one.

VALUE-BLIND: it flags with line numbers and never rewrites the resume.
"""
from __future__ import annotations

import re
from pathlib import Path

import chrono_check

DEFAULT_HEADINGS = ("Summary", "Experience", "Education", "Skills")

# Always flagged, with or without a trailing period.
_ABBREV_ALWAYS = {
    "sr": "Senior", "jr": "Junior", "mgr": "Manager", "dir": "Director",
    "asst": "Assistant", "assoc": "Associate", "engr": "Engineer",
}
# Flagged only with a trailing period, to avoid matching ordinary words.
_ABBREV_DOTTED = {"eng": "Engineer", "exec": "Executive", "coord": "Coordinator",
                  "supv": "Supervisor"}
_ABBREV_RE = re.compile(r"\b([A-Za-z]{2,5})(\.?)(?![A-Za-z])")

_LEGAL_RE = re.compile(
    r"\b(Inc|LLC|L\.L\.C|Corp|Corporation|Ltd|Limited|GmbH|PLC|LP|LLP|PBC|Co)\b\.?",
    re.IGNORECASE,
)

_MONTH_FULL = {"january", "february", "march", "april", "june", "july", "august",
               "september", "october", "november", "december"}
_MONTH_ABBREV = {"jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "sept",
                 "oct", "nov", "dec"}
_MONTH_WORD = (r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
               r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|"
               r"Nov(?:ember)?|Dec(?:ember)?)")
_DATE_RE = re.compile(
    rf"(?P<mon>{_MONTH_WORD})\.?\s+(?:19|20)\d{{2}}"
    r"|(?P<num>(?:0?[1-9]|1[0-2])/(?:19|20)\d{2})"
    r"|(?P<year>\b(?:19|20)\d{2}\b)",
    re.IGNORECASE,
)
_BULLET = re.compile(r"^[-*] ")


def _date_text(lines: list, line_no: int, label: str) -> str:
    """The entry's date text: its own label, else the next non-bullet line."""
    if _DATE_RE.search(label):
        return label
    for nxt in lines[line_no:]:
        n = nxt.strip()
        if not n:
            continue
        if _BULLET.match(n) or n.startswith("#") or chrono_check._BOLD_LINE.match(n):
            return ""
        return n
    return ""


def _date_kinds(text: str) -> set:
    """Date format kinds used in `text`. "May" is ambiguous (short and full), so skipped."""
    kinds = set()
    for m in _DATE_RE.finditer(text):
        if m.group("year"):
            kinds.add("YYYY")
        elif m.group("num"):
            kinds.add("MM/YYYY")
        else:
            word = m.group("mon").lower()
            if word == "may":
                continue
            kinds.add("Month YYYY" if word in _MONTH_FULL else "Mon YYYY")
    return kinds


def _abbreviations(label: str) -> list:
    out = []
    for m in _ABBREV_RE.finditer(label):
        word, dot = m.group(1).lower(), m.group(2)
        if word in _ABBREV_ALWAYS:
            out.append((m.group(1) + dot, _ABBREV_ALWAYS[word]))
        elif dot and word in _ABBREV_DOTTED:
            out.append((m.group(1) + dot, _ABBREV_DOTTED[word]))
    return out


def _headings(md_text: str) -> list:
    out = []
    for i, raw in enumerate(md_text.splitlines(), start=1):
        s = raw.strip()
        if s.startswith("## "):
            out.append((i, s[3:].strip().rstrip(":")))
    return out


def check(md_text: str, allow: tuple = ()) -> dict:
    lines = md_text.splitlines()
    allowed = {h.lower() for h in (*DEFAULT_HEADINGS, *allow)}
    failures, advisories = [], []

    headings = _headings(md_text)
    present = {h.lower() for _, h in headings}
    for lineno, h in headings:
        if h.lower() not in allowed:
            advisories.append({"rule": "nonstandard-heading", "line": lineno, "heading": h,
                               "detail": f"'{h}' is not a standard heading; ATS parsers "
                                         "expect Summary, Experience, Education, Skills"})
    if "experience" not in present:
        failures.append({"rule": "missing-experience", "line": None,
                         "detail": "no 'Experience' section heading found"})
    for name in ("Summary", "Education", "Skills"):
        if name.lower() not in present:
            advisories.append({"rule": "missing-section", "line": None, "heading": name,
                               "detail": f"no '{name}' section heading found"})

    kinds_by_entry = []
    for e in chrono_check._entries(md_text):
        label, line, section = e["entry"], e["line"], e["section"]
        for found, expansion in _abbreviations(label):
            failures.append({"rule": "abbreviated-title", "line": line, "entry": label,
                             "detail": f"'{found}' should be written '{expansion}'"})
        kinds = _date_kinds(_date_text(lines, line, label))
        if kinds:
            kinds_by_entry.append((line, label, kinds))
            if len(kinds) > 1:
                failures.append({"rule": "mixed-date-format", "line": line, "entry": label,
                                 "detail": "one entry mixes date formats: "
                                           + ", ".join(sorted(kinds))})
        if "experience" in section.lower() and not _LEGAL_RE.search(label):
            advisories.append({"rule": "no-legal-identifier", "line": line, "entry": label,
                               "detail": "no legal identifier (Inc., LLC, Corp.) in the entry "
                                         "line; add one only where true"})

    all_kinds = set().union(*(k for _, _, k in kinds_by_entry)) if kinds_by_entry else set()
    if len(all_kinds) > 1:
        for line, label, kinds in kinds_by_entry:
            if len(kinds) != 1:
                continue  # already reported as an internal mix
            failures.append({"rule": "mixed-date-format", "line": line, "entry": label,
                             "detail": f"uses {next(iter(kinds))}; the resume mixes "
                                       + ", ".join(sorted(all_kinds))})
    return {"ok": not failures, "failures": failures, "advisories": advisories,
            "date_formats": sorted(all_kinds)}


def check_file(path, allow: tuple = ()) -> dict:
    return check(Path(path).read_text(encoding="utf-8"), allow=allow)


if __name__ == "__main__":
    import argparse
    import json
    import sys

    from console import utf8_stdout

    utf8_stdout()
    ap = argparse.ArgumentParser(description="Lint resume titles, headings and date format.")
    ap.add_argument("path")
    ap.add_argument("--allow", nargs="+", default=[], metavar="HEADING",
                    help="extra section headings to accept (e.g. Patents Certifications)")
    args = ap.parse_args()

    result = check_file(args.path, allow=tuple(args.allow))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if not result["ok"]:
        print(f"STRUCTURE LINT: {len(result['failures'])} failure(s), "
              f"{len(result['advisories'])} advisory note(s)")
        sys.exit(1)
