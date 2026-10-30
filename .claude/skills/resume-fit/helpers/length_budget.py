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

The model is a vertical-height sum built from Word's own layout rules, measured
in Word (2026-10-09, four real resumes, 81 paragraph pairs, max residual 1.8pt):
- a rendered line is `pt * CALIBRI_LINE_EM * line_spacing` tall (Word's "single"
  line for Calibri is ~1.22 em; "multiple 1.05" scales that, not the font size);
- the gap between two paragraphs is max(previous space_after, this
  space_before): Word does not add the two;
- usable page height is the physical page minus both margins. No fitted
  constant: the old 8.535in "usable height" was a fudge that hid a ~24% per-line
  under-count and under-estimated every resume but the one it was fitted to.
Body text and bullets WRAP: a line longer than the usable text width consumes
multiple rendered lines (this part was always accurate to within one line).

Word is the ground truth. This estimate ranks sections by cost and gives a
quick read; `word_pages.py` gives the real page count and decides "fits".
"""
from __future__ import annotations

import re
from pathlib import Path

import tags

# --- Page geometry (US Letter) -------------------------------------------------
PAGE_WIDTH_IN = 8.5
PAGE_HEIGHT_IN = 11.0
DEFAULT_MARGIN_IN = 0.6  # render_docx.py default; --margin overrides both

# render_docx.py font metrics (Calibri). Average character advance width is
# empirically typical for Calibri: ~0.46 * pt for avg char width.
CHAR_W_PER_PT = 0.0064   # inches of horizontal advance per char, per body pt

# Must match render_docx.py (line_spacing and space_after on Normal).
RENDER_LINE_SPACING = 1.05
CALIBRI_LINE_EM = 1.2    # Word "single" line height for Calibri, in em (measured: 13.84pt pitch at 11pt x 1.05)
SPACE_AFTER_PT = 2

BODY_PT = 11
H1_PT = 20
H2_PT = 13

# space_before per element, in points (render_docx.py). The gap above an
# element is max(SPACE_AFTER_PT, this), per Word's paragraph-spacing rule.
SPACE_BEFORE_PT = {"h1": 0, "h2": 10, "h3": 6, "para": 0, "bullet": 0}

# Bullets are indented, so their usable text width is narrower than body.
BULLET_INDENT_IN = 0.25


def usable_page_height_in(margin_in: float = DEFAULT_MARGIN_IN) -> float:
    return PAGE_HEIGHT_IN - 2 * margin_in


# Kept for importers; the value at the default margin.
USABLE_PAGE_HEIGHT_IN = usable_page_height_in()


def _char_w(pt: float) -> float:
    return CHAR_W_PER_PT * pt


def _line_h(pt: float) -> float:
    return pt * CALIBRI_LINE_EM * RENDER_LINE_SPACING / 72


def _gap_above(kind: str) -> float:
    return max(SPACE_AFTER_PT, SPACE_BEFORE_PT[kind]) / 72


def _wrapped_lines(text: str, usable_width_in: float, pt: int) -> int:
    """How many rendered lines `text` wraps to at the given font size/width."""
    if not text:
        return 1
    chars_per_line = max(1, int(usable_width_in / _char_w(pt)))
    # ceil division; assume greedy word wrap ~= char wrap for estimation
    return max(1, -(-len(text) // chars_per_line))


def _classify(line: str, body_pt: float = BODY_PT):
    """Return (kind, visible_text, font_pt) for a markdown line, or None to skip."""
    s = line.rstrip()
    if not s.strip() or s.strip() == "---":
        return None
    if s.startswith("# "):
        return ("h1", s[2:].strip(), H1_PT)
    if s.startswith("## "):
        return ("h2", s[3:].strip(), H2_PT)
    if s.startswith("### "):
        return ("h3", s[4:].strip(), body_pt)  # bold, body size (render_docx.py)
    if re.match(r"^[-*] ", s):
        return ("bullet", s[2:].strip(), body_pt)
    return ("para", s.strip(), body_pt)


def _strip_md(text: str) -> str:
    """Drop **/* markers so width is measured on visible glyphs."""
    return re.sub(r"\*\*(.+?)\*\*|\*(.+?)\*", lambda m: m.group(1) or m.group(2), text)


def elements(md_text: str, margin_in: float = DEFAULT_MARGIN_IN,
             body_pt: float = BODY_PT) -> list:
    """Per-element layout: kind, visible text, rendered lines, height (inches).

    Lines tagged [REMOVED] are skipped and [CHANGED] is stripped (tags.live_text).
    Height = wrapped lines * line height + the gap above the element (none for
    the first element, which sits at the top margin). Shared with
    whitespace_check.py so both helpers measure the same layout.
    """
    text_width = PAGE_WIDTH_IN - 2 * margin_in
    bullet_width = text_width - BULLET_INDENT_IN
    out = []
    for raw in tags.live_text(md_text).splitlines():
        c = _classify(raw, body_pt)
        if c is None:
            continue
        kind, vis, pt = c
        vis = _strip_md(vis)
        width = bullet_width if kind == "bullet" else text_width
        n = _wrapped_lines(vis, width, pt)
        h = n * _line_h(pt) + (_gap_above(kind) if out else 0.0)
        out.append({"kind": kind, "text": vis, "lines": n, "height_in": h})
    return out


def estimate(md_text: str, margin_in: float = DEFAULT_MARGIN_IN,
             body_pt: float = BODY_PT) -> dict:
    """Estimate rendered height (inches) and pages, with a per-section breakdown.

    Sections are delimited by H2/H3 headings; height accrues to the current
    section so the finishing loop can show where the pages are going.
    """
    total_h = 0.0
    sections: list[dict] = []
    current = {"heading": "(top)", "height_in": 0.0, "lines": 0}

    for e in elements(md_text, margin_in, body_pt):
        if e["kind"] in ("h2", "h3"):
            if current["lines"]:
                sections.append(current)
            current = {"heading": e["text"], "height_in": 0.0, "lines": 0}
        total_h += e["height_in"]
        current["height_in"] += e["height_in"]
        current["lines"] += e["lines"]

    if current["lines"]:
        sections.append(current)

    usable = usable_page_height_in(margin_in)
    pages = total_h / usable
    return {
        "margin_in": margin_in,
        "body_pt": body_pt,
        "total_height_in": round(total_h, 2),
        "usable_page_height_in": round(usable, 3),
        "estimated_pages": round(pages, 2),
        "sections": [
            {"heading": s["heading"],
             "height_in": round(s["height_in"], 2),
             "rendered_lines": s["lines"]}
            for s in sections
        ],
    }


REVIEW_DECISIONS = ("keep", "compress", "cut")


def review_status(sections: list, review: dict | None) -> dict:
    """Has every section been given a keep/compress/cut decision?

    Closes a process gap: the length round is supposed to weigh cost vs. value
    for EVERY section before anything is cut, and in practice sections were
    skipped. The review file (`length_review.yaml`) maps each section heading to
    a decision, either `heading: keep` or `heading: {decision: cut, note: ...}`.
    Still value-blind: this checks the review is complete, not what it decided.
    """
    review = review or {}
    missing, invalid = [], []
    for s in sections:
        h = s["heading"]
        entry = review.get(h)
        decision = entry.get("decision") if isinstance(entry, dict) else entry
        if decision is None:
            missing.append(h)
        elif decision not in REVIEW_DECISIONS:
            invalid.append({"heading": h, "decision": decision})
    return {"complete": not missing and not invalid, "missing": missing, "invalid": invalid}


OVERRIDE_KEY = "override"


# Above this many estimated pages the resume has a real third page. No ATS page
# penalty was found (TODO #23; guidance R4), but two pages are preferred for
# experienced roles, so a third page must carry unique, relevant evidence.
THIRD_PAGE_AT = 2.5


# Within this many pages under the budget the estimate is too close to call
# (Word's page breaks waste a little space the continuous model cannot see):
# confirm with word_pages.py before treating the draft as fitting.
BORDERLINE_PAGES = 0.05


def check(md_text: str, max_pages: float = 2.0, margin_in: float = DEFAULT_MARGIN_IN,
          review: dict | None = None, reason: str | None = None,
          body_pt: float = BODY_PT) -> dict:
    est = estimate(md_text, margin_in=margin_in, body_pt=body_pt)
    est["max_pages"] = max_pages
    est["fits"] = est["estimated_pages"] <= max_pages
    est["borderline"] = est["fits"] and est["estimated_pages"] > max_pages - BORDERLINE_PAGES
    est["over_pages"] = round(max(0.0, est["estimated_pages"] - max_pages), 2)
    est["third_page"] = est["estimated_pages"] > THIRD_PAGE_AT
    est["reason"] = (reason or "").strip() or None
    est["override_recorded"] = (not est["fits"]) and est["reason"] is not None
    if not est["fits"]:
        # Every section must be surveyed before any cut or override.
        est["review_checklist"] = [s["heading"] for s in est["sections"]]
        est["review"] = review_status(est["sections"], review)
    return est


def check_file(path, max_pages: float = 2.0, margin_in: float = DEFAULT_MARGIN_IN,
               review_path=None, reason: str | None = None,
               body_pt: float = BODY_PT) -> dict:
    review = None
    if review_path:
        import yaml

        review = yaml.safe_load(Path(review_path).read_text(encoding="utf-8")) or {}
        # The review file also holds the length decision's override, so one
        # file records the whole round: `override: {reason: ..., open_flags: [...]}`.
        override = review.pop(OVERRIDE_KEY, None)
        if reason is None and override:
            reason = override.get("reason") if isinstance(override, dict) else str(override)
    return check(Path(path).read_text(encoding="utf-8"), max_pages=max_pages,
                 margin_in=margin_in, review=review, reason=reason, body_pt=body_pt)


if __name__ == "__main__":
    import argparse
    import json

    ap = argparse.ArgumentParser(description="Estimate resume page length (advisory).")
    ap.add_argument("path")
    ap.add_argument("--max-pages", type=float, default=2.0)
    ap.add_argument("--margin", type=float, default=DEFAULT_MARGIN_IN,
                    help="page margin in inches; must match render_docx.py --margin")
    ap.add_argument("--body-pt", type=float, default=BODY_PT,
                    help="body font size; must match render_docx.py --body-pt")
    ap.add_argument("--review", metavar="LENGTH_REVIEW_YAML",
                    help="per-section keep/compress/cut decisions to check for completeness")
    ap.add_argument("--reason", metavar="TEXT",
                    help="why the resume may exceed the page target; a third page "
                         "must name unique, relevant evidence")
    args = ap.parse_args()

    from console import utf8_stdout

    utf8_stdout()
    result = check_file(args.path, max_pages=args.max_pages, margin_in=args.margin,
                        review_path=args.review, reason=args.reason, body_pt=args.body_pt)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result["borderline"]:
        print(f"BORDERLINE: ~{result['estimated_pages']} pages is within "
              f"{BORDERLINE_PAGES} of the budget; confirm with word_pages.py.")
    if not result["fits"]:
        print(f"OVER BUDGET: ~{result['estimated_pages']} pages "
              f"(target {result['max_pages']}); over by ~{result['over_pages']}.")
        if result["third_page"]:
            print("THIRD PAGE: keep it only if it carries unique, relevant evidence; "
                  "state which evidence in --reason.")
        if not result["review"]["complete"]:
            print(f"REVIEW INCOMPLETE: {len(result['review']['missing'])} sections "
                  "lack a keep/compress/cut decision. Decide every section in "
                  "length_review.yaml before cutting or overriding.")
        if result["override_recorded"]:
            print(f"OVERRIDE RECORDED: {result['reason']}")
        else:
            # Advisory, non-zero exit so the loop notices; NOT a hard block.
            print("Advisory only -- record a reason (--reason, or `override:` in "
                  "length_review.yaml) to override.")
            raise SystemExit(2)
