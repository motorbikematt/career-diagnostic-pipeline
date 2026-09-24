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


# --- Ambiguous targets (TODO #7) -------------------------------------------

def test_fixture_prescriptions_have_unambiguous_targets():
    import yaml
    from conftest import RUN
    pres = yaml.safe_load((RUN / "prescriptions.yaml").read_text(encoding="utf-8"))
    assert prescriptions.ambiguous_targets(pres) == []


def test_either_or_target_fails():
    pres = {"prescriptions": [
        {"type": "add", "target": "under Professional Summary or as a new early-career entry",
         "why": "..."},
    ]}
    result = prescriptions.check_coverage(pres, {"requirements": []})
    assert result["ok"] is False
    assert len(result["ambiguous_targets"]) == 1


def test_words_containing_or_are_not_flagged():
    pres = {"prescriptions": [
        {"type": "reframe", "target": "Senior Editor role, Coordinator bullet", "why": "..."},
    ]}
    assert prescriptions.ambiguous_targets(pres) == []
