"""hard-no marker listing and review tracking (TODO #11)."""
from datetime import date

import hard_nos
import whd_io

WHD = """---
canary: "x"
hard_no_reviewed: "2026-01-01"
---

<!-- anchor: nimbus-labs -->
# Acme

- hard-no: people management of 5+ reports (confirmed 2025-06-01)
- hard-no: ROS experience (confirmed 2026-08-01)
- hard no: typo marker without date

<!-- anchor: changelog -->
# Changelog

- 2025-06-01 - recorded hard-no: people management (not a marker)
"""
TODAY = date(2026, 9, 24)


def test_lists_markers_with_age_and_anchor():
    r = hard_nos.scan(WHD, today=TODAY)
    assert r["marker_count"] == 2
    first = r["markers"][0]
    assert first["what"] == "people management of 5+ reports"
    assert first["anchor"] == "nimbus-labs"
    assert first["age_days"] == (TODAY - date(2025, 6, 1)).days
    assert [m["what"] for m in r["stale"]] == ["people management of 5+ reports"]


def test_unparsed_mentions_reported_and_changelog_ignored():
    r = hard_nos.scan(WHD, today=TODAY)
    assert [u["text"] for u in r["unparsed"]] == ["- hard no: typo marker without date"]


def test_review_due_after_six_months():
    assert hard_nos.scan(WHD, today=TODAY)["review_due"] is True
    assert hard_nos.scan(WHD, today=date(2026, 3, 1))["review_due"] is False


def test_no_markers_means_no_review_due():
    assert hard_nos.scan("---\ncanary: x\n---\n# Body\n", today=TODAY)["review_due"] is False


def test_mark_reviewed_sets_front_matter_and_keeps_crlf(tmp_path):
    whd = tmp_path / "whd.md"
    whd.write_bytes(WHD.replace("\n", "\r\n").encode("utf-8"))
    hard_nos.mark_reviewed(whd, on="2026-09-24")
    text, eol = whd_io.read_whd(whd)
    assert eol == "\r\n"
    assert whd_io.read_front_matter(text)["hard_no_reviewed"] == "2026-09-24"
    assert hard_nos.scan(text, today=TODAY)["review_due"] is False
