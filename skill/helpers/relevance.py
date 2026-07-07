"""Line-level JD-relevance meter -- the inverse of score.py.

Where score.py walks REQUIREMENTS -> evidence ("does the JD's ask have proof?"),
this walks RESUME ELEMENTS -> JD linkage ("does this line I already have map to
anything the JD wants?"). A resume line with zero JD linkage is structurally
invisible to the requirement-indexed pipeline; this surfaces it.

VALUE-BLIND BY DESIGN: this meters linkage only. It never says "cut" or "keep" --
the model proposes dead-weight vs differentiator and the user ratifies. (Same
discipline as length_budget.py: Python computes the signal, humans own judgment.)

PER-JD BY CONSTRUCTION: the linkage vocabulary comes ENTIRELY from this run's
requirements.yaml (ats_keywords, keywords) and gapmap.yaml (jd_keywords,
resume_evidence). There is NO hardcoded list of "usually irrelevant" sections. The
same line scores `none` against a JD whose keywords it doesn't touch and `strong`
against one it does -- the flag is a pure function of the JD supplied.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

# Reuse the element parser and the synonym-aware keyword matcher already written --
# do not duplicate that logic.
from length_budget import _classify, _strip_md
from ats import _present

# Tokens too generic to carry linkage signal on their own.
_STOPWORDS = {
    "the", "and", "a", "an", "of", "to", "in", "for", "on", "with", "at", "by",
    "from", "as", "is", "was", "were", "an", "or", "that", "this", "it", "its",
    "i", "my", "me", "we", "our", "across", "through", "into", "each", "all",
}


def _tokens(text: str) -> set:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w for w in words if len(w) > 2 and w not in _STOPWORDS}


def _jd_keywords(requirements: dict, gapmap: dict) -> list:
    """The JD's keyword vocabulary, drawn only from this run's files."""
    kws: list = []
    if isinstance(gapmap, dict):
        kws += (gapmap.get("ats", {}) or {}).get("jd_keywords", []) or []
    if isinstance(requirements, dict):
        kws += requirements.get("ats_keywords", []) or []
        for group in ("hard_requirements", "preferred_requirements"):
            for r in requirements.get(group, []) or []:
                kws += r.get("keywords", []) or []
    # de-dup, preserve order
    seen, out = set(), []
    for k in kws:
        kl = k.strip().lower()
        if kl and kl not in seen:
            seen.add(kl)
            out.append(k)
    return out


def _evidence_index(gapmap: dict, overlap_min: int = 2) -> list:
    """Per-requirement (id, evidence-token-set). An element 'links' to a
    requirement when it shares >= overlap_min meaningful tokens with the
    requirement's resume_evidence string (evidence is a paraphrase, so token
    overlap, not exact match)."""
    idx = []
    for r in gapmap.get("requirements", []) if isinstance(gapmap, dict) else []:
        ev = r.get("resume_evidence")
        if ev:
            idx.append((r["id"], _tokens(ev)))
    return idx


def score_element(text: str, jd_keywords: list, evidence_idx: list,
                  overlap_min: int = 2) -> dict:
    tl = text.lower()
    ats_hits = [k for k in jd_keywords if _present(k, tl)]
    el_tokens = _tokens(text)
    linked = [
        rid for rid, ev_tokens in evidence_idx
        if len(el_tokens & ev_tokens) >= overlap_min
    ]
    if ats_hits and linked:
        linkage = "strong"
    elif ats_hits or linked:
        linkage = "weak"
    else:
        linkage = "none"
    return {
        "text": text,
        "ats_hits": ats_hits,
        "linked_requirements": linked,
        "linkage": linkage,
    }


# Element kinds that carry claim content worth scoring (skip headers/contact).
_SCORED_KINDS = {"bullet", "para"}

# Location/date lines and contact lines are structural, not claims -- a city or a
# date range carries no JD linkage by nature and is never a "cut this" decision.
# Skip a para that is dominated by a date range or reads as a contact/location line.
_DATE_RE = re.compile(
    r"\b(19|20)\d{2}\b|\bpresent\b|"
    r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)"
    r"(uary|ruary|ch|il|e|y|ust|tember|ober|ember)?\b",
    re.IGNORECASE,
)
_CONTACT_RE = re.compile(r"@|linkedin\.com|\bhttps?://|\(\d{3}\)|\b\d{3}[.\-]\d{3}[.\-]\d{4}\b",
                         re.IGNORECASE)


# "City, ST" at the very start of a line marks a location/date header line.
_LOCATION_RE = re.compile(r"^[A-Z][A-Za-z.\s]+,\s*[A-Z]{2}\b")


def _is_structural(text: str) -> bool:
    """True for location/date and contact lines -- structural, not a claim."""
    if _CONTACT_RE.search(text):
        return True
    # A line that opens with "City, ST" and carries a date range is a role's
    # location/date header (with or without a parenthetical like "(Hybrid)"), and
    # is not a claim to be scored -- UNLESS an em-dash intro was folded onto it
    # (rev-style "City, ST | dates — led three pods..."), which we keep.
    head = text.split("—", 1)[0]  # portion before an em-dash intro, if any
    if _LOCATION_RE.match(head) and _DATE_RE.search(head):
        if "—" not in text:  # no folded intro -> pure header line, skip
            return True
    # Fallback: short pipe-delimited date line with no claim content.
    if "|" in text and _DATE_RE.search(text) and len(_tokens(text)) <= 8:
        return True
    # A short line that is predominantly a date range (e.g. "2020 - Present",
    # "January 2019 - December 2022") with no folded intro is a header line.
    if "—" not in text and _DATE_RE.search(text) and len(_tokens(text)) <= 4:
        non_date = _tokens(_DATE_RE.sub(" ", text))
        if len(non_date) <= 1:  # essentially nothing but the date
            return True
    return False


def analyze(resume_md: str, requirements: dict, gapmap: dict) -> dict:
    jd_keywords = _jd_keywords(requirements, gapmap)
    evidence_idx = _evidence_index(gapmap)

    elements = []
    for raw in resume_md.splitlines():
        c = _classify(raw)
        if c is None:
            continue
        kind, vis, _pt = c
        if kind not in _SCORED_KINDS:
            continue
        vis = _strip_md(vis)
        if len(_tokens(vis)) < 2:  # too short to score meaningfully
            continue
        if _is_structural(vis):  # location/date/contact -- not a claim
            continue
        el = score_element(vis, jd_keywords, evidence_idx)
        el["kind"] = kind
        elements.append(el)

    counts = {"strong": 0, "weak": 0, "none": 0}
    for e in elements:
        counts[e["linkage"]] += 1

    return {
        "jd_keyword_count": len(jd_keywords),
        "element_count": len(elements),
        "counts": counts,
        "none_linkage": [e["text"] for e in elements if e["linkage"] == "none"],
        "elements": elements,
    }


def analyze_files(resume_path, requirements_path, gapmap_path) -> dict:
    resume = Path(resume_path).read_text(encoding="utf-8")
    req = yaml.safe_load(Path(requirements_path).read_text(encoding="utf-8"))
    gm = yaml.safe_load(Path(gapmap_path).read_text(encoding="utf-8"))
    return analyze(resume, req, gm)


if __name__ == "__main__":
    import argparse
    import json

    ap = argparse.ArgumentParser(
        description="Line-level JD-relevance meter (value-blind, per-JD).")
    ap.add_argument("resume")
    ap.add_argument("requirements")
    ap.add_argument("gapmap")
    ap.add_argument("--none-only", action="store_true",
                    help="print only the none-linkage element texts")
    args = ap.parse_args()

    result = analyze_files(args.resume, args.requirements, args.gapmap)
    if args.none_only:
        for t in result["none_linkage"]:
            print(f"none  {t}")
    else:
        print(json.dumps(result, indent=2))
