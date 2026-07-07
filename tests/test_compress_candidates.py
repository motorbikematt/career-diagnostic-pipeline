"""Tests for the list-compression candidate detector (compress_candidates.py).

This helper finds a PATTERN (3+ item list) mechanically; it must never propose
the replacement category word itself -- that's the model's judgment call.
"""
import compress_candidates as cc


def test_three_item_list_detected():
    text = "- Led teams across China, Australia, and US/Europe/Korea.\n"
    result = cc.analyze(text)
    assert result["candidate_count"] == 1
    assert result["candidates"][0]["item_count"] == 3


def test_two_item_list_not_flagged():
    """Below the 3-item threshold -- compression isn't worth it for 2 items."""
    text = "- Worked with China and Australia on the launch.\n"
    result = cc.analyze(text)
    assert result["candidate_count"] == 0


def test_no_list_not_flagged():
    text = "- Owned the growth funnel end to end.\n"
    result = cc.analyze(text)
    assert result["candidate_count"] == 0


def test_verticals_pattern_detected():
    text = "- Launched the Aerospace, Automotive, and Toys verticals.\n"
    result = cc.analyze(text)
    assert result["candidate_count"] == 1
    assert result["candidates"][0]["item_count"] == 3


def test_value_blind_no_category_suggestion():
    """The detector never proposes a replacement collective noun -- that's the
    model's semantic judgment, ratified by the user."""
    text = "- Led teams across China, Australia, and US/Europe/Korea.\n"
    result = cc.analyze(text)
    for c in result["candidates"]:
        assert set(c.keys()) == {"text", "list_segment", "items",
                                 "item_count", "est_chars_freed"}
        blob = repr(c).lower()
        assert "trans-continental" not in blob
        assert "suggest" not in blob and "replace_with" not in blob
