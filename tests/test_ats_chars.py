"""Tests for the ATS-unsafe character scanner (ats_chars.py).

This is a fixed, mechanical rule (not a style/judgment check): certain Unicode
characters are documented ATS parsing failure points regardless of content or JD.
"""
import ats_chars


def test_clean_text_reports_clean():
    text = "# Jane Doe\n\n- Led the team - shipped the thing.\n- Owned it end to end.\n"
    result = ats_chars.scan(text)
    assert result["clean"] is True
    assert result["violation_count"] == 0


def test_em_dash_flagged_with_line_number():
    text = "# Jane Doe\n\n- Led the team — shipped results.\n"
    result = ats_chars.scan(text)
    assert result["clean"] is False
    assert result["violation_count"] == 1
    assert result["violations"][0]["line"] == 3
    assert result["violations"][0]["char"] == "—"


def test_curly_quotes_flagged():
    text = 'Built the “best” product and the team’s roadmap.\n'
    result = ats_chars.scan(text)
    chars = {v["char"] for v in result["violations"]}
    assert "“" in chars
    assert "”" in chars
    assert "’" in chars  # curly apostrophe


def test_decorative_bullets_and_arrows_flagged():
    text = "★ Top performer\n➤ Drove growth\n✔ Shipped on time\n"
    result = ats_chars.scan(text)
    assert result["violation_count"] == 3


def test_plain_hyphen_and_straight_quotes_not_flagged():
    text = 'Grew revenue - owned "the roadmap" and the team\'s output.\n'
    result = ats_chars.scan(text)
    assert result["clean"] is True


def test_value_blind_no_fix_suggestion_field():
    """The scanner flags; it never proposes a rewritten replacement string."""
    text = "Shipped fast — under budget.\n"
    result = ats_chars.scan(text)
    for v in result["violations"]:
        assert set(v.keys()) == {"line", "char", "reason", "context"}
        assert "fix" not in v and "replacement" not in v


def test_ampersand_as_prose_and_flagged():
    text = "Led Sales & Marketing initiatives across three regions.\n"
    result = ats_chars.scan(text)
    assert result["clean"] is False
    assert any(v["char"] == "&" for v in result["violations"])


def test_ampersand_in_brand_name_not_flagged():
    text = (
        "Worked with AT&T on the integration.\n"
        "Advised on M&A due diligence for the deal.\n"
        "Partnered with Dolce & Gabbana on the campaign.\n"
    )
    result = ats_chars.scan(text)
    assert result["clean"] is True


def test_real_candidate_is_clean():
    """The current resume_candidate.md (post ampersand fix, rev8) should scan clean."""
    from pathlib import Path

    p = Path(
        "D:/vibe/resume-pipeline-data/pipeline/runs/"
        "anthropic-product-manager-api-growth-2026-07-06/resume_candidate.md"
    )
    if not p.exists():
        import pytest
        pytest.skip("data-plane Anthropic run not present")
    result = ats_chars.scan_file(p)
    assert result["clean"] is True
