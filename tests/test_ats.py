import ats


def test_fixture_scan(requirements, resume_text):
    r = ats.scan(requirements["ats_keywords"], resume_text)
    assert set(r["missing"]) == {"robotics", "ROS", "SQL"}
    assert "product management" in r["present"]
    assert "cross-functional" in r["present"]
    assert r["coverage"] == 70


def test_word_boundary_not_substring():
    # "ROS" must not match inside "cross" or "across".
    r = ats.scan(["ROS"], "cross-functional work across teams")
    assert r["missing"] == ["ROS"]


def test_case_insensitive():
    r = ats.scan(["Product Strategy"], "led product strategy for the platform")
    assert r["present"] == ["Product Strategy"]


def test_hyphenated_and_multiword():
    r = ats.scan(["A/B testing", "cross-functional"], "ran A/B testing with cross-functional teams")
    assert r["missing"] == []


def test_empty_keywords():
    assert ats.scan([], "anything")["coverage"] == 0
