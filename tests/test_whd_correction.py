"""Correction patches replace in place (TODO #11)."""
import pytest
import yaml

import whd_anchors
import whd_patch

WHD = """---
canary: "x"
---

<!-- anchor: role-1 -->
# Acme | PM

- Holds 3 patents in imaging.

<!-- anchor: role-1.project-1 -->
**1. Imaging**

- Outcome: 3 patents in imaging filed.

<!-- anchor: voice-sample -->
# Voice

- I talk like this.

<!-- anchor: changelog -->
# Changelog

- 2026-01-01 - Initial WHD created.
"""


def test_correction_replaces_and_logs_old_text():
    out, remaining = whd_patch.apply_correction(
        WHD, "role-1", "Holds 3 patents", "Holds 2 patents",
        "patent count corrected", on="2026-09-24", prompted_by="endless-run")
    section = whd_anchors.resolve_anchor(out, "role-1")
    assert "Holds 2 patents" in section and "Holds 3 patents" not in section
    log = whd_anchors.resolve_anchor(out, "changelog")
    assert 'was "Holds 3 patents", now "Holds 2 patents"; run: endless-run' in log
    assert remaining == []


def test_section_stops_at_sub_anchor_and_leftovers_reported():
    out, remaining = whd_patch.apply_correction(
        WHD, "role-1", "3 patents in imaging", "2 patents in imaging", "fix", on="2026-09-24")
    assert "3 patents in imaging filed" in whd_anchors.resolve_anchor(out, "role-1.project-1")
    assert remaining == ["role-1.project-1"]


def test_correction_must_match_exactly_once():
    with pytest.raises(ValueError, match=r"matched 0 times.*role-1\.project-1"):
        whd_patch.apply_correction(WHD, "role-1", "3 patents in imaging filed", "x", "n")


def test_protected_anchors_refused():
    for anchor in ("voice-sample", "changelog"):
        with pytest.raises(ValueError, match="protected"):
            whd_patch.apply_patch(WHD, anchor, "- x", "n")
        with pytest.raises(ValueError, match="protected"):
            whd_patch.apply_correction(WHD, anchor, "I talk", "x", "n")


def test_apply_file_preserves_crlf(tmp_path):
    whd = tmp_path / "whd.md"
    whd.write_bytes(WHD.replace("\n", "\r\n").encode("utf-8"))
    patches = tmp_path / "patches.yaml"
    patches.write_text(yaml.safe_dump({"patches": [
        {"kind": "correction", "target_anchor": "role-1", "old": "Holds 3", "content": "Holds 2",
         "whd_worthy": True, "status": "approved", "note": "fix"}]}), encoding="utf-8")
    applied, leftovers = whd_patch.apply_file(whd, patches, on="2026-09-24")
    raw = whd.read_bytes()
    assert applied == ["role-1"]
    assert b"Holds 2 patents" in raw
    assert raw.count(b"\n") == raw.count(b"\r\n")  # every line still CRLF
    assert raw.endswith(b"\r\n")
    assert leftovers == {}
    assert yaml.safe_load(patches.read_text(encoding="utf-8"))["patches"][0]["status"] == "applied"


def test_apply_file_twice_is_idempotent(tmp_path):
    whd = tmp_path / "whd.md"
    whd.write_text(WHD, encoding="utf-8")
    patches = tmp_path / "patches.yaml"
    patches.write_text(yaml.safe_dump({"patches": [
        {"kind": "evidence", "target_anchor": "role-1", "content": "- new evidence",
         "whd_worthy": True, "status": "approved", "note": "ev"},
        {"kind": "correction", "target_anchor": "role-1", "old": "Holds 3", "content": "Holds 2",
         "whd_worthy": True, "status": "approved", "note": "fix"}]}), encoding="utf-8")
    whd_patch.apply_file(whd, patches, on="2026-09-24")
    after_first = whd.read_bytes()
    applied, _ = whd_patch.apply_file(whd, patches, on="2026-09-24")  # Phase H re-run
    assert applied == []
    assert whd.read_bytes() == after_first
