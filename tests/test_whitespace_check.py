"""Tests for the page-fullness/whitespace-ratio check (whitespace_check.py).

This is a readability check (research-grounded: whitespace measurably affects
reading comprehension), NOT a bullet-length-uniformity check -- uniform bullet
length is itself an AI-writing signal (low "burstiness"), so this helper must
never push toward a normalized/uniform length. It only measures per-page density.
"""
import whitespace_check


def _dense_resume():
    """Many long bullets packed with no breathing room -- should read dense."""
    long_bullet = (
        "- Owned the end-to-end developer adoption funnel and monetization "
        "model across a large platform, defining and tracking metrics from "
        "first API experiment through production integration and downstream "
        "engagement, while coordinating cross-functionally. "
    )
    lines = ["# Jane Doe", "", "## Experience", "", "### Role — Company", "2020 - Present"]
    lines += [long_bullet * 2 for _ in range(10)]
    return "\n".join(lines)


def _sparse_resume():
    return "# Jane Doe\n\n## Experience\n\n### Role — Company\n2020 - Present\n\n- Did a thing.\n"


def test_dense_page_flagged():
    result = whitespace_check.analyze(_dense_resume())
    assert any(p["verdict"] == "dense" for p in result["pages"])
    assert result["balanced"] is False


def test_sparse_page_flagged():
    result = whitespace_check.analyze(_sparse_resume())
    assert any(p["verdict"] == "sparse" for p in result["pages"])


def test_word_and_char_counts_reported_per_page():
    result = whitespace_check.analyze(_dense_resume())
    for p in result["pages"]:
        assert p["word_count"] > 0
        assert p["char_count"] > 0
    assert result["total_word_count"] == sum(p["word_count"] for p in result["pages"])


def test_page_boundary_caveat_present():
    """The per-page split is approximate -- the caveat must always be surfaced,
    not buried, since it's been shown to produce phantom pages from rounding."""
    result = whitespace_check.analyze(_dense_resume())
    assert "APPROXIMATE" in result["page_boundary_caveat"]


def test_never_recommends_uniform_bullet_length():
    """This helper must never suggest normalizing bullet lengths toward a
    median/average -- that would push AWAY from human-authentic writing
    (uniform length is an AI-detection signal), not toward better readability."""
    result = whitespace_check.analyze(_dense_resume())
    blob = repr(result).lower()
    for forbidden in ("median", "average", "uniform", "normalize", "consistent length"):
        assert forbidden not in blob


def test_value_blind_no_edit_prescription():
    result = whitespace_check.analyze(_dense_resume())
    blob = repr(result).lower()
    for forbidden in ("cut", "shorten", "split", "trim"):
        assert forbidden not in blob
