"""Legacy WHD -> anchored layout migration (TODO #14)."""
import pytest

import hard_nos
import whd_anchors
import whd_io
import whd_migrate
import whd_patch

LEGACY = """---
canary: whd-canary-abc123
---

**WORK HISTORY DOCUMENT**

**Pat Example**

pat@example.com

---
# Old Co LLC  |  Analyst

May 2009 – June 2015  (6 years)  |  Moffett Field, CA

## Context

- 60. Built the lab
## Work — Projects & Initiatives

**1. Lab ****&**** Shop**

- 61. Designed the shop
## Candid Self-Assessment

- 62. Proud of the lab
# New Co  |  Founder

November 2025 – Present  |  Kettering, OH

## Scope

- Solo founder

**1. Pipeline**

- Problem: data was raw
# Candidate Voice Sample

## Q1: Describe what you do.

*I build tools.*
# Mid Corporation  |  PM

January 2019 – December 2022  |  Remote

## Context

- 10. Shipped things
# Beyond Employment

## Patents

- 25. Widget patent
- 26. Gadget patent
## Domain Expertise (Self-Ranked)

- 38. 1. Audio — deepest
- 39. 2. Hardware
*— Additional roles to be documented —*

Document generated: March 8, 2026 | Updated: June 18, 2026 (v4)
"""


def _migrated():
    return whd_migrate.migrate(LEGACY, on="2026-09-24")


def test_wording_preserved():
    result = whd_migrate.check(LEGACY, _migrated())
    assert result["identical"], result


def test_check_catches_a_reworded_line():
    tampered = _migrated().replace("- Designed the shop", "- Designed the big shop")
    result = whd_migrate.check(LEGACY, tampered)
    assert result["identical"] is False
    assert result["only_in_migrated"] == ["- Designed the big shop"]


def test_anchors_are_stable_slugs():
    anchors = whd_anchors.list_anchors(_migrated())
    for aid in ("new-co", "new-co.scope", "new-co.p1", "mid", "old-co", "old-co.context", "old-co.work",
                "old-co.p1", "old-co.self-assessment", "voice-sample", "beyond-employment",
                "beyond-employment.patents", "beyond-employment.domain-expertise", "changelog"):
        assert aid in anchors, aid


def test_roles_newest_first_and_indexed():
    out = _migrated()
    idx = whd_anchors.role_index(out)
    assert [r["id"] for r in idx] == ["new-co", "mid", "old-co"]
    assert idx[0]["dates"] == "2025-11 to present"
    assert idx[2]["dates"] == "2009-05 to 2015-06"
    assert idx[2]["location"] == "Moffett Field, CA"
    assert out.index("# New Co") < out.index("# Mid Corporation") < out.index("# Old Co LLC")
    assert out.index("# Old Co LLC") < out.index("# Candidate Voice Sample") < out.index("# Beyond Employment")


def test_front_matter_keeps_canary_and_reads_content_date():
    fm = whd_io.read_front_matter(_migrated())
    assert fm["canary"] == "whd-canary-abc123"
    assert fm["version"] == "v5"
    assert fm["content_updated"] == "2026-06-18"
    assert fm["owner"] == "Pat Example"


def test_artifacts_fixed():
    out = _migrated()
    assert "****" not in out
    assert "**1. Lab & Shop**" in out
    assert "- Designed the shop" in out and "- 61." not in out
    assert "1. Audio — deepest" in out  # rank kept, counter dropped
    assert "\n \n" not in out


def test_sections_bound_correctly_for_patches():
    out = _migrated()
    p1 = whd_anchors.resolve_anchor(out, "old-co.p1")
    assert "Designed the shop" in p1 and "Proud of the lab" not in p1
    patched = whd_patch.apply_patch(out, "old-co.p1", "- New evidence", "ev", on="2026-09-24")
    p1 = whd_anchors.resolve_anchor(patched, "old-co.p1")
    assert p1.rstrip().endswith("- New evidence")
    fixed, _ = whd_patch.apply_correction(out, "beyond-employment.patents",
                                          "- Gadget patent\n", "", "drop", on="2026-09-24")
    assert "Gadget patent" not in whd_anchors.resolve_anchor(fixed, "beyond-employment.patents")


def test_footer_moves_out_of_last_section():
    out = _migrated()
    tools = whd_anchors.resolve_anchor(out, "beyond-employment.domain-expertise")
    assert "Document generated" not in tools
    assert out.index("Document generated") < out.index("<!-- anchor: new-co -->")


def test_migrated_passes_other_helpers():
    out = _migrated()
    assert hard_nos.scan(out)["unparsed"] == []
    assert whd_anchors.role_index(out)


def test_refuses_already_anchored():
    with pytest.raises(ValueError, match="already has anchors"):
        whd_migrate.migrate(_migrated())


def test_unrecognized_top_level_section_fails():
    with pytest.raises(ValueError, match="unrecognized"):
        whd_migrate.migrate(LEGACY.replace("# Beyond Employment", "# Hobbies"))


def test_cli_preserves_crlf(tmp_path):
    import subprocess
    import sys
    from conftest import REPO
    legacy = tmp_path / "v4.md"
    legacy.write_bytes(LEGACY.replace("\n", "\r\n").encode("utf-8"))
    out = tmp_path / "v5.md"
    helpers = REPO / ".claude" / "skills" / "resume-fit" / "helpers"
    p = subprocess.run([sys.executable, str(helpers / "whd_migrate.py"), str(legacy), str(out),
                        "--on", "2026-09-24"], capture_output=True, cwd=helpers)
    assert p.returncode == 0, p.stderr
    raw = out.read_bytes()
    assert raw.count(b"\n") == raw.count(b"\r\n")
    p2 = subprocess.run([sys.executable, str(helpers / "whd_migrate.py"), str(legacy), str(out)],
                        capture_output=True, cwd=helpers)
    assert p2.returncode != 0 and b"refusing to overwrite" in p2.stderr
