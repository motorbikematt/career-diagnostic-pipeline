"""Newest-first ordering check (TODO #4)."""
import chrono_check


def test_fixture_resume_is_ordered(resume_text):
    r = chrono_check.check(resume_text)
    assert r["ordered"] is True
    assert r["violations"] == []


def test_old_role_first_is_flagged():
    md = """## Experience

### Old Lab - Intern (2008-2009)

- did things

### New Co - Director (2021-present)

- leads things
"""
    r = chrono_check.check(md)
    assert r["ordered"] is False
    assert r["violations"][0]["entry"].startswith("New Co")
    assert r["violations"][0]["is_newer_than"].startswith("Old Lab")


def test_dates_on_next_line_and_bold_entries():
    md = """## Experience

**Acme | Senior PM**
*2020 - Present*

- a

**Beta | PM**
2015 - 2020

- b

**Gamma | Analyst**
2021 - 2022
"""
    r = chrono_check.check(md)
    assert r["ordered"] is False
    assert [v["entry"] for v in r["violations"]] == ["Gamma | Analyst"]


def test_sections_checked_independently():
    md = """## Experience

### A (2020-present)

### B (2010-2019)

## Volunteer

### C (2022-present)

### D (2015-2018)
"""
    assert chrono_check.check(md)["ordered"] is True


def test_undated_entries_listed_not_failed():
    md = """## Experience

### A (2020-present)

### Selected Projects

### B (2010-2019)
"""
    r = chrono_check.check(md)
    assert r["ordered"] is True
    assert [u["entry"] for u in r["undated"]] == ["Selected Projects"]
