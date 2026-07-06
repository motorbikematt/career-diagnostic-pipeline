import gate1


def test_fixture_does_not_trip(gapmap):
    r = gate1.evaluate(gapmap)
    assert r["tripped"] is False
    assert r["unrecoverable_hard_count"] == 0


def test_two_unrecoverable_hard_trips():
    gm = {"requirements": [
        {"id": "a", "kind": "hard", "weight": 1, "classification": "none", "recoverable": False},
        {"id": "b", "kind": "hard", "weight": 1, "classification": "none", "recoverable": False},
        {"id": "c", "kind": "hard", "weight": 1, "classification": "match", "recoverable": False},
    ]}
    r = gate1.evaluate(gm)
    assert r["tripped"] is True
    assert r["unrecoverable_hard_gaps"] == ["a", "b"]


def test_recoverable_gap_does_not_count():
    gm = {"requirements": [
        {"id": "a", "kind": "hard", "weight": 1, "classification": "none", "recoverable": True},
        {"id": "b", "kind": "hard", "weight": 1, "classification": "none", "recoverable": True},
    ]}
    r = gate1.evaluate(gm)
    assert r["unrecoverable_hard_count"] == 0
    assert r["tripped"] is False


def test_fraction_rule_trips_on_single_gap_small_set():
    # 1 of 2 hard reqs unrecoverable = 50% > 1/3 -> trips on the fraction rule.
    gm = {"requirements": [
        {"id": "a", "kind": "hard", "weight": 1, "classification": "none", "recoverable": False},
        {"id": "b", "kind": "hard", "weight": 1, "classification": "match", "recoverable": False},
    ]}
    r = gate1.evaluate(gm)
    assert r["tripped"] is True
    assert any("unrecoverable" in reason for reason in r["reasons"])


def test_custom_trip_rules_are_merged():
    gm = {"requirements": [
        {"id": "a", "kind": "hard", "weight": 1, "classification": "none", "recoverable": False},
    ]}
    # Raise the threshold so a single gap no longer trips the count rule; also
    # relax the fraction rule so 100% does not trip it.
    r = gate1.evaluate(gm, trip_rules={"min_unrecoverable_hard": 3, "unrecoverable_hard_fraction": 1.0})
    assert r["tripped"] is False
