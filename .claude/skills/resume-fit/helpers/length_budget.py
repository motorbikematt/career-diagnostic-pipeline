"""Deterministic page-length estimator + advisory budget check.

Page count is NOT stored in a .docx -- Word computes it at render time from
content, font metrics, margins, and line wrapping. So this helper *models* the
layout of `render_docx.py` output and estimates the rendered page count from the
resume markdown, plus a per-section breakdown that drives the interactive
finishing-loop overflow round.

Policy (user decision): 2 pages is the DEFAULT target, not a hard cap. This
helper WARNS on overflow (advisory exit code) -- it never blocks the render. A
run may exceed 2 pages when the user records a reason; the finishing loop, not
this helper, owns that override.

The model is a vertical-height sum. Each markdown element consumes a known
vertical height in inches (heading sizes + spacing mirror render_docx.py). Body
text and bullets WRAP: a line longer than the usable text width consumes
multiple rendered lines. Free constant `USABLE_PAGE_HEIGHT_IN` is calibrated so
the real Anthropic resume_final.md estimates ~4 pages at 0.5in margins (the
ground truth the user observed), which the tightened 0.6in template + content
cuts then bring to 2.
"""
from __future__ import annotations

import re
from pathlib import Path

# --- Page geometry (US Letter) -------------------------------------------------
PAGE_WIDTH_IN = 8.5
PAGE_HEIGHT_IN = 11.0

# render_docx.py font metrics (Calibri). Average character advance width is
# empirically typical for Calibri: ~0.46 * pt for avg char width.
CHAR_W_PER_PT = 0.0064   # inches of horizontal advance per char, per body pt

# Line height DERIVED from render_docx.py's actual line_spacing (1.05), not a
# separate empirical guess -- these two numbers drifted out of sync once before
# (line-spacing was tightened in render_docx.py without updating this constant,
# causing a ~13%-per-line overshoot that compounded into a 38% total-height
# miscalibration, caught by comparing against a real confirmed page count).
RENDER_LINE_SPACING = 1.05  # must match render_docx.py's normal_para.line_spacing
LINE_H_PER_PT = RENDER_LINE_SPACING / 72  # inches of line height per font pt

BODY_PT = 11
H1_PT = 20
H2_PT = 13
H3_PT = BODY_PT  # bold, same size as body in render_docx.py

# Vertical space each element adds ON TOP of its own text line height (spacing
# before/paragraph gaps), in inches -- mirrors render_docx.py spacing.
SPACE_BEFORE = {"h1": 0.02, "h2": 10 / 72, "h3": 6 / 72, "para": 0.02, "bullet": 0.02}

# Bullets are indented, so their usable text width is narrower than body.
BULLET_INDENT_IN = 0.25

# Calibrated against a SECOND, independent real ground-truth point: the
# Anthropic resume_candidate.md (rev8) is a user-confirmed real 2-page document
# in Word, rendered with the CURRENT (tightened) render_docx.py template --
# 0.6in margins, 2pt space_after, 1.05 line spacing. With the corrected
# LINE_H_PER_PT above (previously stale after the template was tightened, which
# caused a 38% total-height overshoot caught by comparing against this same
# ground truth), total modeled height is 17.07in for a real 2-page doc:
# 17.07 / 2 = 8.535 usable in/page. The ~1.5in/page overhead vs the 10in
# physical usable height (at 0.6in margins) is heading gaps + paragraph spacing,
# which the element model deliberately keeps simple rather than replicating
# Word's layout engine exactly.
#
# History: the ORIGINAL calibration point (Anthropic resume_final.md, the pre-
# tightening 4-page seed at 0.5in margins) is kept as a regression check in
# tests -- see test_length_budget.py -- but is no longer the fitted constant,
# since it was calibrated against a render template that no longer exists.
USABLE_PAGE_HEIGHT_IN = 8.535


def _char_w(pt: int) -> float:
    return CHAR_W_PER_PT * pt


def _line_h(pt: int) -> float:
    return LINE_H_PER_PT * pt


def _wrapped_lines(text: str, usable_width_in: float, pt: int) -> int:
    """How many rendered lines `text` wraps to at the given font size/width."""
    if not text:
        return 1
    chars_per_line = max(1, int(usable_width_in / _char_w(pt)))
    # ceil division; assume greedy word wrap ~= char wrap for estimation
    return max(1, -(-len(text) // chars_per_line))


def _classify(line: str):
    """Return (kind, visible_text, font_pt) for a markdown line, or None to skip."""
    s = line.rstrip()
    if not s.strip() or s.strip() == "---":
        return None
    if s.startswith("# "):
        return ("h1", s[2:].strip(), H1_PT)
    if s.startswith("## "):
        return ("h2", s[3:].strip(), H2_PT)
    if s.startswith("### "):
        return ("h3", s[4:].strip(), H3_PT)
    if re.match(r"^[-*] ", s):
        return ("bullet", s[2:].strip(), BODY_PT)
    return ("para", s.strip(), BODY_PT)


def _strip_md(text: str) -> str:
    """Drop **/* markers so width is measured on visible glyphs."""
    return re.sub(r"\*\*(.+?)\*\*|\*(.+?)\*", lambda m: m.group(1) or m.group(2), text)


def estimate(md_text: str, margin_in: float = 0.6) -> dict:
    """Estimate rendered height (inches) and pages, with a per-section breakdown.

    Sections are delimited by H2/H3 headings; height accrues to the current
    section so the finishing loop can show where the pages are going.
    """
    text_width = PAGE_WIDTH_IN - 2 * margin_in
    bullet_width = text_width - BULLET_INDENT_IN

    total_h = 0.0
    sections: list[dict] = []
    current = {"heading": "(top)", "height_in": 0.0, "lines": 0}

    for raw in md_text.splitlines():
        c = _classify(raw)
        if c is None:
            continue
        kind, vis, pt = c
        vis = _strip_md(vis)

        if kind in ("h2", "h3"):
            if current["lines"]:
                sections.append(current)
            current = {"heading": vis, "height_in": 0.0, "lines": 0}

        width = bullet_width if kind == "bullet" else text_width
        rendered_lines = _wrapped_lines(vis, width, pt)
        h = rendered_lines * _line_h(pt) + SPACE_BEFORE[kind]

        total_h += h
        current["height_in"] += h
        current["lines"] += rendered_lines

    if current["lines"]:
        sections.append(current)

    pages = total_h / USABLE_PAGE_HEIGHT_IN
    return {
        "margin_in": margin_in,
        "total_height_in": round(total_h, 2),
        "usable_page_height_in": USABLE_PAGE_HEIGHT_IN,
        "estimated_pages": round(pages, 2),
        "sections": [
            {"heading": s["heading"],
             "height_in": round(s["height_in"], 2),
             "rendered_lines": s["lines"]}
            for s in sections
        ],
    }


def check(md_text: str, max_pages: float = 2.0, margin_in: float = 0.6) -> dict:
    est = estimate(md_text, margin_in=margin_in)
    est["max_pages"] = max_pages
    est["fits"] = est["estimated_pages"] <= max_pages + 0.05  # small tolerance
    est["over_pages"] = round(max(0.0, est["estimated_pages"] - max_pages), 2)
    return est


def check_file(path, max_pages: float = 2.0, margin_in: float = 0.6) -> dict:
    return check(Path(path).read_text(encoding="utf-8"),
                 max_pages=max_pages, margin_in=margin_in)


if __name__ == "__main__":
    import argparse
    import json

    ap = argparse.ArgumentParser(description="Estimate resume page length (advisory).")
    ap.add_argument("path")
    ap.add_argument("--max-pages", type=float, default=2.0)
    ap.add_argument("--margin", type=float, default=0.6,
                    help="page margin in inches (render_docx.py uses 0.6)")
    args = ap.parse_args()

    result = check_file(args.path, max_pages=args.max_pages, margin_in=args.margin)
    print(json.dumps(result, indent=2))
    if not result["fits"]:
        print(f"OVER BUDGET: ~{result['estimated_pages']} pages "
              f"(target {result['max_pages']}); over by ~{result['over_pages']}. "
              f"Advisory only -- record a reason to override.")
        # Advisory, non-zero exit so the loop notices; NOT a hard block.
        raise SystemExit(2)
