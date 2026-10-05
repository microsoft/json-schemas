import json
import os
import glob
import re
import pytest

SCHEMA_DIR = "fabric"
POSTGRESQL_ITEM_DIR = os.path.join(SCHEMA_DIR, "item", "postgreSQLDatabase")
POSTGRESQL_MANIFEST_SCHEMA = os.path.join(
    POSTGRESQL_ITEM_DIR, "definition", "manifest", "1.0.0", "schema.json"
)
POSTGRESQL_MANIFEST_EXAMPLE = os.path.join(
    os.path.dirname(POSTGRESQL_MANIFEST_SCHEMA), "examples", "inline.json"
)
POSTGRESQL_DEFINITION_STRUCTURE = os.path.join(
    POSTGRESQL_ITEM_DIR, "definitionStructure", "1.0.0", "definitionStructure.json"
)
POSTGRESQL_MANIFEST_URI = (
    "https://developer.microsoft.com/json-schemas/fabric/item/"
    "postgreSQLDatabase/definition/manifest/1.0.0/schema.json"
)
NON_SCHEMA_JSON_FILES = {
    POSTGRESQL_MANIFEST_EXAMPLE,
    POSTGRESQL_DEFINITION_STRUCTURE,
}

def find_json_files(root_dir):
    """Yield all .json files under a directory recursively."""
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".json"):
                yield os.path.join(dirpath, filename)

def find_schema_files(root_dir):
    """Yield schemas, excluding only the two named PostgreSQL JSON artifacts."""
    for json_file in find_json_files(root_dir):
        if os.path.normpath(json_file) not in NON_SCHEMA_JSON_FILES:
            yield json_file

def extract_refs(schema, base_path):
    """Recursively extract $ref values from a schema and yield the resolved path."""
    if isinstance(schema, dict):
        for key, value in schema.items():
            if key == "$ref" and isinstance(value, str):
                if not value.startswith("#") and not value.startswith("https://developer.microsoft.com/json-schemas"): # Ignore internal references and our published URLs
                    ref_path = value.split("#")[0]
                    resolved_path = os.path.normpath(os.path.join(base_path, ref_path))
                    yield resolved_path
            else:
                yield from extract_refs(value, base_path)
    elif isinstance(schema, list):
        for item in schema:
            yield from extract_refs(item, base_path)

@pytest.mark.parametrize("json_file", list(find_json_files(SCHEMA_DIR)))
def test_refs_exist(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        try:
            schema = json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON in {json_file}: {e}")

    base_path = os.path.dirname(json_file)
    for ref_path in extract_refs(schema, base_path):
        assert os.path.isfile(ref_path), f"Missing file for $ref in {json_file}: {ref_path}"


@pytest.mark.parametrize("json_file", list(find_schema_files(SCHEMA_DIR)))
def test_id_properties_exist(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        try:
            schema = json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON in {json_file}: {e}")
    
    assert "$id" in schema, f"Missing $id property in {json_file}"
    assert isinstance(schema["$id"], str), f"$id property must be a string in {json_file}"
    assert schema["$id"].startswith("https://developer.microsoft.com/json-schemas"), \
        f"$id property in {json_file} must start with 'https://developer.microsoft.com/json-schemas', got: {schema['$id']}"

@pytest.mark.parametrize("json_file", list(find_schema_files(SCHEMA_DIR)))
def test_schema_properties_exist(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        try:
            schema = json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON in {json_file}: {e}")
    
    assert "$schema" in schema, f"Missing $schema property in {json_file}"
    assert isinstance(schema["$schema"], str), f"$schema property must be a string in {json_file}"
    assert schema["$schema"].startswith("http://json-schema.org/") or schema["$schema"].startswith("https://json-schema.org/"), \
        f"$schema property in {json_file} must start with 'http://json-schema.org/', got: {schema['$schema']}"


def test_non_schema_artifact_discovery():
    json_files = set(find_json_files(SCHEMA_DIR))
    schema_files = set(find_schema_files(SCHEMA_DIR))
    assert NON_SCHEMA_JSON_FILES <= json_files, "Missing PostgreSQL JSON artifacts"
    assert json_files - schema_files == NON_SCHEMA_JSON_FILES
    assert POSTGRESQL_MANIFEST_SCHEMA in schema_files


@pytest.fixture
def postgresql_manifest_schema():
    with open(POSTGRESQL_MANIFEST_SCHEMA, "r", encoding="utf-8") as f:
        return json.load(f)


def test_postgresql_manifest_contract(postgresql_manifest_schema):
    assert postgresql_manifest_schema == {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": POSTGRESQL_MANIFEST_URI,
        "type": "object",
        "description": (
            "Describes the pgschema manifest for a Fabric PostgreSQL Database item "
            "definition, identifying its serialization format and version."
        ),
        "additionalProperties": False,
        "required": ["$schema", "format", "version"],
        "properties": {
            "$schema": {
                "type": "string",
                "description": "Identifies the JSON schema for this manifest.",
                "format": "uri",
                "const": POSTGRESQL_MANIFEST_URI,
            },
            "format": {
                "type": "string",
                "description": "The definition serialization format, fixed to pgschema.",
                "const": "pgschema",
            },
            "version": {
                "type": "string",
                "description": (
                    "The supported pgschema definition serialization version, fixed to 1.0.0."
                ),
                "const": "1.0.0",
                "pattern": r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$",
            },
        },
    }, f"Unexpected manifest contract in {POSTGRESQL_MANIFEST_SCHEMA}"


@pytest.mark.parametrize("version, matches_pattern", [
    ("0.0.0", True),
    ("1.0.0", True),
    ("10.20.30", True),
    ("1", False),
    ("1.0", False),
    ("1.0.0.0", False),
    ("01.0.0", False),
    ("1.00.0", False),
    ("1.0.00", False),
    ("v1.0.0", False),
    ("1.0.0-beta", False),
    ("1.0.0+build", False),
    ("-1.0.0", False),
    ("1.0.0\n", False),
])
def test_postgresql_manifest_version_pattern(
    postgresql_manifest_schema, version, matches_pattern
):
    pattern = postgresql_manifest_schema["properties"]["version"]["pattern"]
    assert (re.fullmatch(pattern, version) is not None) == matches_pattern


def test_postgresql_manifest_example(postgresql_manifest_schema):
    with open(POSTGRESQL_MANIFEST_EXAMPLE, "r", encoding="utf-8") as f:
        example = json.load(f)
    assert example == {
        name: postgresql_manifest_schema["properties"][name]["const"]
        for name in postgresql_manifest_schema["required"]
    }, f"Unexpected manifest example in {POSTGRESQL_MANIFEST_EXAMPLE}"


def test_postgresql_definition_structure_contract():
    with open(POSTGRESQL_DEFINITION_STRUCTURE, "r", encoding="utf-8") as f:
        descriptor = json.load(f)
    optional_sql_groups = [
        ("types/*.sql", "Database type declarations."),
        ("domains/*.sql", "Database domain declarations."),
        ("sequences/*.sql", "Structural sequence declarations."),
        ("functions/*.sql", "Database routine source."),
        ("procedures/*.sql", "Stored procedure declarations and source."),
        ("aggregates/*.sql", "Aggregate declarations."),
        ("tables/*.sql", "Table declarations and associated constraints, indexes, and triggers."),
        ("views/*.sql", "View declarations."),
        ("materialized_views/*.sql", "Materialized view declarations and associated indexes and comments."),
        ("privileges/*.sql", "Object and column GRANT and REVOKE statements."),
        ("default_privileges/*.sql", "Schema-scoped default GRANT and REVOKE statements."),
    ]
    assert descriptor == {
        "$schema": (
            "https://developer.microsoft.com/json-schemas/fabric/common/"
            "definition-structure/1.0.0/schema.json"
        ),
        "version": "1.0.0",
        "format": "pgschema",
        "files": [
            {
                "path": "manifest.json",
                "type": "json",
                "description": (
                    "The manifest identifying the pgschema definition serialization format and version."
                ),
                "minCount": 1,
                "maxCount": 1,
                "schemaRef": [{"uri": POSTGRESQL_MANIFEST_URI}],
            },
            {
                "path": "main.sql",
                "type": "sql",
                "description": (
                    "The SQL include and index entry script for the database structure and source files."
                ),
                "minCount": 1,
                "maxCount": 1,
            },
        ] + [
            {"path": path, "type": "sql", "description": description, "minCount": 0}
            for path, description in optional_sql_groups
        ],
    }, f"Unexpected layout contract in {POSTGRESQL_DEFINITION_STRUCTURE}"
