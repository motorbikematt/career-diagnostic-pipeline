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


# --- Role bullet budget: Add paired with Cut (TODO 42) -----------------------

def _resume(*role_sizes):
    """A seed resume with one Experience role per size, newest first."""
    parts = ["# Name\n\n## Summary\n\nPM with 8 years.\n\n## Experience\n"]
    for i, n in enumerate(role_sizes):
        parts.append(f"### Co{i} — Product Manager ({2024 - 3 * i}–{2027 - 3 * i})\n")
        parts += [f"- bullet {j}\n" for j in range(n)]
        parts.append("\n")
    return "".join(parts)


def _p(typ, role=None, **extra):
    p = {"type": typ, "target": f"a bullet in {role}" if role else "somewhere",
         "why": "x", **extra}
    if role:
        p["role"] = role
    return p


R0 = "Co0 — Product Manager (2024–2027)"
R1 = "Co1 — Product Manager (2021–2024)"
R2 = "Co2 — Product Manager (2018–2021)"


def test_budget_needs_the_resume():
    assert prescriptions.role_budget_issues({"prescriptions": [_p("add", R0)]}, None)["issues"] == []


def test_add_within_budget_passes():
    res = prescriptions.role_budget_issues({"prescriptions": [_p("add", R0)]}, _resume(4, 3, 2))
    assert res["issues"] == []
    assert res["roles"][0] == {"entry": R0, "bullets": 4, "net": 1, "projected": 5, "budget": 5}


def test_add_past_budget_fails():
    res = prescriptions.role_budget_issues({"prescriptions": [_p("add", R0)]}, _resume(5, 3, 2))
    assert len(res["issues"]) == 1 and R0 in res["issues"][0]


def test_budget_falls_with_recency():
    # Third role: budget is 2, so a third bullet fails even though role one could take it.
    res = prescriptions.role_budget_issues({"prescriptions": [_p("add", R2)]}, _resume(5, 4, 2))
    assert len(res["issues"]) == 1 and R2 in res["issues"][0]


def test_cut_in_the_same_role_offsets_an_add():
    pres = {"prescriptions": [_p("add", R0), _p("cut", R0)]}
    assert prescriptions.role_budget_issues(pres, _resume(5, 3, 2))["issues"] == []


def test_remove_offsets_and_bullets_count_scales():
    pres = {"prescriptions": [_p("add", R0, bullets=2), _p("remove", R0, bullets=2)]}
    assert prescriptions.role_budget_issues(pres, _resume(5, 3, 2))["issues"] == []
    short = {"prescriptions": [_p("add", R0, bullets=2), _p("cut", R0)]}
    assert prescriptions.role_budget_issues(short, _resume(5, 3, 2))["issues"]


def test_compress_does_not_offset_an_add():
    pres = {"prescriptions": [_p("add", R0), _p("compress", R0)]}
    assert prescriptions.role_budget_issues(pres, _resume(5, 3, 2))["issues"]


def test_cut_in_another_role_does_not_offset():
    pres = {"prescriptions": [_p("add", R0), _p("cut", R1)]}
    assert prescriptions.role_budget_issues(pres, _resume(5, 3, 2))["issues"]


def test_approved_reason_waives_the_budget():
    pres = {"prescriptions": [_p("add", R0, over_budget_reason="closes the one hard gap")]}
    assert prescriptions.role_budget_issues(pres, _resume(5, 3, 2))["issues"] == []


def test_role_already_over_budget_is_not_flagged_without_growth():
    pres = {"prescriptions": [_p("reframe", R0)]}
    assert prescriptions.role_budget_issues(pres, _resume(7, 3, 2))["issues"] == []
    paired = {"prescriptions": [_p("add", R0), _p("cut", R0)]}
    assert prescriptions.role_budget_issues(paired, _resume(7, 3, 2))["issues"] == []
    grows = {"prescriptions": [_p("add", R0)]}
    assert prescriptions.role_budget_issues(grows, _resume(7, 3, 2))["issues"]


def test_unknown_role_is_a_note_not_a_failure():
    pres = {"prescriptions": [_p("add", "Some Other Co — Founder (2012–2014)")]}
    res = prescriptions.role_budget_issues(pres, _resume(5, 3, 2))
    assert res["issues"] == [] and "not an Experience entry" in res["notes"][0]


def test_add_naming_a_company_without_a_role_is_a_note():
    pres = {"prescriptions": [{"type": "add", "target": "A metric under Co0", "why": "x"}]}
    res = prescriptions.role_budget_issues(pres, _resume(5, 3, 2))
    assert res["issues"] == [] and "no `role`" in res["notes"][0]


def test_role_matches_by_unique_substring():
    pres = {"prescriptions": [_p("add", "Co0")]}
    assert prescriptions.role_budget_issues(pres, _resume(5, 3, 2))["issues"]


def test_check_coverage_ok_reflects_the_budget():
    pres = {"prescriptions": [SUMMARY, _p("add", R0)]}
    result = prescriptions.check_coverage(pres, {"requirements": []}, None, _resume(5, 3, 2))
    assert result["ok"] is False and result["budget_issues"]
    assert prescriptions.check_coverage(pres, {"requirements": []})["ok"] is True  # no resume given


def test_fixture_passes_its_budget():
    from conftest import RUN
    result = prescriptions.check_files(RUN / "prescriptions.yaml", RUN / "gapmap.yaml",
                                       RUN / "requirements.yaml", RUN / "resume.md")
    assert result["ok"] is True, result
    assert result["budget_issues"] == []


def test_cli_keeps_positional_arguments_and_adds_resume(tmp_path):
    import subprocess
    import sys

    from conftest import REPO, RUN
    helper = REPO / ".claude" / "skills" / "resume-fit" / "helpers" / "prescriptions.py"
    base = [sys.executable, str(helper), str(RUN / "prescriptions.yaml"),
            str(RUN / "gapmap.yaml"), str(RUN / "requirements.yaml")]
    assert subprocess.run(base, capture_output=True, cwd=helper.parent).returncode == 0
    full = subprocess.run([*base, "--resume", str(RUN / "resume.md")], capture_output=True,
                          cwd=helper.parent)
    assert full.returncode == 0, full.stderr


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
