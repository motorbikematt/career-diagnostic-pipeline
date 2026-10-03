"""Structure lint: abbreviations, headings, date format (TODO #17, #18)."""
import structure_lint


def _rules(result, key="failures"):
    return [f["rule"] for f in result[key]]


def test_fixture_resume_passes(resume_text):
    r = structure_lint.check(resume_text)
    assert r["ok"] is True
    assert r["date_formats"] == ["YYYY"]


def test_abbreviated_title_fails_with_expansion():
    md = "## Experience\n\n### Acme, Inc. | Sr. Product Manager (2020-2022)\n"
    r = structure_lint.check(md)
    assert r["ok"] is False
    f = r["failures"][0]
    assert f["rule"] == "abbreviated-title"
    assert "Senior" in f["detail"]


def test_dotted_only_abbreviation_not_flagged_without_period():
    md = "## Experience\n\n### Acme, Inc. | Eng Manager (2020-2022)\n"
    assert "abbreviated-title" not in _rules(structure_lint.check(md))
    md = "## Experience\n\n### Acme, Inc. | Eng. Manager (2020-2022)\n"
    assert "abbreviated-title" in _rules(structure_lint.check(md))


def test_nonstandard_heading_is_advisory_and_allowable():
    md = "## Experience\n\n## Patents\n"
    r = structure_lint.check(md)
    assert r["ok"] is True
    assert any(a["rule"] == "nonstandard-heading" and a["heading"] == "Patents"
               for a in r["advisories"])
    r2 = structure_lint.check(md, allow=("Patents",))
    assert not any(a["rule"] == "nonstandard-heading" for a in r2["advisories"])


def test_missing_experience_fails_missing_others_advise():
    r = structure_lint.check("## Summary\n\ntext\n")
    assert _rules(r) == ["missing-experience"]
    missing = {a["heading"] for a in r["advisories"] if a["rule"] == "missing-section"}
    assert missing == {"Education", "Skills"}


def test_mixed_date_formats_across_entries_fail():
    md = """## Experience

### A, Inc. | Director (2020-2022)

### B, Inc. | Manager (Jan 2015 - Dec 2019)
"""
    r = structure_lint.check(md)
    assert r["ok"] is False
    assert set(_rules(r)) == {"mixed-date-format"}
    assert len(r["failures"]) == 2


def test_present_does_not_count_as_a_format():
    md = """## Experience

### A, Inc. | Director (2020-present)

### B, Inc. | Manager (2015-2020)
"""
    assert structure_lint.check(md)["ok"] is True


def test_mixed_formats_within_one_entry_fail():
    md = "## Experience\n\n### A, Inc. | Director (Jan 2020 - 2022)\n"
    r = structure_lint.check(md)
    assert _rules(r) == ["mixed-date-format"]


def test_dates_on_next_line_are_read():
    md = """## Experience

**A, Inc. | Director**
*Jan 2020 - Present*

**B, Inc. | Manager**
2015 - 2019
"""
    assert structure_lint.check(md)["ok"] is False


def test_legal_identifier_advisory_only_in_experience():
    md = """## Experience

### Nimbus Labs | Director (2020-2022)

### Acme, Inc. | Manager (2015-2019)

## Education

### State University | BS (2010-2014)
"""
    r = structure_lint.check(md)
    flagged = [a["entry"] for a in r["advisories"] if a["rule"] == "no-legal-identifier"]
    assert flagged == ["Nimbus Labs | Director (2020-2022)"]
    assert r["ok"] is True
