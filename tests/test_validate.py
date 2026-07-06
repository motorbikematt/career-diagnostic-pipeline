import pytest
import validate
from validate import SchemaError

from conftest import RUN


@pytest.mark.parametrize("filename,schema", [
    ("requirements.yaml", "requirements"),
    ("scd.yaml", "scd"),
    ("gapmap.yaml", "gapmap"),
    ("screen.yaml", "screen"),
    ("prescriptions.yaml", "prescriptions"),
])
def test_fixture_artifacts_validate(filename, schema):
    validate.validate_file(RUN / filename, schema)


def test_missing_required_key_raises():
    schema = validate.load_schema("requirements")
    bad = {"company": "X"}  # missing role, hard_requirements, etc.
    with pytest.raises(SchemaError):
        validate.validate(bad, schema)


def test_wrong_type_raises():
    schema = {"type": "object", "properties": {"n": {"type": "number"}}}
    with pytest.raises(SchemaError):
        validate.validate({"n": "not a number"}, schema)


def test_bool_is_not_number():
    schema = {"type": "object", "properties": {"n": {"type": "number"}}}
    with pytest.raises(SchemaError):
        validate.validate({"n": True}, schema)


def test_nested_item_required_key():
    schema = validate.load_schema("gapmap")
    bad = {
        "requirements": [{"id": "x", "kind": "hard"}],  # missing weight/classification/recoverable
        "seeker_archetype": "a",
        "jd_archetype": "b",
    }
    with pytest.raises(SchemaError):
        validate.validate(bad, schema)


def test_null_required_key_raises():
    schema = validate.load_schema("scd")
    bad = {"company": None, "evidence_confidence": "low", "shadow_requirements": []}
    with pytest.raises(SchemaError):
        validate.validate(bad, schema)
