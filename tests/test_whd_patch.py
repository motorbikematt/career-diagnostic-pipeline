import whd_anchors
import whd_patch


def test_apply_patch_appends_to_section_and_changelog(synthetic_whd):
    before_anchors = whd_anchors.list_anchors(synthetic_whd)
    out = whd_patch.apply_patch(
        synthetic_whd,
        anchor_id="nimbus-labs",
        content="- Ran a pricing A/B test that lifted activation 12% (new evidence).",
        changelog_note="added A/B test evidence to nimbus-labs (Anthropic run)",
        on="2026-07-06",
    )
    # content landed inside the nimbus-labs section
    section = whd_anchors.resolve_anchor(out, "nimbus-labs")
    assert "pricing A/B test that lifted activation 12%" in section
    # it did NOT bleed into circuit-dynamics
    assert "pricing A/B test" not in whd_anchors.resolve_anchor(out, "circuit-dynamics")
    # changelog entry appended
    changelog = whd_anchors.resolve_anchor(out, "changelog")
    assert "2026-07-06 - added A/B test evidence to nimbus-labs" in changelog
    # every original anchor still present
    assert set(before_anchors).issubset(set(whd_anchors.list_anchors(out)))


def test_apply_patches_respects_status_and_worthiness(synthetic_whd):
    patches = [
        {"kind": "evidence", "target_anchor": "nimbus-labs", "content": "- durable fact A",
         "whd_worthy": True, "status": "approved", "note": "A"},
        {"kind": "fact", "target_anchor": "circuit-dynamics", "content": "- proposed only",
         "whd_worthy": True, "status": "proposed", "note": "B"},
        {"kind": "correction", "target_anchor": "circuit-dynamics", "content": "- app-specific framing",
         "whd_worthy": False, "status": "approved", "note": "C"},
    ]
    out, applied, _ = whd_patch.apply_patches(synthetic_whd, patches, on="2026-07-06")
    assert applied == ["nimbus-labs"]  # only the approved + whd_worthy one
    assert "durable fact A" in out
    assert "proposed only" not in out       # not approved
    assert "app-specific framing" not in out  # not whd_worthy


def test_hard_no_marker_patch(synthetic_whd):
    out = whd_patch.apply_patch(
        synthetic_whd, "nimbus-labs",
        content="- hard-no: ROS experience (confirmed 2026-07-06)",
        changelog_note="recorded hard-no: ROS", on="2026-07-06",
    )
    assert "hard-no: ROS experience (confirmed 2026-07-06)" in whd_anchors.resolve_anchor(out, "nimbus-labs")


def test_missing_anchor_raises(synthetic_whd):
    import pytest
    with pytest.raises(KeyError):
        whd_patch.apply_patch(synthetic_whd, "role-99", "- x", "note")
