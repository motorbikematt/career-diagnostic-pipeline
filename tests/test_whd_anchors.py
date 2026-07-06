import pytest
import whd_anchors


def test_front_matter_parses(synthetic_whd):
    fm = whd_anchors.parse_front_matter(synthetic_whd)
    assert fm["owner"] == "Alex Rivera"
    assert fm["canary"].startswith("WHD-CANARY-")


def test_role_index(synthetic_whd):
    roles = whd_anchors.role_index(synthetic_whd)
    assert [r["id"] for r in roles] == ["role-1", "role-2"]
    assert roles[0]["company"] == "Nimbus Labs"


def test_list_anchors(synthetic_whd):
    anchors = whd_anchors.list_anchors(synthetic_whd)
    for expected in ["role-1", "role-1.project-1", "role-2", "voice-sample", "changelog"]:
        assert expected in anchors


def test_resolve_role_section(synthetic_whd):
    body = whd_anchors.resolve_anchor(synthetic_whd, "role-2")
    assert body.startswith("# Circuit Dynamics")
    # Stops before the next anchor (role-2.project-1).
    assert "Smart Camera Hardware Lifecycle" not in body


def test_resolve_project_section(synthetic_whd):
    body = whd_anchors.resolve_anchor(synthetic_whd, "role-1.project-1")
    assert "Platform Roadmap Overhaul" in body
    assert "Experimentation Program" not in body  # next project excluded


def test_missing_anchor_raises(synthetic_whd):
    with pytest.raises(KeyError):
        whd_anchors.resolve_anchor(synthetic_whd, "role-99")
