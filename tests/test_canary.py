import pytest
import canary

from conftest import EXAMPLES, RUN

WHD = EXAMPLES / "synthetic-whd.md"


def test_read_canary():
    token = canary.read_canary(WHD)
    assert token == "WHD-CANARY-SYNTHETIC-0000-DO-NOT-OUTPUT"


def test_clean_screen_no_leak():
    result = canary.check(RUN / "screen.yaml", WHD)
    assert result["leaked"] is False


def test_leak_detected(tmp_path):
    token = canary.read_canary(WHD)
    leaky = tmp_path / "screen.yaml"
    leaky.write_text(f"first_friction_trigger: something\nnote: {token}\n", encoding="utf-8")
    result = canary.check(leaky, WHD)
    assert result["leaked"] is True


def test_missing_canary_raises(tmp_path):
    whd = tmp_path / "whd.md"
    whd.write_text("---\nowner: X\n---\n# Role\n", encoding="utf-8")
    with pytest.raises(ValueError):
        canary.read_canary(whd)


TEMPLATE_WHD = (
    "---\ndocument: Work History Document\n"
    'canary: "WHD-CANARY-REPLACE-WITH-UNIQUE-TOKEN-DO-NOT-OUTPUT"\n'
    "roles: []\n---\n\n# Body\n"
)


def test_placeholder_is_refused(tmp_path):
    whd = tmp_path / "whd.md"
    whd.write_text(TEMPLATE_WHD, encoding="utf-8")
    with pytest.raises(ValueError, match="placeholder"):
        canary.read_canary(whd)


def test_init_replaces_placeholder(tmp_path):
    whd = tmp_path / "whd.md"
    whd.write_text(TEMPLATE_WHD, encoding="utf-8")
    result = canary.init_canary(whd)
    assert result["changed"] is True
    assert canary.read_canary(whd) == result["canary"]
    text = whd.read_text(encoding="utf-8")
    assert "REPLACE" not in text
    assert text.endswith("# Body\n")  # body untouched


def test_init_keeps_real_token_unless_forced(tmp_path):
    whd = tmp_path / "whd.md"
    whd.write_text(TEMPLATE_WHD, encoding="utf-8")
    first = canary.init_canary(whd)["canary"]
    assert canary.init_canary(whd) == {"changed": False, "canary": first}
    rotated = canary.init_canary(whd, force=True)
    assert rotated["changed"] is True and rotated["canary"] != first


def test_init_adds_missing_token(tmp_path):
    whd = tmp_path / "whd.md"
    whd.write_text("---\nowner: X\n---\n# Role\n", encoding="utf-8")
    token = canary.init_canary(whd)["canary"]
    assert canary.read_canary(whd) == token


def test_tokens_are_unique():
    assert canary.new_token() != canary.new_token()


# --- Escalation quote (TODO 42) ----------------------------------------------

import yaml

RESUME = "- Managed a smart-camera hardware product from prototype to production\n"


def _screen(**over):
    base = {"first_escalation_trigger": "The lifecycle scope compels a call.",
            "escalation_quote": "Managed a smart-camera hardware product from prototype to production"}
    base.update(over)
    return base


def test_quote_on_the_resume_passes():
    res = canary.check_quote(_screen(), RESUME)
    assert res == {"ok": True, "failures": [], "warnings": []}


def test_missing_quote_fails():
    res = canary.check_quote(_screen(escalation_quote=""), RESUME)
    assert res["ok"] is False and "missing" in res["failures"][0]


def test_quote_not_on_resume_fails():
    res = canary.check_quote(_screen(escalation_quote="Shipped 50k units in year one"), RESUME)
    assert res["ok"] is False and "not on the resume" in res["failures"][0]


def test_trigger_figure_not_on_resume_warns_but_does_not_fail():
    res = canary.check_quote(
        _screen(first_escalation_trigger="Shipped prototype-to-production (50k units)."), RESUME)
    assert res["ok"] is True
    assert any("50k" in w for w in res["warnings"])


def test_trigger_figure_on_resume_is_fine():
    resume = RESUME + "- Cut latency 80% in a quarter\n"
    res = canary.check_quote(_screen(first_escalation_trigger="Cut latency 80%."), resume)
    assert res["warnings"] == []


def test_example_fixture_quote_is_on_its_resume(resume_text):
    screen = yaml.safe_load((RUN / "screen.yaml").read_text(encoding="utf-8"))
    assert canary.check_quote(screen, resume_text) == {"ok": True, "failures": [], "warnings": []}


def test_example_screen_cites_nothing_the_resume_lacks(resume_text):
    # The fixture once quoted "50k units", a figure only the WHD holds.
    screen = yaml.safe_load((RUN / "screen.yaml").read_text(encoding="utf-8"))
    assert "50k" not in screen["first_escalation_trigger"]
    assert "50k" not in resume_text


def test_cli_resume_flag_fails_on_a_bad_quote(tmp_path):
    import subprocess
    import sys

    from conftest import REPO
    screen = tmp_path / "screen.yaml"
    screen.write_text(yaml.safe_dump(_screen(escalation_quote="Never on the page")), encoding="utf-8")
    resume = tmp_path / "resume.md"
    resume.write_text(RESUME, encoding="utf-8")
    helper = REPO / ".claude" / "skills" / "resume-fit" / "helpers" / "canary.py"
    p = subprocess.run([sys.executable, str(helper), str(screen), str(WHD), "--resume", str(resume)],
                       capture_output=True, text=True, cwd=helper.parent)
    assert p.returncode == 1
    assert "BLINDNESS VIOLATION" in p.stdout
    ok = subprocess.run([sys.executable, str(helper), str(screen), str(WHD)],
                        capture_output=True, text=True, cwd=helper.parent)
    assert ok.returncode == 0  # no --resume: the existing canary scan is unchanged
