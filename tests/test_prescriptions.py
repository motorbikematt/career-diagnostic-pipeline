import prescriptions


def test_fixture_has_no_recoverable_gaps(gapmap):
    assert prescriptions.recoverable_gap_ids(gapmap) == []


def _gapmap_with_recoverable():
    return {"requirements": [
        {"id": "hr-9", "kind": "hard", "weight": 2, "classification": "none", "recoverable": True},
        {"id": "hr-1", "kind": "hard", "weight": 2, "classification": "match", "recoverable": False},
    ]}


def test_covered_recoverable_gap_passes():
    gm = _gapmap_with_recoverable()
    pres = {"prescriptions": [
        {"type": "add", "target": "Role X", "why": "closes budget ownership",
         "closes": ["hr-9"], "source": "role-2.project-2"},
    ]}
    result = prescriptions.check_coverage(pres, gm)
    assert result["ok"] is True
    assert result["covered"] == ["hr-9"]


def test_uncovered_recoverable_gap_fails():
    gm = _gapmap_with_recoverable()
    pres = {"prescriptions": [
        {"type": "reorder", "target": "top fold", "why": "lead with platform"},
    ]}
    result = prescriptions.check_coverage(pres, gm)
    assert result["ok"] is False
    assert result["uncovered"] == ["hr-9"]


def test_add_without_source_does_not_cover():
    gm = _gapmap_with_recoverable()
    pres = {"prescriptions": [
        {"type": "add", "target": "Role X", "why": "...", "closes": ["hr-9"]},  # no source
    ]}
    result = prescriptions.check_coverage(pres, gm)
    assert result["ok"] is False
