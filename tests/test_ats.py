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


def test_synonym_abbreviation_in_resume():
    # JD keyword is the canonical term; resume uses the abbreviation.
    r = ats.scan(["Kubernetes"], "ran workloads on k8s clusters")
    assert r["present"] == ["Kubernetes"]


def test_synonym_canonical_in_resume():
    # JD keyword is the abbreviation; resume uses the canonical term.
    r = ats.scan(["k8s"], "ran workloads on kubernetes clusters")
    assert r["present"] == ["k8s"]


def test_synonym_no_false_positive():
    r = ats.scan(["Kubernetes"], "worked with docker containers")
    assert r["missing"] == ["Kubernetes"]


# --- Ambiguous short terms (TODO #2): ordinary English must not count ---------

def test_go_language_not_matched_by_verb():
    assert ats.scan(["Go"], "We go to market fast.")["missing"] == ["Go"]


def test_go_language_not_matched_by_go_to_market():
    assert ats.scan(["Go"], "Owned Go-to-market launch")["missing"] == ["Go"]


def test_go_language_matched_when_written_as_language():
    assert ats.scan(["Go"], "Built services in Go and Python")["present"] == ["Go"]
    assert ats.scan(["Go"], "Built services in golang")["present"] == ["Go"]


def test_rest_api_not_matched_by_the_rest_of():
    assert ats.scan(["REST API"], "Aligned the rest of the team.")["missing"] == ["REST API"]


def test_rest_api_matched_by_rest():
    assert ats.scan(["REST API"], "Designed REST endpoints")["present"] == ["REST API"]


def test_node_not_matched_by_graph_node():
    assert ats.scan(["Node.js"], "Each node in the graph")["missing"] == ["Node.js"]


def test_node_matched_when_capitalized():
    assert ats.scan(["Node.js"], "Backend in Node and Postgres")["present"] == ["Node.js"]


def test_ai_not_matched_by_name():
    assert ats.scan(["AI"], "Worked in Ai Weiwei's studio")["missing"] == ["AI"]
    assert ats.scan(["AI"], "Shipped AI features")["present"] == ["AI"]
    assert ats.scan(["AI"], "Shipped artificial intelligence features")["present"] == ["AI"]


def test_pm_does_not_mean_project_management():
    r = ats.scan(["Project Management"], "Senior PM, product roadmap owner")
    assert r["missing"] == ["Project Management"]


def test_hyphen_compounds_still_count_except_go():
    assert ats.scan(["AI"], "Built AI-native tools")["present"] == ["AI"]
    assert ats.scan(["Machine Learning"], "Shipped ML-based ranking")["present"] == ["Machine Learning"]
    assert ats.scan(["REST API"], "Migrated to REST-based services")["present"] == ["REST API"]
    assert ats.scan(["Go"], "Led Go-to-market")["missing"] == ["Go"]
