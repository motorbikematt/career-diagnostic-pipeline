"""Tests for the advisory page-length estimator (length_budget.py).

The estimator is a *cost meter*: it measures rendered inches/pages and produces a
per-section breakdown. It must never fail closed (it's advisory) and must stay
value-blind (no cut recommendations in its output).
"""
import length_budget


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


def test_calibration_against_observed_ground_truth():
    """Anthropic resume_candidate.md (rev8) is a user-confirmed real 2-page
    document in Word, rendered with the CURRENT render_docx.py template (0.6in
    margins, 2pt space_after, 1.05 line spacing). The estimator must reproduce
    that within tight tolerance -- this pins USABLE_PAGE_HEIGHT_IN and
    LINE_H_PER_PT together so a future template change (e.g. re-tightening
    render_docx.py without updating this model) can't silently drift them out of
    sync again, which previously caused a 38% total-height miscalibration that
    went undetected until checked against this exact ground truth."""
    from pathlib import Path

    p = Path(
        "D:/vibe/resume-pipeline-data/pipeline/runs/"
        "anthropic-product-manager-api-growth-2026-07-06/resume_candidate.md"
    )
    if not p.exists():
        import pytest
        pytest.skip("data-plane Anthropic run not present")
    est = length_budget.check_file(p, max_pages=2, margin_in=0.6)
    assert 1.85 <= est["estimated_pages"] <= 2.15
