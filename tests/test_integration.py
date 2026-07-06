"""Deterministic end-to-end integration over the synthetic fixture.

Exercises the full plumbing chain the orchestrator runs between subagent
dispatches — proving the pieces compose before a live LLM run. The subagent
LLM calls themselves are exercised in a live run, not here.
"""
import canary
import gapmap_summary
import gate1
import score
import validate

from conftest import EXAMPLES, RUN

WHD = EXAMPLES / "synthetic-whd.md"


def test_all_artifacts_validate():
    validate.validate_file(RUN / "requirements.yaml", "requirements")
    validate.validate_file(RUN / "scd.yaml", "scd")
    validate.validate_file(RUN / "gapmap.yaml", "gapmap")
    validate.validate_file(RUN / "screen.yaml", "screen")


def test_score_then_gate1_chain():
    import yaml
    gm = yaml.safe_load((RUN / "gapmap.yaml").read_text(encoding="utf-8"))
    s = score.compute(gm)
    g = gate1.evaluate(gm)
    # The score's unrecoverable count and gate1's must agree (same definition).
    assert s["unrecoverable_hard_count"] == g["unrecoverable_hard_count"]
    # Fixture is a viable "apply with edits" case: strong score, gate not tripped.
    assert s["paper_score"] >= 70
    assert g["tripped"] is False


def test_screening_input_is_whd_blind():
    import yaml
    gm = yaml.safe_load((RUN / "gapmap.yaml").read_text(encoding="utf-8"))
    summary = gapmap_summary.summarize(gm)
    dumped = yaml.safe_dump(summary, allow_unicode=True)
    # No WHD-derived fields in what screening would receive.
    assert "whd_evidence" not in dumped
    assert "recoverable" not in dumped
    # And the WHD canary token cannot appear in the screening-safe summary.
    token = canary.read_canary(WHD)
    assert token not in dumped


def test_canary_scan_passes_on_clean_run():
    result = canary.check(RUN / "screen.yaml", WHD)
    assert result["leaked"] is False
