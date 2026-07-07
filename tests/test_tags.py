import tags


def test_clean_draft():
    result = tags.scan("# Name\n- Led a team and shipped a product.\n")
    assert result["clean"] is True
    assert result["blocking_total"] == 0


def test_blocking_tags_counted():
    draft = (
        "- [CHANGED] Reframed this bullet.\n"
        "- [CANDIDATE TO SUPPLY: a growth metric] \n"
        "- [NOT INTEGRATED] self-serve keyword\n"
        "VOICE NOTE: this line may need review\n"
    )
    result = tags.scan(draft)
    assert result["clean"] is False
    assert result["counts"]["CANDIDATE TO SUPPLY"] == 1
    assert result["counts"]["NOT INTEGRATED"] == 1
    assert result["counts"]["VOICE NOTE"] == 1
    assert result["counts"]["CHANGED"] == 1  # informational, not blocking
    assert result["blocking_total"] == 3


def test_changed_alone_is_clean():
    # [CHANGED]/[REMOVED] are review markers, not blockers.
    result = tags.scan("- [CHANGED] a line\n- [REMOVED] old line (reason)\n")
    assert result["clean"] is True
