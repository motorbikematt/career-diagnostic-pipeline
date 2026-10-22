import pytest
import summary_lint
import validate

GOOD = ("Senior product manager with 8 years across SaaS and connected hardware. "
        "Took a smart-camera product from prototype to 50k units and ran 30+ "
        "experiments in two quarters, tying platform roadmap work to hardware delivery.")


def rules(result, kind="violations"):
    return {v["rule"] for v in result[kind]}


def test_good_summary_is_clean():
    res = summary_lint.lint_text(GOOD)
    assert res["violations"] == []
    assert res["warnings"] == []


def test_empty_summary_is_missing():
    assert rules(summary_lint.lint_text("  ")) == {"missing-summary"}


@pytest.mark.parametrize("text", [
    "I lead platform teams across 3 product lines.",
    "I'm a product leader with 8 years in hardware.",
    "Led my team to 50k units shipped.",
])
def test_first_person_is_a_violation(text):
    assert "first-person" in rules(summary_lint.lint_text(text))


@pytest.mark.parametrize("text", [
    "Seeking a senior product role with 8 years of experience.",
    "Looking for a platform role after 8 years in SaaS.",
    "Objective: a robotics product role, 8 years.",
])
def test_objective_wording_is_a_violation(text):
    assert "objective" in rules(summary_lint.lint_text(text))


def test_words_containing_i_or_me_are_not_flagged():
    res = summary_lint.lint_text("Hardware and metrics leader, 8 years, meeting every milestone.")
    assert res["violations"] == []


def test_long_summary_warns_but_does_not_fail():
    res = summary_lint.lint_text("Delivered 1 launch. " + "word " * 80)
    assert "long" in rules(res, "warnings")
    assert res["violations"] == []


def test_no_number_warns():
    res = summary_lint.lint_text("Product manager across SaaS and connected hardware.")
    assert "no-number" in rules(res, "warnings")


RESUME = """# Name

## Summary

Product manager with 8 years across SaaS and hardware.

## Experience

- bullet
"""


def test_extracts_the_summary_section():
    assert summary_lint.extract_summary(RESUME) == "Product manager with 8 years across SaaS and hardware."


def test_professional_summary_heading_is_accepted():
    md = RESUME.replace("## Summary", "## Professional Summary")
    assert summary_lint.extract_summary(md).startswith("Product manager")


def test_resume_without_summary_is_a_violation():
    res = summary_lint.lint_resume("# Name\n\n## Experience\n\n- bullet\n")
    assert rules(res) == {"missing-summary"}


def test_fixture_resume_summary_is_lintable():
    from conftest import RUN
    res = summary_lint.lint_resume((RUN / "resume.md").read_text(encoding="utf-8"))
    assert "missing-summary" not in rules(res)


# --- options file ------------------------------------------------------------

WHD = "<!-- anchor: acme -->\n# Acme\n\n<!-- anchor: acme.p1 -->\n**1. Thing**\n"


def _options(**over):
    data = {"options": [{"id": "a", "text": GOOD,
                         "claims": [{"claim": "50k units", "anchor": "acme.p1"}]}]}
    data.update(over)
    return data


def test_options_schema_validates():
    validate.validate(_options(chosen="a", edited=False, final_text=GOOD),
                      validate.load_schema("summary_options"))


def test_claim_without_anchor_is_unsupported():
    data = _options()
    data["options"][0]["claims"].append({"claim": "led 12 people", "anchor": ""})
    res = summary_lint.check_options(data, WHD)
    assert "unsupported-claim" in rules(res)


def test_anchor_missing_from_whd_is_unsupported():
    data = _options()
    data["options"][0]["claims"][0]["anchor"] = "acme.p9"
    res = summary_lint.check_options(data, WHD)
    assert any("not in WHD" in v["detail"] for v in res["violations"])


def test_good_options_are_clean():
    assert summary_lint.check_options(_options(chosen="a"), WHD)["violations"] == []


def test_choice_must_name_an_option():
    assert "bad-choice" in rules(summary_lint.check_options(_options(chosen="z"), WHD))


def test_final_text_is_linted():
    res = summary_lint.check_options(_options(final_text="I run 3 teams."), WHD)
    assert any(v["option"] == "final_text" for v in res["violations"])
