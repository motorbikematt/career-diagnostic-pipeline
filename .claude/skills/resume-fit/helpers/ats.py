"""Exact-match ATS keyword scan, synonym-aware.

Term frequency between JD keywords and resume text is string matching, not
judgment — so Python owns it. The model only adjudicates semantic terminology
mismatches separately (e.g. "Product Ops" vs. "Program Management").

Synonym/abbreviation pairs (e.g. "K8s" / "Kubernetes") are still exact-match
string equivalence, not semantic judgment, so they stay in this deterministic
layer via skill_taxonomy.yaml.

Matching is case-insensitive EXCEPT for the short terms in CASE_SENSITIVE, which
are also ordinary English words or names ("go", "rest", "node", "Ai"). Those
match only in their written technical form, so "we go to market" no longer
counts as the Go language and "the rest of the team" no longer counts as a REST
API.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

TAXONOMY_PATH = Path(__file__).resolve().parent / "skill_taxonomy.yaml"

# lowercase term -> the only spelling that counts as a match.
CASE_SENSITIVE = {
    "go": "Go",
    "rest": "REST",
    "node": "Node",
    "ai": "AI",
    "ml": "ML",
    "ts": "TS",
    "rn": "RN",
}

# Case-sensitive terms whose hyphen compounds are a different word.
HYPHEN_EXCLUDED = {"go"}


def _load_synonyms() -> dict:
    if not TAXONOMY_PATH.exists():
        return {}
    return yaml.safe_load(TAXONOMY_PATH.read_text(encoding="utf-8")) or {}


SKILL_SYNONYMS = _load_synonyms()


def _matches(cand: str, text: str, text_lower: str) -> bool:
    cased = CASE_SENSITIVE.get(cand)
    if cased is not None:
        # Exact casing. Hyphen compounds still count ("AI-native", "ML-based"),
        # except for terms in HYPHEN_EXCLUDED ("Go-to-market" is not Go).
        tail = r"(?![\w-])" if cand in HYPHEN_EXCLUDED else r"(?!\w)"
        pattern = r"(?<!\w)" + re.escape(cased) + tail
        return re.search(pattern, text) is not None
    # Word-boundary match that also works for multi-word and hyphenated terms.
    pattern = r"(?<!\w)" + re.escape(cand) + r"(?!\w)"
    return re.search(pattern, text_lower) is not None


def _present(keyword: str, text: str, synonyms: dict | None = None) -> bool:
    """True if `keyword` (or a taxonomy synonym of it) appears in `text`.

    `text` is the original, un-lowercased text: case-sensitive terms need it.
    """
    synonyms = SKILL_SYNONYMS if synonyms is None else synonyms
    kw = keyword.strip().lower()
    if not kw:
        return False
    canonical = synonyms.get(kw, kw)
    candidates = {kw, canonical}
    candidates.update(k for k, v in synonyms.items() if v == canonical)
    text_lower = text.lower()
    return any(_matches(cand, text, text_lower) for cand in candidates)


def scan(jd_keywords, resume_text: str) -> dict:
    present, missing = [], []
    for kw in jd_keywords:
        (present if _present(kw, resume_text) else missing).append(kw)
    return {
        "present": present,
        "missing": missing,
        "coverage": round(len(present) / len(jd_keywords) * 100) if jd_keywords else 0,
    }


if __name__ == "__main__":
    import json
    import sys

    req = yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8"))
    kws = req.get("ats_keywords", []) if isinstance(req, dict) else req
    resume = Path(sys.argv[2]).read_text(encoding="utf-8")
    print(json.dumps(scan(kws, resume), indent=2))
