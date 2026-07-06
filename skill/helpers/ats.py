"""Exact-match ATS keyword scan.

Term frequency between JD keywords and resume text is string matching, not
judgment — so Python owns it. The model only adjudicates semantic terminology
mismatches separately (e.g. "Product Ops" vs. "Program Management").
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml


def _present(keyword: str, text_lower: str) -> bool:
    kw = keyword.strip().lower()
    if not kw:
        return False
    # Word-boundary match that also works for multi-word and hyphenated terms.
    pattern = r"(?<!\w)" + re.escape(kw) + r"(?!\w)"
    return re.search(pattern, text_lower) is not None


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
