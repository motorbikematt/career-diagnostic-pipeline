"""Phase B.5 gap-review row selection (TODO #12)."""
import gap_review
import gapmap_summary


def _gm():
    return {"requirements": [
        {"id": "pr-1", "kind": "preferred", "classification": "none", "recoverable": False},
        {"id": "hr-1", "kind": "hard", "classification": "match", "recoverable": False},
        {"id": "hr-2", "kind": "hard", "classification": "partial", "recoverable": True},
        {"id": "hr-3", "kind": "hard", "classification": "partial", "recoverable": False},
        {"id": "hr-4", "kind": "hard", "classification": "none", "recoverable": True},
    ]}


def test_selects_every_none_and_weak_partials_hard_first():
    ids = [r["id"] for r in gap_review.rows(_gm())]
    assert ids == ["hr-3", "hr-4", "pr-1"]  # recoverable Partial and match skipped


def test_requirement_text_attached(requirements, gapmap):
    for r in gap_review.rows(gapmap, requirements):
        assert r["requirement"]


def test_upgrade_via_classification_is_rejected_by_gate1():
    import pytest
    import gate1
    gm = {"requirements": [
        # Model wrongly upgraded classification instead of recording WHD evidence.
        {"id": "hr-1", "kind": "hard", "classification": "match", "recoverable": False,
         "review": {"decision": "reframe"}},
    ]}
    assert gap_review.review_violations(gm)[0]["missing"] == [
        "recoverable: true", "whd_evidence", "review.anchor"]
    with pytest.raises(ValueError, match="never change classification"):
        gate1.evaluate(gm)


def test_correct_upgrade_passes_and_leaves_tally():
    import gate1
    gm = {"requirements": [
        {"id": "hr-1", "kind": "hard", "classification": "none", "recoverable": True,
         "whd_evidence": "circuit-dynamics.p1: shipped X", "weight": 1,
         "review": {"decision": "new-evidence", "anchor": "circuit-dynamics.p1"}},
    ]}
    assert gap_review.review_violations(gm) == []
    assert gate1.evaluate(gm)["weighted_unrecoverable"] == 0


def test_review_outcome_never_reaches_screening(gapmap):
    # A WHD-based upgrade records review + whd_evidence, never classification.
    row = gapmap["requirements"][0]
    row["review"] = {"decision": "reframe", "anchor": "circuit-dynamics.p1"}
    summary = gapmap_summary.summarize(gapmap)
    assert "review" not in summary["requirements"][0]
    assert "circuit-dynamics.p1" not in str(summary)
