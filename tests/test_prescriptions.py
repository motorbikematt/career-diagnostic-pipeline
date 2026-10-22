import pytest
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
        {"type": "summary", "target": "Summary section", "why": "rebuild"},
        {"type": "add", "target": "Role X", "why": "closes budget ownership",
         "closes": ["hr-9"], "source": "circuit-dynamics.p2"},
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


# --- Summary and banner (TODO 32, decision D1) ------------------------------

SUMMARY = {"type": "summary", "target": "Summary section", "why": "rebuild"}
REQ = {"role": "Senior Product Manager, Robotics Platform"}


def _banner(title="Senior Product Manager, Robotics Platform", **extra):
    return {"type": "banner", "target": "Banner line under the name",
            "jd_title": title, "why": "tie to posting", **extra}


def test_fixture_passes_with_requirements():
    from conftest import RUN
    result = prescriptions.check_files(RUN / "prescriptions.yaml", RUN / "gapmap.yaml",
                                       RUN / "requirements.yaml")
    assert result["ok"] is True, result


def test_missing_summary_prescription_fails():
    result = prescriptions.check_coverage({"prescriptions": []}, {"requirements": []})
    assert result["ok"] is False
    assert "no summary prescription" in result["summary_issues"][0]


def test_two_summary_prescriptions_fail():
    pres = {"prescriptions": [SUMMARY, dict(SUMMARY)]}
    assert prescriptions.summary_issues(pres)


def test_banner_with_verbatim_jd_title_passes():
    pres = {"prescriptions": [SUMMARY, _banner()]}
    assert prescriptions.check_coverage(pres, {"requirements": []}, REQ)["ok"] is True


def test_banner_title_must_match_jd_role_verbatim():
    pres = {"prescriptions": [SUMMARY, _banner("Product Leader")]}
    issues = prescriptions.banner_issues(pres, REQ)
    assert any("verbatim" in i for i in issues)


def test_banner_without_jd_title_fails():
    pres = {"prescriptions": [SUMMARY, {"type": "banner", "target": "Banner", "why": "x"}]}
    assert any("no jd_title" in i for i in prescriptions.banner_issues(pres, REQ))


def test_banner_required_when_requirements_given():
    pres = {"prescriptions": [SUMMARY]}
    assert any("no banner prescription" in i for i in prescriptions.banner_issues(pres, REQ))
    # Without requirements the role is unknown, so the requirement is not evaluated.
    assert prescriptions.banner_issues(pres, None) == []


def test_two_banners_fail():
    pres = {"prescriptions": [SUMMARY, _banner(), _banner()]}
    assert any("at most one" in i for i in prescriptions.banner_issues(pres, REQ))


def test_credentialed_title_banner_needs_a_whd_source():
    req = {"role": "Staff Software Engineer"}
    no_src = {"prescriptions": [SUMMARY, _banner("Staff Software Engineer")]}
    assert any("license or credential" in i for i in prescriptions.banner_issues(no_src, req))
    with_src = {"prescriptions": [SUMMARY, _banner("Staff Software Engineer", source="acme.p1")]}
    assert prescriptions.banner_issues(with_src, req) == []


def test_credentialed_title_may_omit_the_banner():
    req = {"role": "Registered Nurse"}
    assert prescriptions.banner_issues({"prescriptions": [SUMMARY]}, req) == []


@pytest.mark.parametrize("title,expected", [
    ("Staff Software Engineer", True),
    ("Registered Nurse", True),
    ("General Counsel", True),
    ("Senior CPA", True),
    ("Solutions Architect", True),
    ("Engineering Manager", False),   # "engineering" is not "engineer"
    ("Senior Product Manager", False),
    ("Managing Director", False),
    ("Director of Operations", False),
])
def test_credentialed_title_detection(title, expected):
    assert prescriptions.credentialed_title(title) is expected
