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
