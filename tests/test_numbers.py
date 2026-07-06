import numbers_strip

from conftest import RUN


def test_numbers_strip_from_fixture():
    n = numbers_strip.assemble(RUN)
    assert n["paper_score"] == 83
    assert n["recoverable_gaps_count"] == 0
    assert n["escalation_likelihood"] == "competitive"
    assert n["evidence_confidence"] == "medium"
