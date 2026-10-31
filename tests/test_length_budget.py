"""Tests for the advisory page-length estimator (length_budget.py).

The estimator is a *cost meter*: it measures rendered inches/pages and produces a
per-section breakdown. It must never fail closed (it's advisory) and must stay
value-blind (no cut recommendations in its output).
"""
import length_budget
from conftest import data_plane_runs


SHORT = """# Jane Doe

jane@example.com | 555-0100

## Summary

Product manager with a focus on developer platforms.

## Experience

### Senior PM — Acme
2020 – Present

- Shipped an API used by thousands of developers.
- Owned the adoption funnel end to end.

## Education

- B.S., State University
"""


def _long_resume(n_roles=8, bullets_per_role=7):
    """Build an intentionally over-budget resume (many long-wrapping bullets)."""
    long_bullet = (
        "- " + "Owned the end-to-end developer adoption funnel and monetization "
        "model across a large platform, defining and tracking metrics from first "
        "API experiment through production integration and downstream engagement. "
        * 2
    )
    parts = ["# Sample Candidate", "", "contact line", "", "## Experience", ""]
    for i in range(n_roles):
        parts.append(f"### Role {i} — Company {i}")
        parts.append("2010 – 2020")
        parts.extend(long_bullet for _ in range(bullets_per_role))
        parts.append("")
    return "\n".join(parts)


def test_short_resume_fits_two_pages():
    result = length_budget.check(SHORT, max_pages=2)
    assert result["fits"] is True
    assert result["estimated_pages"] <= 2
    assert result["over_pages"] == 0


def test_long_resume_overflows():
    result = length_budget.check(_long_resume(), max_pages=2)
    assert result["fits"] is False
    assert result["estimated_pages"] > 2
    assert result["over_pages"] > 0


def test_per_section_breakdown_present():
    result = length_budget.estimate(_long_resume(n_roles=3, bullets_per_role=3))
    headings = [s["heading"] for s in result["sections"]]
    assert "Role 0 — Company 0" in headings
    assert "Role 2 — Company 2" in headings
    # every section reports both cost signals
    for s in result["sections"]:
        assert s["height_in"] > 0
        assert s["rendered_lines"] >= 1


def test_narrower_margin_wraps_more():
    """Same content at wider text width (smaller margin) should be no taller,
    and at 0.5in vs 0.6in the 0.6in (narrower text) wraps at least as much."""
    body = _long_resume(n_roles=2, bullets_per_role=3)
    wide = length_budget.estimate(body, margin_in=0.5)["total_height_in"]
    narrow = length_budget.estimate(body, margin_in=0.75)["total_height_in"]
    # Narrower text column (bigger margin) => more wrapping => >= height.
    assert narrow >= wide


def test_estimator_is_value_blind():
    """The cost meter must not emit any cut/keep recommendation — value lives in
    gapmap, not here."""
    result = length_budget.check(_long_resume(), max_pages=2)
    blob = " ".join(str(v).lower() for v in result.keys())
    for forbidden in ("cut", "keep", "drop", "recommend", "relevance"):
        assert forbidden not in blob


# --- Layout model pinned to Word measurements (2026-10-09) -------------------

def test_line_height_matches_word_measurement():
    """Word measured a 13.84pt pitch for 11pt Calibri at 1.05 line spacing
    (81 paragraph pairs, four resumes). The old model used 11.55pt, a ~24%
    per-line under-count that a fitted page-height constant only partly hid."""
    assert abs(length_budget._line_h(11) * 72 - 13.84) < 0.1


def test_paragraph_gap_is_max_not_sum():
    """Word uses max(space_after, space_before) between paragraphs, not both."""
    assert length_budget._gap_above("h2") * 72 == 10
    assert length_budget._gap_above("bullet") * 72 == length_budget.SPACE_AFTER_PT


def test_usable_height_is_physical_page_minus_margins():
    assert length_budget.usable_page_height_in(0.6) == 11.0 - 1.2
    assert length_budget.usable_page_height_in(0.5) == 10.0


def test_smaller_body_font_is_shorter():
    body = _long_resume(n_roles=2, bullets_per_role=3)
    at_11 = length_budget.estimate(body, body_pt=11)["total_height_in"]
    at_10_5 = length_budget.estimate(body, body_pt=10.5)["total_height_in"]
    assert at_10_5 < at_11


def test_no_tolerance_over_budget_and_borderline_flag():
    """`fits` has no slack above the budget; just under it is flagged
    borderline so the loop confirms with word_pages.py."""
    r = length_budget.check(SHORT, max_pages=2)
    assert r["borderline"] is False
    tiny_budget = length_budget.estimate(SHORT)["estimated_pages"]
    r = length_budget.check(SHORT, max_pages=tiny_budget + 0.01)
    assert r["fits"] is True and r["borderline"] is True
    assert length_budget.check(SHORT, max_pages=tiny_budget - 0.01)["fits"] is False


def test_against_word_ground_truth():
    """Four real resumes, frozen in the data plane's fixtures with the page
    positions Word measured (word_measurements.yaml). The old model estimated
    Qualcomm at 1.99 and called it fitting when Word printed 3 pages; every
    estimate must now land within 0.1 page of Word."""
    import pytest
    import yaml

    gt = data_plane_runs().parent / "fixtures" / "word_ground_truth"
    if not gt.exists():
        pytest.skip("data-plane Word ground-truth fixtures not present")
    truth = yaml.safe_load((gt / "word_measurements.yaml").read_text(encoding="utf-8"))
    for name, m in truth.items():
        est = length_budget.estimate((gt / f"{name}.md").read_text(encoding="utf-8"))
        assert abs(est["estimated_pages"] - m["fractional_pages"]) <= 0.1, (name, est["estimated_pages"])


# --- Section review completeness (TODO #8) ---------------------------------

def test_over_budget_emits_checklist_and_incomplete_review():
    r = length_budget.check(_long_resume(), max_pages=2)
    assert r["fits"] is False
    assert r["review_checklist"] == [s["heading"] for s in r["sections"]]
    assert r["review"]["complete"] is False
    assert r["review"]["missing"] == r["review_checklist"]


def test_complete_review_passes_and_bad_decision_is_invalid():
    first = length_budget.check(_long_resume(), max_pages=2)
    review = {h: "keep" for h in first["review_checklist"]}
    assert length_budget.check(_long_resume(), max_pages=2, review=review)["review"]["complete"]

    h0 = first["review_checklist"][0]
    review[h0] = {"decision": "shrink", "note": "?"}
    status = length_budget.check(_long_resume(), max_pages=2, review=review)["review"]
    assert status["complete"] is False
    assert status["invalid"] == [{"heading": h0, "decision": "shrink"}]


def test_review_file_override_records_the_reason(tmp_path):
    """One file records the whole length round: section decisions plus the
    override, which is never mistaken for a section heading."""
    import yaml

    md = tmp_path / "r.md"
    md.write_text(_long_resume(), encoding="utf-8")
    first = length_budget.check(_long_resume(), max_pages=2)
    review = {h: "keep" for h in first["review_checklist"]}
    review["override"] = {"reason": "publications list is the evidence", "open_flags": []}
    rp = tmp_path / "length_review.yaml"
    rp.write_text(yaml.safe_dump(review), encoding="utf-8")
    r = length_budget.check_file(md, max_pages=2, review_path=rp)
    assert r["override_recorded"] is True
    assert r["reason"] == "publications list is the evidence"
    assert r["review"]["complete"] is True


def test_fitting_resume_has_no_review_gate():
    r = length_budget.check(SHORT, max_pages=2)
    assert r["fits"] is True
    assert "review" not in r


# --- Page-three reason (TODO #23) -------------------------------------------

def test_over_budget_without_reason_records_no_override():
    r = length_budget.check(_long_resume(), max_pages=2)
    assert r["override_recorded"] is False
    assert r["reason"] is None


def test_reason_records_override_and_blank_reason_does_not():
    r = length_budget.check(_long_resume(), max_pages=2, reason="patents are unique evidence")
    assert r["override_recorded"] is True
    assert r["reason"] == "patents are unique evidence"
    blank = length_budget.check(_long_resume(), max_pages=2, reason="   ")
    assert blank["override_recorded"] is False


def test_third_page_flag_only_above_two_and_a_half_pages():
    assert length_budget.check(SHORT)["third_page"] is False
    big = length_budget.check(_long_resume())
    assert big["estimated_pages"] > length_budget.THIRD_PAGE_AT
    assert big["third_page"] is True


def test_fitting_resume_never_records_override():
    r = length_budget.check(SHORT, reason="irrelevant")
    assert r["override_recorded"] is False


def test_removed_lines_and_changed_tags_do_not_count_toward_height():
    base = "# Jane\n\n## Experience\n\n- " + "kept bullet " * 5 + "\n"
    tagged = base.replace("- kept", "- [CHANGED] kept") + "- [REMOVED] " + "dead line " * 40 + "\n"
    assert length_budget.estimate(tagged) == length_budget.estimate(base)
