"""Tests for the line-level JD-relevance meter (relevance.py).

Guards three properties the design depends on:
  1. It flags a zero-linkage claim as `none` and reads a keyword-rich claim as
     `strong`.
  2. It is value-blind -- no "cut"/"keep" verdict anywhere in its output.
  3. It is per-JD -- the SAME resume scored against two different requirements
     yields DIFFERENT linkage flags (a hardcoded stoplist would fail this).
"""
import relevance


# Minimal JD "A": a growth / API product role.
REQ_A = {
    "ats_keywords": ["growth", "API", "funnel", "monetization", "activation"],
    "hard_requirements": [
        {"id": "a1", "keywords": ["api", "developer platform"]},
        {"id": "a2", "keywords": ["growth", "funnel"]},
    ],
}
GAP_A = {
    "requirements": [
        {"id": "a1", "resume_evidence": "led three API launches on a developer platform"},
        {"id": "a2", "resume_evidence": "owned the growth funnel acquisition activation"},
    ],
    "ats": {"jd_keywords": ["growth", "API", "funnel", "monetization"]},
}

# Minimal JD "B": a hardware / manufacturing role -- totally different vocabulary.
REQ_B = {
    "ats_keywords": ["hardware", "manufacturing", "robotics", "CNC", "fabrication"],
    "hard_requirements": [
        {"id": "b1", "keywords": ["hardware", "manufacturing"]},
    ],
}
GAP_B = {
    "requirements": [
        {"id": "b1", "resume_evidence": "built an advanced manufacturing makerspace hardware lab"},
    ],
    "ats": {"jd_keywords": ["hardware", "manufacturing", "robotics"]},
}

RESUME = """# Jane Doe

jane@example.com | 555-0100

## Experience

### Senior PM — Acme
2020 – Present

- Owned the growth funnel and drove API adoption across the developer platform, tracking activation and monetization.
- Built an advanced manufacturing makerspace and hardware fabrication lab from scratch.
- Coordinated the annual company softball tournament and volunteer picnic logistics.
"""


def test_flags_zero_linkage_and_reads_strong():
    result = relevance.analyze(RESUME, REQ_A, GAP_A)
    by_text = {e["text"]: e for e in result["elements"]}
    growth_line = next(t for t in by_text if "growth funnel" in t)
    softball_line = next(t for t in by_text if "softball" in t)
    assert by_text[growth_line]["linkage"] == "strong"   # keyword + evidence
    assert by_text[softball_line]["linkage"] == "none"    # neither
    assert softball_line in result["none_linkage"]


def test_value_blind_no_cut_or_keep_verdict():
    result = relevance.analyze(RESUME, REQ_A, GAP_A)
    blob = repr(result).lower()
    # element records carry only linkage signal, never a recommendation
    for e in result["elements"]:
        assert set(e.keys()) <= {"text", "ats_hits", "linked_requirements",
                                 "linkage", "kind"}
    for forbidden in ("cut", "keep", "drop", "remove", "recommend"):
        assert forbidden not in blob


def test_per_jd_flags_change_no_stoplist():
    """The manufacturing bullet is `none` against the growth JD but `strong`
    against the hardware JD -- proving the flag follows the JD, not a fixed list."""
    manu = "Built an advanced manufacturing makerspace and hardware fabrication lab from scratch."

    a = relevance.analyze(RESUME, REQ_A, GAP_A)
    b = relevance.analyze(RESUME, REQ_B, GAP_B)
    a_manu = next(e for e in a["elements"] if "manufacturing" in e["text"])
    b_manu = next(e for e in b["elements"] if "manufacturing" in e["text"])

    assert a_manu["linkage"] == "none"     # off-target for a growth JD
    assert b_manu["linkage"] == "strong"   # on-target for a hardware JD
    assert a_manu["linkage"] != b_manu["linkage"]


def test_structural_lines_are_not_scored():
    """Contact and location/date lines are structural, not claims -- excluded."""
    result = relevance.analyze(RESUME, REQ_A, GAP_A)
    texts = [e["text"] for e in result["elements"]]
    assert not any("555-0100" in t for t in texts)          # contact
    assert not any(t.strip().startswith("2020") for t in texts)  # date line


def test_real_seed_flags_offtarget_not_roblox():
    """On the real Anthropic seed: off-target lines flag `none`; no Roblox
    monetization/funnel bullet does (Roblox is protected by the data)."""
    from pathlib import Path

    run = Path(
        "D:/vibe/resume-pipeline-data/pipeline/runs/"
        "anthropic-product-manager-api-growth-2026-07-06"
    )
    if not (run / "resume_final.md").exists():
        import pytest
        pytest.skip("data-plane Anthropic run not present")
    result = relevance.analyze_files(
        run / "resume_final.md", run / "requirements.yaml", run / "gapmap.yaml")
    none_blob = " ".join(result["none_linkage"]).lower()
    # off-target content surfaces
    assert "horticulture" in none_blob or "democratic party" in none_blob
    # no Roblox monetization/funnel bullet is ever flagged none
    for e in result["elements"]:
        if e["linkage"] == "none":
            assert "cost-to-serve" not in e["text"].lower()
            assert "adoption funnel" not in e["text"].lower()
