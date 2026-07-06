import score


def test_fixture_scores(gapmap):
    r = score.compute(gapmap)
    # Weighted: hard = (2+1.5+3+2+2)/12 = 10.5/12; overall = 12.5/15.
    assert r["hard_score"] == 88
    assert r["preferred_score"] == 67
    assert r["paper_score"] == 83
    assert r["counts"] == {"match": 6, "partial": 1, "none": 1}
    assert r["hard_total"] == 5
    assert r["preferred_total"] == 3
    assert r["recoverable_gaps_count"] == 0
    assert r["unrecoverable_hard_count"] == 0


def test_all_match_is_100():
    gm = {"requirements": [
        {"id": "a", "kind": "hard", "weight": 2, "classification": "match", "recoverable": False},
        {"id": "b", "kind": "hard", "weight": 5, "classification": "match", "recoverable": False},
    ]}
    assert score.compute(gm)["paper_score"] == 100


def test_all_none_is_0():
    gm = {"requirements": [
        {"id": "a", "kind": "hard", "weight": 2, "classification": "none", "recoverable": False},
    ]}
    assert score.compute(gm)["paper_score"] == 0


def test_recoverable_vs_unrecoverable():
    gm = {"requirements": [
        {"id": "a", "kind": "hard", "weight": 1, "classification": "none", "recoverable": True},
        {"id": "b", "kind": "hard", "weight": 1, "classification": "none", "recoverable": False},
    ]}
    r = score.compute(gm)
    assert r["recoverable_gaps"] == ["a"]
    assert r["unrecoverable_hard_gaps"] == ["b"]


def test_empty_requirements_is_zero():
    assert score.compute({"requirements": []})["paper_score"] == 0
