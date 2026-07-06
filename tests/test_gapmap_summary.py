import gapmap_summary


def test_strips_whd_fields(gapmap):
    summary = gapmap_summary.summarize(gapmap)
    for req in summary["requirements"]:
        assert "whd_evidence" not in req  # WHD-derived, must not reach screening
        assert "recoverable" not in req   # WHD-derived signal, stripped
        assert set(req.keys()) == {"id", "kind", "classification", "resume_evidence"}


def test_keeps_resume_and_jd_signal(gapmap):
    summary = gapmap_summary.summarize(gapmap)
    assert summary["jd_archetype"] == "robotics platform product manager"
    assert summary["ats"]["jd_keywords"]  # resume/JD-derived, safe
    # resume_evidence is resume-only and safe to keep
    hr1 = next(r for r in summary["requirements"] if r["id"] == "hr-1")
    assert "product management" in hr1["resume_evidence"]


def test_no_canary_token_survives_summary(gapmap):
    # Even if a stray token were in a WHD field, it must not survive summarization.
    gapmap["requirements"][0]["whd_evidence"] = "WHD-CANARY-SYNTHETIC-0000-DO-NOT-OUTPUT"
    import yaml
    dumped = yaml.safe_dump(gapmap_summary.summarize(gapmap))
    assert "CANARY" not in dumped
