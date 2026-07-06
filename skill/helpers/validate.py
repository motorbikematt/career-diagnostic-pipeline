"""Pure-Python validator for the artifact schema subset (no external deps
beyond PyYAML).

Schema language (a small JSON-Schema subset expressed in YAML):
  type:       object | list | str | number | bool
  required:   [key, ...]        # object: keys that must be present and non-null
  properties: {key: subschema}  # object: per-key subschemas (validated if present)
  items:      subschema         # list: schema applied to every element

Structural drift fails loudly here (plan section 9), rather than silently
downstream. Raises SchemaError(path, message) on the first violation.
"""
from __future__ import annotations

from pathlib import Path

import yaml

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"

_TYPES = {"object": dict, "list": list, "str": str}


class SchemaError(ValueError):
    def __init__(self, path, message):
        self.path = path or "<root>"
        self.message = message
        super().__init__(f"{self.path}: {message}")


def _check_type(value, typ, path):
    if typ == "number":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise SchemaError(path, f"expected number, got {type(value).__name__}")
        return
    if typ == "bool":
        if not isinstance(value, bool):
            raise SchemaError(path, f"expected bool, got {type(value).__name__}")
        return
    py = _TYPES.get(typ)
    if py is None:
        raise SchemaError(path, f"unknown type in schema: {typ!r}")
    if not isinstance(value, py):
        raise SchemaError(path, f"expected {typ}, got {type(value).__name__}")


def validate(data, schema, path=""):
    """Validate data against schema. Returns True or raises SchemaError."""
    typ = schema.get("type")
    if typ:
        _check_type(data, typ, path)

    # Object rules: applied when type=object, or when object-only keys appear.
    if typ == "object" or "required" in schema or "properties" in schema:
        if not isinstance(data, dict):
            raise SchemaError(path, f"expected object, got {type(data).__name__}")
        for key in schema.get("required", []):
            child = f"{path}.{key}" if path else key
            if key not in data or data[key] is None:
                raise SchemaError(child, "required key missing or null")
        for key, subschema in schema.get("properties", {}).items():
            if key in data and data[key] is not None:
                validate(data[key], subschema, f"{path}.{key}" if path else key)

    # List rules.
    if typ == "list":
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(data):
                validate(item, item_schema, f"{path}[{i}]")

    return True


def load_schema(name: str) -> dict:
    p = SCHEMA_DIR / f"{name}.schema.yaml"
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def validate_file(yaml_path, schema_name: str):
    """Validate a YAML artifact file against a named schema; return the data."""
    data = yaml.safe_load(Path(yaml_path).read_text(encoding="utf-8"))
    validate(data, load_schema(schema_name))
    return data


if __name__ == "__main__":
    import sys

    yaml_path, schema_name = sys.argv[1], sys.argv[2]
    try:
        validate_file(yaml_path, schema_name)
        print(f"OK: {yaml_path} valid against {schema_name}")
    except SchemaError as e:
        print(f"INVALID: {e}")
        sys.exit(1)
