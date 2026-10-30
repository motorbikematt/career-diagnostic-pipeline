import json
import os
import subprocess
import sys

import pytest
import yaml

import bullet_lint as bl
from conftest import REPO, RUN, data_plane_runs

HELPERS = REPO / ".claude" / "skills" / "resume-fit" / "helpers"


def rules(raw):
    return bl.classify(raw)["rules"]


def resume(*bullets, extra=""):
    body = "\n".join(f"- {b}" for b in bullets)
    return (f"# Name\n\n## Summary\n\nPM.\n\n## Experience\n\n### Co — PM (2021–present)\n\n"
            f"{body}\n{extra}")


@pytest.mark.parametrize("raw", [
    "Responsible for the platform roadmap",
    "Was responsible for onboarding",
    "In charge of three launches",
    "Helped with the pricing model",
    "Helped ship the SDK",
    "Assisted with partner calls",
    "Worked on the voice API",
    "Worked with engineering on latency",
    "Involved in the WebRTC overhaul",
    "Participated in roadmap reviews",
    "Tasked with a rebuild",
    "Duties included roadmap work",
    "Contributed to the launch",
    "**Developer Productivity:** Responsible for the voice API",
    "**Launch Messaging** Worked on announcements",
])
def test_duty_openers_are_flagged(raw):
    assert "duty-opener" in rules(raw)


@pytest.mark.parametrize("raw", [
    "Led the WebRTC overhaul, cutting latency 80%",
    "Helpfully rebuilt the roadmap",          # not the word "helped"
    "Built the pipeline responsible for ingestion",   # duty phrase mid-sentence
    "**Responsible AI Architecture:** Designed a five-layer guardrail system",
])
def test_non_duty_openers_are_not_flagged(raw):
    assert "duty-opener" not in rules(raw)


@pytest.mark.parametrize("raw, flagged", [
    ("Cut voice latency 80%", False),
    ("Grew DAU from 2M to 5M", False),
    ("Saved ~$775K a year", False),
    ("Ran 30+ experiments in two quarters", False),
    ("Built a pricing model from scratch", True),
    ("Coordinated firmware, optics, and contract manufacturing", True),
    ("Shipped in 2019 and 2021", True),          # bare years are not measures
    ("Took the model to leadership, resulting in a new toy", False),   # a result in words
    ("Delivered toolkits to partners, earning the highest CSAT", False),
])
def test_no_measure_needs_neither_number_nor_result(raw, flagged):
    assert ("no-measure" in rules(raw)) is flagged


def test_qualitative_only_is_information_not_a_flag():
    c = bl.classify("Delivered toolkits to partners, resulting in a new toy")
    assert c["rules"] == [] and c["qualitative_only"] is True
    assert bl.classify("Cut latency 80%")["qualitative_only"] is False


@pytest.mark.parametrize("raw, flagged", [
    ("Significantly improved onboarding", True),
    ("Dramatically reduced churn", True),
    ("Improved onboarding conversion significantly", True),
    ("Significantly improved onboarding, from 12% to 31%", False),
    ("Improved onboarding", False),
])
def test_vague_qualifier_only_without_a_number(raw, flagged):
    assert ("vague-qualifier" in rules(raw)) is flagged


def test_skills_and_education_lists_are_skipped():
    md = resume("Cut latency 80%", extra="\n## Skills\n\n- Responsible for nothing\n"
                                          "\n## Education\n\n- Worked on a thesis\n")
    res = bl.check(md)
    assert res["stats"]["bullets"] == 1 and res["flags"] == []


def test_flags_carry_role_rank_and_priority():
    roles = "".join(f"### Co{i} — PM ({2024 - 3 * i}–{2027 - 3 * i})\n\n- Built a thing\n\n"
                    for i in range(3))
    md = "# N\n\n## Summary\n\nPM.\n\n## Experience\n\n" + roles
    res = bl.check(md)
    by_rank = {f["rank"]: f["priority"] for f in res["flags"]}
    assert by_rank == {0: True, 1: True, 2: False}
    assert res["stats"]["priority_activity_only"] == 2
    assert [r["activity_only"] for r in res["stats"]["roles"]] == [1, 1, 1]


def test_each_flag_has_a_key_that_is_normalized_and_bounded():
    md = resume("**Label:** " + "word " * 40 + "end")
    flag = bl.check(md)["flags"][0]
    assert len(flag["key"]) <= bl.KEY_CHARS and "**" not in flag["key"]


# --- Review file ------------------------------------------------------------

def _review(tmp_path, data):
    p = tmp_path / "measure_review.yaml"
    p.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    return p


def test_no_measure_decision_silences_that_bullet(tmp_path):
    md = resume("Coordinated firmware, optics, and contract manufacturing partners",
                "Built a pricing model from scratch under data uncertainty")
    key = bl.check(md)["flags"][0]["key"]
    review = bl.load_review(_review(tmp_path, {key: "no-measure"}))
    res = bl.check(md, review)
    assert [f["rule"] for f in res["flags"]] == ["no-measure"]
    assert res["stats"]["acknowledged"] == 1 and res["stats"]["activity_only"] == 1


def test_no_measure_decision_does_not_silence_a_duty_opener(tmp_path):
    md = resume("Responsible for firmware, optics, and contract manufacturing partners")
    review = bl.load_review(_review(tmp_path, {bl.check(md)["flags"][0]["key"]: "no-measure"}))
    assert [f["rule"] for f in bl.check(md, review)["flags"]] == ["duty-opener"]


def test_keep_decision_silences_every_flag(tmp_path):
    md = resume("Responsible for firmware, optics, and contract manufacturing partners")
    review = bl.load_review(_review(tmp_path, {bl.check(md)["flags"][0]["key"]: {"decision": "keep",
                                                                                  "note": "x"}}))
    assert bl.check(md, review)["flags"] == []


def test_a_key_matches_by_prefix_but_short_keys_do_not(tmp_path):
    md = resume("Coordinated firmware, optics, and contract manufacturing partners")
    assert bl.check(md, bl.load_review(_review(tmp_path, {"Coordinated firmware, optics": "keep"})))["flags"] == []
    assert bl.check(md, bl.load_review(_review(tmp_path, {"Coordinated": "keep"})))["flags"]


def test_stale_keys_are_reported_not_fatal(tmp_path):
    md = resume("Cut latency 80% across all low-end devices")
    review = bl.load_review(_review(tmp_path, {"Coordinated firmware, optics, and more": "keep"}))
    assert bl.check(md, review)["stale_review_keys"] == ["Coordinated firmware, optics, and more"]


def test_unknown_decision_fails_loudly(tmp_path):
    with pytest.raises(ValueError, match="decision"):
        bl.load_review(_review(tmp_path, {"Some bullet text that is long enough": "maybe"}))


# --- Fixture, CLI, real runs ---------------------------------------------------

def test_example_fixture_flags_are_pinned(resume_text):
    res = bl.check(resume_text)
    assert res["stats"]["bullets"] == 6 and res["stats"]["with_number"] == 1
    assert [f["rule"] for f in res["flags"]] == ["no-measure"] * 5
    assert res["stats"]["priority_activity_only"] == 5


def test_cli_is_advisory_and_survives_cp1252(tmp_path):
    f = tmp_path / "r.md"
    f.write_text(resume("Responsible for the roadmap → everything"), encoding="utf-8")
    p = subprocess.run([sys.executable, str(HELPERS / "bullet_lint.py"), str(f)],
                       capture_output=True, cwd=HELPERS,
                       env={**os.environ, "PYTHONIOENCODING": "cp1252"})
    assert p.returncode == 0, p.stderr
    out = p.stdout.decode("utf-8")
    assert b"UnicodeEncodeError" not in p.stderr
    assert json.loads(out[:out.rindex("}") + 1])["flags"]


@pytest.mark.skipif(not data_plane_runs().exists(), reason="data plane not configured")
def test_real_runs_parse_and_count():
    for f in sorted(data_plane_runs().glob("*/resume_candidate.md")):
        res = bl.check_file(f)
        assert res["stats"]["bullets"] > 0 and res["stats"]["roles"], f.parent.name
        s = res["stats"]
        assert s["with_number"] + s["qualitative_only"] + s["activity_only"] + s["acknowledged"] \
            <= s["bullets"]
