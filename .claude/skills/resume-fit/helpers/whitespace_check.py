"""Page-fullness / whitespace-ratio check (deterministic, research-grounded).

Distinct from length_budget.py: that helper counts PAGES (does this fit in N
pages). This helper measures DENSITY WITHIN a page -- what fraction of each
page's available height is filled with ink (headings/bullets/paragraphs) vs.
whitespace (blank space, inter-element spacing).

Grounded in resume-readability research (not house style): recruiters read in an
F-pattern and form an impression in ~7 seconds; a page-long "wall of text" with
no whitespace measurably impairs comprehension (Wichita State research found
whitespace around text blocks can improve reading comprehension up to 20%).
Cluttered layout + lack of whitespace + long unbroken sentences are named
together in the literature as what does NOT work for a human reader -- this is a
readability check, not a style preference.

IMPORTANT -- explicitly NOT a bullet-length-uniformity check. AI-text-detection
research shows uniform sentence/bullet length (low "burstiness") is itself a
signal of machine-generated text; human writing has natural variance. So this
helper never nudges bullet lengths toward a resume's own median -- that would
push the text toward LESS authentic, not more readable. It only measures
per-page fullness, which is a layout property, not a style-uniformity property.

VALUE-BLIND: reports a fullness ratio per page; does not prescribe which lines
to shorten, split, or reflow. That's a model/user judgment call, same as every
other helper in this pipeline.
"""
from __future__ import annotations

from pathlib import Path

from length_budget import (
    PAGE_HEIGHT_IN,
    USABLE_PAGE_HEIGHT_IN,
    _classify,
    _strip_md,
    _line_h,
    _wrapped_lines,
    PAGE_WIDTH_IN,
    BULLET_INDENT_IN,
    BODY_PT,
    SPACE_BEFORE,
)

# Research-grounded band, not an arbitrary cutoff: below ~55% full a page can
# start to look sparse/unfinished; above ~85% full it reads as a dense
# "wall of text" the literature associates with worse comprehension and a
# harder recruiter scan. The band, not a single number, is what's checked.
DENSE_THRESHOLD = 0.85
SPARSE_THRESHOLD = 0.55


def _element_stats(md_text: str, margin_in: float) -> list:
    """Per-element (height_in, word_count) -- reuses length_budget's exact
    element model so this check stays consistent with the page estimator."""
    text_width = PAGE_WIDTH_IN - 2 * margin_in
    bullet_width = text_width - BULLET_INDENT_IN
    stats = []
    for raw in md_text.splitlines():
        c = _classify(raw)
        if c is None:
            continue
        kind, vis, pt = c
        vis = _strip_md(vis)
        width = bullet_width if kind == "bullet" else text_width
        rendered_lines = _wrapped_lines(vis, width, pt)
        h = rendered_lines * _line_h(pt) + SPACE_BEFORE[kind]
        stats.append({"height_in": h, "words": len(vis.split()), "chars": len(vis)})
    return stats


def analyze(md_text: str, margin_in: float = 0.6) -> dict:
    stats = _element_stats(md_text, margin_in)
    total_h = sum(s["height_in"] for s in stats)

    # Walk elements, accumulating into pages of USABLE_PAGE_HEIGHT_IN each --
    # mirrors how length_budget.py turns total height into a page count, but
    # keeps the per-page breakdown instead of collapsing to one number.
    # CAVEAT (loud, not buried): this per-page boundary is APPROXIMATE. A greedy
    # bucket walk on a derived height model cannot reproduce Word's actual layout
    # engine exactly -- small rounding can spill a sliver of content into a
    # phantom extra "page" that doesn't exist in the real render. Confirmed on
    # real data: this walk once produced a near-empty page 3 for a document that
    # is a genuine, user-confirmed 2-page document in Word. TREAT PAGE-LEVEL
    # ASSIGNMENT AS ILLUSTRATIVE ONLY -- always sanity-check against the real
    # rendered docx by eye, never act on the per-page split alone. The raw
    # word/char counts below are reported precisely so they can be independently
    # verified (e.g. against Word's own word-count tool) rather than trusting
    # this tool's derived ratio on faith.
    pages = []
    current = {"height_in": 0.0, "words": 0, "chars": 0}
    for s in stats:
        if current["height_in"] + s["height_in"] > USABLE_PAGE_HEIGHT_IN and current["height_in"] > 0:
            pages.append(current)
            current = {"height_in": 0.0, "words": 0, "chars": 0}
        current["height_in"] += s["height_in"]
        current["words"] += s["words"]
        current["chars"] += s["chars"]
    if current["height_in"] > 0:
        pages.append(current)

    page_reports = []
    for i, p in enumerate(pages, start=1):
        ratio = round(p["height_in"] / USABLE_PAGE_HEIGHT_IN, 2)
        if ratio >= DENSE_THRESHOLD:
            verdict = "dense"
        elif ratio <= SPARSE_THRESHOLD:
            verdict = "sparse"
        else:
            verdict = "balanced"
        page_reports.append({
            "page": i,
            "fullness_ratio": ratio,
            "word_count": p["words"],
            "char_count": p["chars"],
            "verdict": verdict,
        })

    return {
        "margin_in": margin_in,
        "page_count": len(pages),
        "total_word_count": sum(s["words"] for s in stats),
        "total_char_count": sum(s["chars"] for s in stats),
        "page_boundary_caveat": (
            "Per-page assignment below is APPROXIMATE (a derived model, not "
            "Word's real layout engine) -- verify against the actual rendered "
            "docx by eye before acting on it. word_count/char_count per page "
            "are reported so they can be independently checked."
        ),
        "pages": page_reports,
        "dense_pages": [p["page"] for p in page_reports if p["verdict"] == "dense"],
        "sparse_pages": [p["page"] for p in page_reports if p["verdict"] == "sparse"],
        "balanced": all(p["verdict"] == "balanced" for p in page_reports),
    }


def analyze_file(path, margin_in: float = 0.6) -> dict:
    return analyze(Path(path).read_text(encoding="utf-8"), margin_in=margin_in)


if __name__ == "__main__":
    import argparse
    import json

    ap = argparse.ArgumentParser(
        description="Report per-page whitespace/fullness ratio (advisory).")
    ap.add_argument("path")
    ap.add_argument("--margin", type=float, default=0.6)
    args = ap.parse_args()

    result = analyze_file(args.path, margin_in=args.margin)
    print(json.dumps(result, indent=2))
    if result["dense_pages"] or result["sparse_pages"]:
        issues = []
        if result["dense_pages"]:
            issues.append(f"dense (wall-of-text risk): page(s) {result['dense_pages']}")
        if result["sparse_pages"]:
            issues.append(f"sparse (may look unfinished): page(s) {result['sparse_pages']}")
        print("WHITESPACE IMBALANCE: " + "; ".join(issues))
