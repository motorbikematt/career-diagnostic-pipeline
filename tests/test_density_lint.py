import json
import os
import subprocess
import sys

import pytest

import density_lint as dl
from conftest import REPO, RUN, data_plane_runs

HELPERS = REPO / ".claude" / "skills" / "resume-fit" / "helpers"


def rules(result):
    return [f["rule"] for f in result["flags"]]


def words(n, word="word"):
    return " ".join([word] * n)


def resume(experience: str, summary: str = "Product manager with 8 years.") -> str:
    return f"# Name\n\n## Summary\n\n{summary}\n\n## Experience\n\n{experience}\n"


def test_example_fixture_is_clean():
    res = dl.check((RUN / "resume.md").read_text(encoding="utf-8"))
    assert res["flags"] == []
    assert res["stats"]["bullets"] == 6
    assert [r["bullets"] for r in res["stats"]["roles"]] == [3, 3]


def test_bullet_at_ceiling_passes_and_one_over_flags():
    at = resume(f"### Co - PM (2021-present)\n\n- {words(dl.MAX_BULLET_WORDS)}\n")
    over = resume(f"### Co - PM (2021-present)\n\n- {words(dl.MAX_BULLET_WORDS + 1)}\n")
    assert "bullet-long" not in rules(dl.check(at))
    assert "bullet-long" in rules(dl.check(over))


def test_bold_markers_do_not_count_as_words():
    text = f"**Label:** {words(dl.MAX_BULLET_WORDS - 1)}"
    md = resume(f"### Co - PM (2021-present)\n\n- {text}\n")
    assert "bullet-long" not in rules(dl.check(md))


@pytest.mark.parametrize("text, count", [
    ("Cut latency 80% and costs ~$775K/yr", 2),
    ("Grew DAU from 2M to 5M, +40% in 6 months", 4),
    ("Compressed cycles 10-20x in 2023", 1),
    ("Shipped in 2019 and 2021", 0),
    ("Reached 425 of the top 1,000 experiences", 2),
])
def test_number_counting(text, count):
    assert len(dl.numbers(text)) == count


def test_bullet_with_too_many_numbers_flags():
    md = resume("### Co - PM (2021-present)\n\n"
                "- Grew DAU from 2M to 5M, +40% in 6 months\n")
    assert "bullet-metrics" in rules(dl.check(md))


def test_role_budget_by_recency():
    first = "\n".join(f"- bullet {i}" for i in range(dl.ROLE_BULLET_BUDGET[0]))
    old_budget = dl.ROLE_BULLET_BUDGET[-1]
    old = "\n".join(f"- bullet {i}" for i in range(old_budget + 1))
    md = resume(f"### A - PM (2021-present)\n\n{first}\n\n"
                f"### B - PM (2018-2021)\n\n- one\n\n"
                f"### C - PM (2015-2018)\n\n- one\n\n"
                f"### D - PM (2012-2015)\n\n{old}\n")
    res = dl.check(md)
    flagged = [f["role"] for f in res["flags"] if f["rule"] == "role-bullets"]
    assert flagged == ["D - PM (2012-2015)"]
    assert res["stats"]["roles"][3]["budget"] == old_budget


def test_intro_skips_the_date_line():
    md = resume("### Senior Product Manager - Roblox\n"
                "Remote (Dayton, OH; HQ San Mateo, CA) | Dec 2022 - Apr 2025\n"
                f"{words(dl.MAX_INTRO_WORDS)}\n- bullet\n")
    res = dl.check(md)
    assert res["stats"]["roles"][0]["intro_words"] == dl.MAX_INTRO_WORDS
    assert "role-intro-long" not in rules(res)


def test_long_intro_flags_even_when_it_mentions_a_year():
    md = resume("### Founder - Co\nKettering, OH | Jul 2025 - Present\n"
                f"Founded in 2025, {words(dl.MAX_INTRO_WORDS)}\n- bullet\n")
    assert "role-intro-long" in rules(dl.check(md))


def test_summary_number_repeated_in_a_bullet_flags():
    md = resume("### Co - PM (2021-present)\n\n- Reached 425 of the top 1,000 games\n",
                summary="PM whose API reached 425 of the top 1,000 games.")
    flag = [f for f in dl.check(md)["flags"] if f["rule"] == "summary-repeats"]
    assert flag and "425" in flag[0]["detail"] and "1,000" in flag[0]["detail"]


def test_small_numbers_are_not_repeats():
    md = resume("### Co - PM (2021-present)\n\n- Led 3 pods\n",
                summary="PM who led 3 pods across 8 years.")
    assert "summary-repeats" not in rules(dl.check(md))


def test_skills_and_education_bullets_are_not_claims():
    md = resume("### Co - PM (2021-present)\n\n- short\n") + (
        f"\n## Skills\n\n- {words(dl.MAX_BULLET_WORDS + 10)}\n"
        f"\n## Education\n\n- 1, 2, 3, 4 degrees\n")
    res = dl.check(md)
    assert res["stats"]["bullets"] == 1
    assert not {"bullet-long", "bullet-metrics"} & set(rules(res))


def test_scan_zone_and_total_words_flag_a_dense_resume():
    bullets = "\n".join(f"- {words(30)}" for _ in range(40))
    res = dl.check(resume(f"### Co - PM (2021-present)\n\n{bullets}\n"))
    assert res["stats"]["scan_zone_words"] > dl.MAX_SCAN_ZONE_WORDS
    assert {"scan-zone-words", "total-words"} <= set(rules(res))


def test_scan_zone_grows_with_narrower_margins():
    # 304 characters: 4 lines at 0.6 in margins, 3 lines at 0.5 in.
    bullets = "\n".join(f"- {words(61)}" for _ in range(40))
    md = resume(f"### Co - PM (2021-present)\n\n{bullets}\n")
    assert (dl.check(md, margin_in=0.5)["stats"]["scan_zone_words"]
            > dl.check(md, margin_in=0.6)["stats"]["scan_zone_words"])


def test_cli_is_advisory_and_survives_cp1252(tmp_path):
    f = tmp_path / "r.md"
    f.write_text(resume(f"### Co → PM (2021-present)\n\n- {words(60)}\n"), encoding="utf-8")
    p = subprocess.run([sys.executable, str(HELPERS / "density_lint.py"), str(f)],
                       capture_output=True, cwd=HELPERS,
                       env={**os.environ, "PYTHONIOENCODING": "cp1252"})
    assert p.returncode == 0, p.stderr
    assert b"UnicodeEncodeError" not in p.stderr
    out = p.stdout.decode("utf-8")
    assert json.loads(out[:out.rindex("}") + 1])["flags"]


# --- Escalation quote position (TODO 42) --------------------------------------

QUOTE = "Cut voice latency 80% across all low-end devices"


def _bullets(n, word="filler"):
    return "\n".join(f"- {words(30, word)}" for _ in range(n))


def test_quote_in_the_scan_zone_is_clean():
    md = resume(f"### Co - PM (2021-present)\n\n- {QUOTE}\n{_bullets(3)}\n")
    res = dl.check(md, screen={"escalation_quote": QUOTE})
    loc = res["stats"]["escalation"]
    assert loc["match"] == "exact" and loc["in_scan_zone"] is True
    assert not {"escalation-below-scan-zone", "escalation-missing"} & set(rules(res))


def test_quote_below_the_scan_zone_flags():
    md = resume(f"### Co - PM (2021-present)\n\n{_bullets(30)}\n- {QUOTE}\n")
    res = dl.check(md, screen={"escalation_quote": QUOTE})
    assert res["stats"]["escalation"]["in_scan_zone"] is False
    assert "escalation-below-scan-zone" in rules(res)


def test_quote_matches_across_markdown_emphasis():
    md = resume("### Co - PM (2021-present)\n\n- **Cut voice latency 80%** across all low-end devices\n")
    assert dl.check(md, screen={"escalation_quote": QUOTE})["stats"]["escalation"]["match"] == "exact"


def test_reworded_draft_falls_back_to_the_figures():
    md = resume("### Co - PM (2021-present)\n\n- Reduced voice latency by 80% on budget phones\n")
    loc = dl.check(md, screen={"escalation_quote": QUOTE})["stats"]["escalation"]
    assert loc["match"] == "figures" and loc["in_scan_zone"] is True


def test_quote_with_no_figures_has_no_fallback():
    md = resume("### Co - PM (2021-present)\n\n- Ran product discovery with partners\n")
    res = dl.check(md, screen={"escalation_quote": "Led the discovery effort"})
    assert "escalation-missing" in rules(res)


def test_missing_quote_or_empty_screen_flags_missing():
    md = resume("### Co - PM (2021-present)\n\n- short\n")
    assert "escalation-missing" in rules(dl.check(md, screen={}))
    assert "escalation-missing" in rules(dl.check(md, screen={"escalation_quote": QUOTE}))


def test_no_screen_means_no_escalation_check():
    res = dl.check(resume("### Co - PM (2021-present)\n\n- short\n"))
    assert "escalation" not in res["stats"]


def test_example_fixture_quote_sits_in_the_scan_zone(resume_text):
    import yaml
    screen = yaml.safe_load((RUN / "screen.yaml").read_text(encoding="utf-8"))
    res = dl.check(resume_text, screen=screen)
    assert res["stats"]["escalation"]["in_scan_zone"] is True
    assert res["flags"] == []


@pytest.mark.skipif(not data_plane_runs().exists(), reason="data plane not configured")
def test_real_runs_parse_roles():
    for f in sorted(data_plane_runs().glob("*/resume_candidate.md")):
        res = dl.check_file(f)
        assert res["stats"]["roles"], f"no Experience roles found in {f.parent.name}"
