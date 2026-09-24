"""Location rules for Gate 1 (TODO #10). Preferences mirror the decided rules."""
import pytest
import yaml

import location_gate
import validate
from conftest import REPO

PREFS = {
    "home": "Kettering, OH",
    "commute": {"onsite_max_minutes": 60, "hybrid_max_minutes": 90, "hybrid_max_days_per_week": 3},
    "relocation": {
        "open": True, "requires_paid_package": True, "metro_reach_minutes": 60,
        "metros": ["New York", "Columbus", "San Francisco Bay Area", "Washington DC"],
    },
}


def req(arrangement, location="Somewhere", **kw):
    return {"work_arrangement": arrangement, "location": location, **kw}


def loc(drive=None, metro=None, metro_minutes=None, borderline=False):
    return {"drive_minutes_from_home": drive, "nearest_metro": metro,
            "metro_minutes": metro_minutes, "borderline": borderline}


def result(r, a=None, p=PREFS):
    return location_gate.evaluate(r, a, p)["result"]


def test_remote_passes_without_assessment():
    assert result(req("remote")) == "pass"


def test_no_preferences_is_not_evaluated_never_pass():
    assert result(req("onsite"), loc(drive=500), None) == "not-evaluated"


def test_unstated_is_open_question():
    assert result(req("unstated")) == "open-question"
    assert result({"work_arrangement": "hybrid", "location": None}) == "open-question"


def test_onsite_within_commute_passes():
    assert result(req("onsite", "Dayton, OH"), loc(drive=15)) == "pass"


def test_hybrid_columbus_is_a_commute_not_a_relocation():
    r = req("hybrid", "Columbus, OH", hybrid_days=2, relocation_support="not-offered")
    assert result(r, loc(drive=75, metro="Columbus", metro_minutes=5)) == "pass"


def test_onsite_columbus_needs_the_package():
    a = loc(drive=75, metro="Columbus", metro_minutes=5)
    assert result(req("onsite", "Columbus, OH", relocation_support="offered"), a) == "pass"
    assert result(req("onsite", "Columbus, OH", relocation_support="unstated"), a) == "open-question"
    assert result(req("onsite", "Columbus, OH", relocation_support="not-offered"), a) == "trip"


def test_hybrid_days_unstated_in_hybrid_band_is_open_question():
    assert result(req("hybrid", "Columbus, OH"), loc(drive=75)) == "open-question"


def test_hybrid_too_many_days_falls_through_to_metro_rules():
    r = req("hybrid", "Columbus, OH", hybrid_days=4, relocation_support="not-offered")
    assert result(r, loc(drive=75, metro="Columbus", metro_minutes=5)) == "trip"


def test_columbia_md_counts_as_dc():
    r = req("hybrid", "Columbia, MD", relocation_support="unstated")
    assert result(r, loc(drive=480, metro="Washington DC", metro_minutes=40)) == "open-question"


def test_outside_everything_trips():
    assert result(req("onsite", "Austin, TX"), loc(drive=1100)) == "trip"


def test_metro_beyond_reach_trips():
    r = req("onsite", "Baltimore, MD", relocation_support="offered")
    assert result(r, loc(drive=480, metro="Washington DC", metro_minutes=75)) == "trip"


def test_borderline_is_open_question():
    r = req("onsite", "Baltimore, MD", relocation_support="offered")
    a = loc(drive=480, metro="Washington DC", metro_minutes=62, borderline=True)
    assert result(r, a) == "open-question"


def test_unknown_values_fail_loudly():
    with pytest.raises(ValueError):
        location_gate.evaluate(req("hybrid-remote"), loc(drive=10), PREFS)
    with pytest.raises(ValueError):
        location_gate.evaluate(req("onsite", relocation_support="maybe"), loc(drive=10), PREFS)
    with pytest.raises(ValueError):  # metro name not in the preferences list
        location_gate.evaluate(req("onsite"), loc(drive=900, metro="NYC", metro_minutes=5), PREFS)


def test_non_remote_without_assessment_fails_loudly():
    with pytest.raises(ValueError):
        location_gate.evaluate(req("onsite"), None, PREFS)


def test_template_and_decided_prefs_validate():
    tmpl = REPO / ".claude/skills/resume-fit/templates/preferences-template.yaml"
    schema = validate.load_schema("preferences")
    validate.validate(yaml.safe_load(tmpl.read_text(encoding="utf-8")), schema)
    validate.validate(PREFS, schema)
