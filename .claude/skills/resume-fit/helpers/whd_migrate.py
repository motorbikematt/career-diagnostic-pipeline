"""Migrate a legacy (pre-anchor) WHD to the anchored layout, provably wording-safe.

A legacy WHD (typically a Word export) has the template's shape, `# Company  |
Title` role headings with `##` subsections and `**N. Title**` projects, but no
`<!-- anchor: id -->` marker lines, no `roles:` index, roles in arbitrary order,
and export artifacts. Without anchors, every tool that addresses the WHD by
section (whd_patch.py, whd_anchors.py citations, prescription sources) fails.

What the migration does (structure only):
1. Inserts anchor marker lines. IDs are STABLE SLUGS, never positional, so a
   newly added most-recent role never renames existing anchors:
     role                <company-slug>             e.g. roblox
     role subsection     <role>.<section>           e.g. roblox.scope
     project             <role>.p<N>                e.g. roblox.p1 (existing number)
     voice sample        voice-sample
     beyond employment   beyond-employment[.<sub>]  e.g. beyond-employment.patents
     changelog           changelog
2. Orders roles newest-first; then Voice Sample, Beyond Employment, Changelog.
3. Fixes export artifacts: whitespace-only lines, `****` split-bold runs, and
   the document-wide bullet counter (`- 60. text` -> `- text`; a ranked
   `- 38. 1. text` keeps its rank as `1. text`).
4. Writes front-matter (existing keys such as `canary` are kept, never
   rotated), a `roles:` index with ISO-month dates, a generated Contents list
   (one line per role) for human readers, and a seeded Changelog.

`--check` proves the wording is unchanged: after the artifact fixes, the
legacy file and the migrated file (minus anchors, front-matter, the Contents
line and the Changelog) must hold the identical multiset of non-empty lines.
Lines may move; none may be added, lost or reworded.
"""
from __future__ import annotations

import re
from collections import Counter
from datetime import date

import yaml

from whd_anchors import ANCHOR_RE
from whd_io import front_matter_end, read_whd, write_whd

_ROLE_H1 = re.compile(r"^# (?P<company>.+?)\s+\|\s+(?P<title>.+?)\s*$")
_PROJECT = re.compile(r"^\*\*(?P<n>\d+)\. ")
_COUNTER_RANKED = re.compile(r"^- \d+\. (\d+\. )")
_COUNTER = re.compile(r"^- \d+\. ")
_MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july",
     "august", "september", "october", "november", "december"], start=1)}
_MONTH_YEAR = re.compile(r"\b(" + "|".join(_MONTHS) + r")\s+(\d{4})\b", re.IGNORECASE)
_ONGOING = re.compile(r"\b(present|current)\b", re.IGNORECASE)
_COMPANY_SUFFIXES = re.compile(
    r"\s+(benefit company|research center|laboratories|networks|corporation|"
    r"company|llc|inc\.?|ltd\.?)$", re.IGNORECASE)
_UPDATED = re.compile(r"Updated:\s*(" + "|".join(_MONTHS) + r")\s+(\d{1,2}),\s*(\d{4})", re.IGNORECASE)

ROLE_SECTIONS = {
    "context": "context", "scope": "scope", "work": "work",
    "relationships": "relationships", "candid self-assessment": "self-assessment",
}
BEYOND_SECTIONS = {
    "education": "education", "certifications": "certifications",
    "publications": "publications", "patents": "patents",
    "ongoing side projects": "side-projects", "domain expertise": "domain-expertise",
    "tools": "tools",
}
# Generated Contents block: this heading line, then one "- " line per role, up
# to the first blank line. --check skips exactly that block.
CONTENTS_HEADING = "**Contents** (generated from the roles index)"
VOICE_H1 = "Candidate Voice Sample"
BEYOND_H1 = "Beyond Employment"


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def company_slug(company: str) -> str:
    return slugify(_COMPANY_SUFFIXES.sub("", company.strip()))


def _section_slug(heading: str, table: dict) -> str:
    h = heading.lower()
    for prefix, slug in table.items():
        if h.startswith(prefix):
            return slug
    return slugify(heading)[:40]


def normalize_line(line: str) -> str:
    """The export-artifact fixes (step 3). Applied to BOTH files in --check."""
    if not line.strip():
        return ""
    line = line.replace("****", "")
    m = _COUNTER_RANKED.match(line)
    if m:
        return m.group(1) + line[m.end():]
    return _COUNTER.sub("- ", line)


def _split_front_matter(text: str):
    lines = text.split("\n")
    try:
        end = front_matter_end(lines)
    except ValueError:
        return {}, lines
    fm = yaml.safe_load("\n".join(lines[1:end])) or {}
    return fm, lines[end + 1:]


def _month_dates(date_line: str):
    """(start 'YYYY-MM', end 'YYYY-MM' | 'present', sort key)."""
    found = [(int(y), _MONTHS[m.lower()]) for m, y in _MONTH_YEAR.findall(date_line)]
    if not found:
        raise ValueError(f"cannot read dates from role date line: {date_line!r}")
    start = found[0]
    ongoing = bool(_ONGOING.search(date_line))
    end = (9999, 12) if ongoing else found[-1]
    fmt = lambda ym: f"{ym[0]:04d}-{ym[1]:02d}"
    return fmt(start), ("present" if ongoing else fmt(end)), (end, start)


def _location(date_line: str) -> str:
    loc = date_line.split("|", 1)[1] if "|" in date_line else ""
    return loc.strip()


def _blocks(body: list):
    """Split body lines into (header_lines, [(h1_line, lines)])."""
    header, blocks, current = [], [], None
    for line in body:
        if line.startswith("# "):
            current = (line, [])
            blocks.append(current)
        elif current is None:
            header.append(line)
        else:
            current[1].append(line)
    return header, blocks


def _split_footer(lines: list):
    """Trailing plain-text lines after the last list item / heading of the final
    block (e.g. 'Document generated: ...'). They move to the header area so the
    last anchored section ends cleanly."""
    i = len(lines)
    while i > 0:
        s = lines[i - 1].strip()
        if s and (s.startswith(("-", "#", "**")) or re.match(r"^\d+\. ", s)):
            break
        i -= 1
    return lines[:i], lines[i:]


def _anchor(aid: str) -> str:
    return f"<!-- anchor: {aid} -->"


def _anchor_role(slug: str, h1: str, lines: list) -> list:
    out = [_anchor(slug), h1]
    for line in lines:
        if line.startswith("## "):
            out.append(_anchor(f"{slug}.{_section_slug(line[3:].strip(), ROLE_SECTIONS)}"))
        m = _PROJECT.match(line)
        if m:
            out.append(_anchor(f"{slug}.p{m.group('n')}"))
        out.append(line)
    return out


def _anchor_beyond(h1: str, lines: list) -> list:
    out = [_anchor("beyond-employment"), h1]
    for line in lines:
        if line.startswith("## "):
            out.append(_anchor(f"beyond-employment.{_section_slug(line[3:].strip(), BEYOND_SECTIONS)}"))
        out.append(line)
    return out


def _collapse_blanks(lines: list) -> list:
    out = []
    for line in lines:
        if line == "" and out and out[-1] == "":
            continue
        out.append(line)
    while out and out[-1] == "":
        out.pop()
    return out


def _spaced(lines: list) -> list:
    """Blank line before every anchor, so each section reads as its own block."""
    out = []
    for line in lines:
        if ANCHOR_RE.match(line) and out and out[-1] != "":
            out.append("")
        out.append(line)
    return out


def migrate(text: str, version: str = "v5", on: str | None = None,
            slugs: dict | None = None) -> str:
    on = on or date.today().isoformat()
    slugs = slugs or {}
    fm, body = _split_front_matter(text)
    if any(ANCHOR_RE.match(l) for l in body):
        raise ValueError("WHD already has anchors; migration is for legacy files only")
    body = [normalize_line(l) for l in body]
    header, blocks = _blocks(body)

    roles, voice, beyond, other = [], None, None, []
    for h1, lines in blocks:
        title = h1[2:].strip()
        if title == VOICE_H1:
            voice = (h1, lines)
        elif title == BEYOND_H1:
            beyond = (h1, lines)
        elif _ROLE_H1.match(h1):
            roles.append((h1, lines))
        else:
            other.append(title)
    if other:
        raise ValueError(f"unrecognized top-level sections (not a role, voice sample or beyond): {other}")

    # Footer text trailing the final block moves up into the header area.
    last = blocks[-1][1]
    kept, footer = _split_footer(last)
    last[:] = kept

    index, anchored_roles, seen = [], [], set()
    for h1, lines in roles:
        m = _ROLE_H1.match(h1)
        company, title = m.group("company").strip(), m.group("title").strip()
        slug = slugs.get(company) or company_slug(company)
        if slug in seen:
            raise ValueError(f"duplicate role slug {slug!r}; pass an override for {company!r}")
        seen.add(slug)
        date_line = next(l for l in lines if l.strip())
        start, end, key = _month_dates(date_line)
        index.append({"key": key, "entry": {
            "id": slug, "company": company, "title": title,
            "dates": f"{start} to {end}", "location": _location(date_line), "tags": [],
        }})
        anchored_roles.append((key, _anchor_role(slug, h1, lines)))
    order = sorted(range(len(index)), key=lambda i: index[i]["key"], reverse=True)

    updated = _UPDATED.search("\n".join(footer + header))
    content_updated = (
        f"{int(updated.group(3)):04d}-{_MONTHS[updated.group(1).lower()]:02d}-{int(updated.group(2)):02d}"
        if updated else on
    )
    owner = next((l.strip("* ").strip() for l in header
                  if l.startswith("**") and "WORK HISTORY" not in l.upper()), "")
    new_fm = {
        "document": "Work History Document",
        "owner": owner,
        "version": version,
        "content_updated": content_updated,
        "structure_updated": on,
        "schema_version": 1,
        **{k: v for k, v in fm.items() if k not in {
            "document", "owner", "version", "content_updated", "structure_updated",
            "schema_version", "roles", "special_sections"}},
        "roles": [index[i]["entry"] for i in order],
        "special_sections": [
            {"id": "voice-sample", "editable": False,
             "note": "Voice calibration source for drafting; the reconciliation loop never edits it."},
            {"id": "beyond-employment"},
            {"id": "changelog"},
        ],
    }
    contents = [CONTENTS_HEADING] + [
        f"- {index[i]['entry']['company']}, {index[i]['entry']['title']} ({index[i]['entry']['dates']})"
        for i in order]

    while header and not header[0].strip():
        header = header[1:]
    out = ["---", yaml.safe_dump(new_fm, sort_keys=False, allow_unicode=True).rstrip("\n"), "---", ""]
    out += _collapse_blanks(header) + [""] + contents + [""]
    if footer and any(l.strip() for l in footer):
        out += _collapse_blanks(footer) + [""]
    for i in order:
        out += _collapse_blanks(anchored_roles[i][1]) + [""]
    if voice:
        out += _collapse_blanks([_anchor("voice-sample"), voice[0], *voice[1]]) + [""]
    if beyond:
        out += _collapse_blanks(_anchor_beyond(beyond[0], beyond[1])) + [""]
    out += [_anchor("changelog"), "# Changelog", "",
            f"- {on} - Migrated to anchored {version} (structure only; no wording changes)."]
    return "\n".join(_spaced(out)) + "\n"


def _content_lines(text: str, migrated: bool) -> Counter:
    _, body = _split_front_matter(text)
    lines = []
    in_contents = False
    for line in body:
        if migrated:
            if line == CONTENTS_HEADING:
                in_contents = True
                continue
            if in_contents:
                if line.strip():
                    continue
                in_contents = False
            if ANCHOR_RE.match(line):
                if line == _anchor("changelog"):
                    break  # the Changelog is generated, and it is last
                continue
        else:
            line = normalize_line(line)
        if line.strip():
            lines.append(line)
    return Counter(lines)


def check(legacy_text: str, migrated_text: str) -> dict:
    a, b = _content_lines(legacy_text, False), _content_lines(migrated_text, True)
    return {
        "identical": a == b,
        "only_in_legacy": sorted((a - b).elements()),
        "only_in_migrated": sorted((b - a).elements()),
        "line_count": sum(a.values()),
    }


if __name__ == "__main__":
    import argparse
    import json
    from pathlib import Path

    from console import utf8_stdout

    utf8_stdout()
    ap = argparse.ArgumentParser(description="Migrate a legacy WHD to the anchored layout.")
    ap.add_argument("legacy")
    ap.add_argument("migrated")
    ap.add_argument("--check", action="store_true", help="only verify wording preservation")
    ap.add_argument("--version", default="v5")
    ap.add_argument("--on", help="migration date (default today)")
    ap.add_argument("--slugs", help="YAML map of company name -> anchor slug overrides")
    args = ap.parse_args()

    legacy, eol = read_whd(args.legacy)
    if not args.check:
        if Path(args.migrated).exists():
            raise SystemExit(f"refusing to overwrite existing {args.migrated}")
        slugs = yaml.safe_load(Path(args.slugs).read_text(encoding="utf-8")) if args.slugs else None
        write_whd(args.migrated, migrate(legacy, args.version, args.on, slugs), eol)
    migrated, _ = read_whd(args.migrated)
    result = check(legacy, migrated)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if not result["identical"]:
        print("WORDING CHANGED: the migrated file does not preserve the legacy lines.")
        raise SystemExit(1)
