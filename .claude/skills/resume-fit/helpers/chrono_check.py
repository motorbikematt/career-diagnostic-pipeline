"""Reverse-chronological ordering check for a resume draft (deterministic).

Invariant (contracts/finishing.md §2b): within each `##` section, dated entries
appear newest first. Nothing enforced this before, and an ambiguous prescription
once placed a decade-old role at the top of a resume.

An ENTRY is a `###` heading or a line that is entirely bold (`**...**`). Its
dates are read from the entry line, or failing that from the next non-bullet
line (a common "2020 – Present" layout). Years are compared, so month-level
order within one year is not checked. "present" / "current" / "now" sort as the
latest possible end. Undated entries are listed but never fail the check.

Sort key per entry is (end, start). The check fails when any entry is strictly
newer than the entry above it.
"""
from __future__ import annotations

import re
from pathlib import Path

_YEAR = re.compile(r"\b(19|20)\d{2}\b")
_ONGOING = re.compile(r"\b(present|current|now)\b", re.IGNORECASE)
_BOLD_LINE = re.compile(r"^\*\*[^*].*\*\*$")
ONGOING_END = 9999


def _dates(text: str):
    years = [int(m.group(0)) for m in _YEAR.finditer(text)]
    ongoing = bool(_ONGOING.search(text))
    if not years:
        return None
    start = years[0]
    end = ONGOING_END if ongoing else years[-1]
    return end, start


def _entries(md_text: str) -> list:
    """Return [{section, entry, line, key}] for every entry, in document order."""
    lines = md_text.splitlines()
    section = "(top)"
    out = []
    for i, raw in enumerate(lines):
        s = raw.strip()
        if s.startswith("## "):
            section = s[3:].strip()
            continue
        is_entry = s.startswith("### ") or bool(_BOLD_LINE.match(s))
        if not is_entry:
            continue
        label = s[4:].strip() if s.startswith("### ") else s.strip("*").strip()
        key = _dates(label)
        if key is None:
            # Look at the next non-blank line when it is not a bullet or entry.
            for nxt in lines[i + 1:]:
                n = nxt.strip()
                if not n:
                    continue
                is_bullet = re.match(r"^[-*] ", n) is not None
                if not (is_bullet or n.startswith("#") or _BOLD_LINE.match(n)):
                    key = _dates(n)
                break
        out.append({"section": section, "entry": label, "line": i + 1, "key": key})
    return out


def check(md_text: str) -> dict:
    entries = _entries(md_text)
    violations, undated = [], []
    last_by_section: dict = {}
    for e in entries:
        if e["key"] is None:
            undated.append({"section": e["section"], "entry": e["entry"], "line": e["line"]})
            continue
        prev = last_by_section.get(e["section"])
        if prev is not None and e["key"] > prev["key"]:
            violations.append({
                "section": e["section"],
                "entry": e["entry"],
                "line": e["line"],
                "is_newer_than": prev["entry"],
                "above_line": prev["line"],
            })
        last_by_section[e["section"]] = e
    return {"ordered": not violations, "violations": violations, "undated": undated}


def check_file(path) -> dict:
    return check(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    import json
    import sys

    from console import utf8_stdout

    utf8_stdout()
    result = check_file(sys.argv[1])
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if not result["ordered"]:
        print(f"OUT OF ORDER: {len(result['violations'])} entries are newer than "
              "the entry above them (sections must be newest-first)")
        sys.exit(1)
