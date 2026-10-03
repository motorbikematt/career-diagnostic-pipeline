"""Character scanner for resume text (deterministic, JD-independent).

Every violation carries a `category` that says WHY it is flagged, because the
evidence differs (docs/research/ats-evidence-2026.md; two direct extraction
tests found dashes and curly quotes survive intact [S93, L1]):

  house-style   em/en dashes, curly quotes, arrows. A house rule of the resume
                owner (dashes read as an AI-authorship tell), NOT a documented
                ATS parsing failure.
  hygiene       emoji, decorative bullets/stars/checkmarks, inline bullet
                characters. Cheap to avoid and unreadable to some parsers.
  search-term   "&" used as a substituted "and" in prose (e.g. "Sales & Marketing"),
                which can miss a recruiter search for the literal phrase. A
                heuristic exception covers brand names (AT&T, M&A, Dolce & Gabbana).
                Treat as style unless the phrase is a plausible JD search term.

Detecting these is exact character matching, so Python owns it, the same
principle as ats.py's keyword matching and canary.py's token scan.

VALUE-BLIND: this flags violations with line numbers; it does not rewrite the
text. A fix often requires restructuring the sentence (e.g. an em-dash clause
becomes two sentences), which is a judgment call for the model/user, not a
mechanical substitution this helper should silently apply.
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

# Character -> human-readable reason it is flagged.
UNSAFE_CHARS = {
    "—": "em dash (—): house style, rephrase the clause",
    "–": "en dash (–): house style, use a plain hyphen (-) for date ranges",
    "‘": "curly single-quote opening: house style, use a straight apostrophe (')",
    "’": "curly single-quote closing: house style, use a straight apostrophe (')",
    "“": "curly double-quote opening (“): house style, use a straight quote (\")",
    "”": "curly double-quote closing (”): house style, use a straight quote (\")",
    "•": "bullet character (•) inline in text: use markdown '- ' list syntax instead",
    "→": "arrow (→): house style, spell out ('to')",
    "➤": "decorative arrow bullet (➤): use a plain hyphen bullet",
    "★": "decorative star (★): remove or use plain text",
    "◆": "decorative diamond (◆): remove or use plain text",
    "✔": "checkmark (✔): remove or use plain text",
    "✓": "checkmark (✓): remove or use plain text",
}

# Characters flagged as the owner's house style rather than a parsing hazard.
HOUSE_STYLE_CHARS = frozenset("—–‘’“”→")


def _category(ch: str) -> str:
    return "house-style" if ch in HOUSE_STYLE_CHARS else "hygiene"


def _is_emoji(ch: str) -> bool:
    try:
        name = unicodedata.name(ch)
    except ValueError:
        return False
    return "EMOJI" in name or unicodedata.category(ch) == "So" and ord(ch) > 0x2600


# Ampersand: flagged EXCEPT inside a literal company/brand-name token, where it's
# expected and correct (AT&T, M&A, Dolce & Gabbana). Heuristic: a brand token is a
# PROPER-NOUN pair -- both sides start with a capital letter and are not common
# lowercase role/domain words (which is how "&" shows up as a substituted "and" in
# prose, e.g. "Sales & Marketing", "Product & Partnerships"). This can't be a
# blanket ban -- ampersand is only unsafe as a REPLACEMENT for the word "and" in
# prose, a real ATS keyword-matching risk (a JD's literal "Sales and Marketing"
# may not match "Sales & Marketing"), not a ban on the character itself.
_AMPERSAND_TOKEN_RE = re.compile(r"([A-Za-z]+)\s*&\s*([A-Za-z]+)")

# Common resume role/domain nouns that read as prose "and" even when capitalized
# (title case is standard in resume headings) -- distinguishes "Product &
# Partnerships" (prose) from "Dolce & Gabbana" (brand) even though both are
# capitalized proper-noun-shaped tokens.
_PROSE_AMPERSAND_WORDS = {
    "product", "partnerships", "sales", "marketing", "engineering", "design",
    "operations", "strategy", "planning", "management", "research", "development",
    "growth", "acquisition", "activation", "monetization", "programs", "policy",
    "communications", "partner", "partner management", "customer", "success",
    "analytics", "data", "platform", "infrastructure", "security", "legal",
}


def _ampersand_violations(line: str) -> list:
    """Heuristic, not exhaustive: catches the common resume-role-noun case
    ("Sales & Marketing") and the common brand cases in the test suite (AT&T,
    M&A, Dolce & Gabbana). An unfamiliar brand name not in _PROSE_AMPERSAND_WORDS
    and not matching either side could still slip through unflagged, or a
    legitimate but unlisted role noun could go unflagged too -- this trades
    perfect recall for a low false-positive rate on real brand names."""
    out = []
    for m in re.finditer(_AMPERSAND_TOKEN_RE, line):
        left, right = m.group(1).lower(), m.group(2).lower()
        if left in _PROSE_AMPERSAND_WORDS or right in _PROSE_AMPERSAND_WORDS:
            out.append(m.start())  # reads as substituted "and" -- flag
        # else: looks like a brand/company token (AT&T, M&A, Dolce & Gabbana) -- allowed
    return out


def scan(text: str) -> dict:
    violations = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for ch in line:
            reason = UNSAFE_CHARS.get(ch)
            if reason is None and _is_emoji(ch) and ch not in UNSAFE_CHARS:
                reason = f"emoji ({ch}): some parsers cannot read emoji"
            if reason:
                violations.append({
                    "line": lineno,
                    "char": ch,
                    "category": _category(ch),
                    "reason": reason,
                    "context": line.strip()[:100],
                })
        for _pos in _ampersand_violations(line):
            violations.append({
                "line": lineno,
                "char": "&",
                "category": "search-term",
                "reason": "ampersand (&) used as 'and': a recruiter search for the "
                          "literal phrase (e.g. 'Sales and Marketing') may not match "
                          "'Sales & Marketing'; style unless the phrase is a likely "
                          "search term, and fine in a brand name (AT&T, M&A)",
                "context": line.strip()[:100],
            })
    seen = set()
    unique = []
    for v in violations:
        key = (v["line"], v["char"])
        if key not in seen:
            seen.add(key)
            unique.append(v)
    return {
        "violation_count": len(unique),
        "clean": len(unique) == 0,
        "violations": unique,
    }


def scan_file(path) -> dict:
    return scan(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    import json
    import sys

    from console import utf8_stdout

    utf8_stdout()
    result = scan_file(sys.argv[1])
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if not result["clean"]:
        by_cat: dict = {}
        for v in result["violations"]:
            by_cat[v["category"]] = by_cat.get(v["category"], 0) + 1
        print(f"CHARACTER FLAGS: {result['violation_count']} found "
              + ", ".join(f"{n} {c}" for c, n in sorted(by_cat.items())))
        sys.exit(1)
