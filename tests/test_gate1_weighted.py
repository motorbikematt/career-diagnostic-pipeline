"""Gate 1 weak-Partial tally and location integration (TODO #10, #12)."""
import yaml

import gate1


def _hard(i, cls, recoverable=False):
    return {"id": i, "kind": "hard", "weight": 1, "classification": cls, "recoverable": recoverable}


def test_weak_partial_counts_half():
    gm = {"requirements": [_hard(f"p{i}", "partial") for i in range(4)]
          + [_hard(f"m{i}", "match") for i in range(8)]}
    r = gate1.evaluate(gm)
    assert r["unrecoverable_hard_count"] == 0          # None-only integer unchanged
    assert r["weak_partial_hard_gaps"] == ["p0", "p1", "p2", "p3"]
    assert r["weighted_unrecoverable"] == 2.0
    assert r["tripped"] is True                         # 4 weak Partials == 2 Nones


def test_single_weak_partial_in_large_set_does_not_trip():
    gm = {"requirements": [_hard("p", "partial")] + [_hard(f"m{i}", "match") for i in range(9)]}
    assert gate1.evaluate(gm)["tripped"] is False


def test_recoverable_partial_is_not_weak():
    gm = {"requirements": [_hard("p", "partial", recoverable=True), _hard("m", "match")]}
    assert gate1.evaluate(gm)["weak_partial_hard_gaps"] == []


def test_location_trip_trips_alone(gapmap):
    r = gate1.evaluate(gapmap, location={"result": "trip", "reason": "Austin: outside"})
    assert r["tripped"] is True
    assert r["reasons"] == ["location: Austin: outside"]


def test_location_open_question_does_not_trip(gapmap):
    r = gate1.evaluate(gapmap, location={"result": "open-question", "reason": "ask"})
    assert r["tripped"] is False
    assert r["location"]["result"] == "open-question"


def test_evaluate_files_remote_needs_no_location_file(tmp_path, gapmap, requirements):
    gm, rq, pf = tmp_path / "gapmap.yaml", tmp_path / "requirements.yaml", tmp_path / "prefs.yaml"
    gm.write_text(yaml.safe_dump(gapmap), encoding="utf-8")
    rq.write_text(yaml.safe_dump({**requirements, "work_arrangement": "remote"}), encoding="utf-8")
    pf.write_text(yaml.safe_dump({"home": "X", "commute": {}, "relocation": {}}), encoding="utf-8")
    r = gate1.evaluate_files(gm, rq, None, pf)
    assert r["location"]["result"] == "pass"
