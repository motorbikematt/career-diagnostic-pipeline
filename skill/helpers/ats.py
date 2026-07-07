"""Exact-match ATS keyword scan, synonym-aware.

Term frequency between JD keywords and resume text is string matching, not
judgment — so Python owns it. The model only adjudicates semantic terminology
mismatches separately (e.g. "Product Ops" vs. "Program Management").

Synonym/abbreviation pairs (e.g. "K8s" / "Kubernetes") are still exact-match
string equivalence, not semantic judgment, so they stay in this deterministic
layer via skill_taxonomy.yaml.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

TAXONOMY_PATH = Path(__file__).resolve().parent / "skill_taxonomy.yaml"


def _load_synonyms() -> dict:
    if not TAXONOMY_PATH.exists():
        return {}
    return yaml.safe_load(TAXONOMY_PATH.read_text(encoding="utf-8")) or {}


SKILL_SYNONYMS = _load_synonyms()


def _present(keyword: str, text_lower: str, synonyms: dict | None = None) -> bool:
    synonyms = SKILL_SYNONYMS if synonyms is None else synonyms
    kw = keyword.strip().lower()
    if not kw:
        return False
    canonical = synonyms.get(kw, kw)
    candidates = {kw, canonical}
    candidates.update(k for k, v in synonyms.items() if v == canonical)
    for cand in candidates:
        # Word-boundary match that also works for multi-word and hyphenated terms.
        pattern = r"(?<!\w)" + re.escape(cand) + r"(?!\w)"
        if re.search(pattern, text_lower):
            return True
    return False


def scan(jd_keywords, resume_text: str) -> dict:
    tl = resume_text.lower()
    present, missing = [], []
    for kw in jd_keywords:
        (present if _present(kw, tl) else missing).append(kw)
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
