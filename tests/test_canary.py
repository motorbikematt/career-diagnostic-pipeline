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
