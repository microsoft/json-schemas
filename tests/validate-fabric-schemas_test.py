import json
import os
import glob
import pytest
import jsonschema
from jsonschema.validators import validator_for

SCHEMA_DIR = "fabric"

# ---------------------------------------------------------------------------
# Document classification: every fabric/**.json is exactly ONE of three kinds
# ---------------------------------------------------------------------------
# Not every .json file under fabric/ is a JSON *Schema*. Each file falls into
# exactly one of these categories, decided by its top-level "$schema":
#
#   1. JSON Schema document - "$schema" points at json-schema.org (e.g.
#      "http://json-schema.org/draft-07/schema#"). These carry a "$id" on
#      developer.microsoft.com and describe the shape of other documents. They
#      run the schema-only contract tests (top-level $id + json-schema.org
#      $schema) AND are structurally validated against their declared dialect's
#      metaschema (test_schema_documents_are_valid_json_schema), which catches
#      malformed schemas that the $id/$schema/$ref convention checks miss. See
#      is_json_schema_document().
#
#   2. Recognized instance (definitionStructure ONLY) - "$schema" is one of OUR
#      published definition-structure META-schema URLs on developer.microsoft.com
#      (any version under DEFINITION_STRUCTURE_PREFIX), meaning "validate ME
#      against that meta-schema". These are data, not schemas: they have no
#      "$id" and must NOT be held to the schema-only contract. They are skipped
#      by the contract tests and positively validated against their meta-schema
#      by test_instance_documents_validate_against_meta_schema(). See
#      is_recognized_instance().
#
#   3. Anything else - neither a JSON Schema document nor a recognized instance.
#      This must FAIL LOUDLY (test_document_is_recognized) so that a new/unknown
#      document type can never silently pass by being mistaken for an instance.
#      If a legitimate new instance type appears, extend the classifier.
# ---------------------------------------------------------------------------

PUBLISHED_PREFIX = "https://developer.microsoft.com/json-schemas/"

# Published prefix of the definition-structure meta-schema. Version-tolerant:
# matches .../definition-structure/1.0.0/... and any future x.y.z.
DEFINITION_STRUCTURE_PREFIX = "https://developer.microsoft.com/json-schemas/fabric/common/definition-structure/"


def is_json_schema_document(doc):
    """Return True iff *doc* is a JSON Schema document (category 1).

    A JSON Schema document declares a JSON Schema dialect: its top-level
    "$schema" is a string starting with "http://json-schema.org/" or
    "https://json-schema.org/".
    """
    if not isinstance(doc, dict):
        return False
    schema_uri = doc.get("$schema")
    return isinstance(schema_uri, str) and (
        schema_uri.startswith("http://json-schema.org/")
        or schema_uri.startswith("https://json-schema.org/")
    )


def is_recognized_instance(doc):
    """Return True iff *doc* is a recognized instance document (category 2).

    Currently the only recognized instance type is definitionStructure: its
    top-level "$schema" points at the published definition-structure meta-schema
    (any version under DEFINITION_STRUCTURE_PREFIX).
    """
    if not isinstance(doc, dict):
        return False
    schema_uri = doc.get("$schema")
    return isinstance(schema_uri, str) and schema_uri.startswith(DEFINITION_STRUCTURE_PREFIX)


def find_json_files(root_dir):
    """Yield all .json files under a directory recursively."""
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".json"):
                yield os.path.join(dirpath, filename)

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


def _build_schema_store():
    """Map every schema's ``$id`` -> its parsed content, for OFFLINE $ref
    resolution.

    Only JSON Schema documents (those carrying a string ``$id``) are indexed;
    instance/data documents have no ``$id`` and are skipped. This store lets the
    meta-schema validation resolve ``$ref``s that use full published
    developer.microsoft.com URLs (e.g. file-structure) from local files with no
    network I/O.
    """
    store = {}
    for json_file in find_json_files(SCHEMA_DIR):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                doc = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        if isinstance(doc, dict) and isinstance(doc.get("$id"), str):
            store[doc["$id"]] = doc
    return store


# Built once per test session; scanning all schemas is cheap.
_SCHEMA_STORE = _build_schema_store()


def _make_meta_schema_validator(meta_schema):
    """Build a Draft7 validator for *meta_schema* that resolves every
    developer.microsoft.com ``$ref`` from the local schema store (no network).

    Prefers the modern ``referencing`` registry API (jsonschema >= 4.18) and
    falls back to the deprecated ``RefResolver`` for older jsonschema versions.
    """
    from jsonschema import Draft7Validator

    try:
        from referencing import Registry, Resource
        from referencing.jsonschema import DRAFT7

        resources = []
        for uri, contents in _SCHEMA_STORE.items():
            try:
                resource = Resource.from_contents(contents)
            except Exception:
                # Contents without a recognizable $schema dialect: assume draft-07.
                resource = DRAFT7.create_resource(contents)
            resources.append((uri, resource))
        registry = Registry().with_resources(resources)
        return Draft7Validator(meta_schema, registry=registry)
    except ImportError:
        import jsonschema

        resolver = jsonschema.RefResolver(
            base_uri="", referrer=meta_schema, store=dict(_SCHEMA_STORE)
        )
        return Draft7Validator(meta_schema, resolver=resolver)


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


@pytest.mark.parametrize("json_file", list(find_json_files(SCHEMA_DIR)))
def test_id_properties_exist(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        try:
            schema = json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON in {json_file}: {e}")

    if not is_json_schema_document(schema):
        pytest.skip("instance/data document, validated against its meta-schema instead")

    assert "$id" in schema, f"Missing $id property in {json_file}"
    assert isinstance(schema["$id"], str), f"$id property must be a string in {json_file}"
    assert schema["$id"].startswith("https://developer.microsoft.com/json-schemas"), \
        f"$id property in {json_file} must start with 'https://developer.microsoft.com/json-schemas', got: {schema['$id']}"

@pytest.mark.parametrize("json_file", list(find_json_files(SCHEMA_DIR)))
def test_schema_properties_exist(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        try:
            schema = json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON in {json_file}: {e}")

    if not is_json_schema_document(schema):
        pytest.skip("instance/data document, validated against its meta-schema instead")

    assert "$schema" in schema, f"Missing $schema property in {json_file}"
    assert isinstance(schema["$schema"], str), f"$schema property must be a string in {json_file}"
    assert schema["$schema"].startswith("http://json-schema.org/") or schema["$schema"].startswith("https://json-schema.org/"), \
        f"$schema property in {json_file} must start with 'http://json-schema.org/', got: {schema['$schema']}"


@pytest.mark.parametrize("json_file", list(find_json_files(SCHEMA_DIR)))
def test_schema_documents_are_valid_json_schema(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        try:
            doc = json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON in {json_file}: {e}")

    if not is_json_schema_document(doc):
        pytest.skip("not a JSON Schema document; structural validation applies to schemas only")

    cls = validator_for(doc)
    # Validate structural well-formedness for the declared dialect; this catches
    # malformed schemas (for example bad properties nesting) that string/ref
    # convention checks miss, while staying offline via bundled metaschemas.
    try:
        cls.check_schema(doc)
    except jsonschema.exceptions.SchemaError as e:
        pytest.fail(f"Schema {json_file} is not a valid {cls.__name__} schema: {e.message}")


@pytest.mark.parametrize("json_file", list(find_json_files(SCHEMA_DIR)))
def test_instance_documents_validate_against_meta_schema(json_file):
    """Recognized instance documents must validate against their meta-schema.

    Only runs for category-2 (recognized instance) documents; JSON Schema
    documents and any unrecognized document are skipped here (unrecognized docs
    are caught by test_document_is_recognized instead). The instance's top-level
    ``$schema`` names one of our published meta-schemas on developer.microsoft.com;
    that URL is mapped to a LOCAL file and used to validate the instance with all
    ``$ref``s resolved OFFLINE from the schema store.
    """
    with open(json_file, "r", encoding="utf-8") as f:
        try:
            doc = json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON in {json_file}: {e}")

    if not is_recognized_instance(doc):
        pytest.skip("not a recognized instance document")

    meta_url = doc.get("$schema") if isinstance(doc, dict) else None
    assert isinstance(meta_url, str) and meta_url.startswith(PUBLISHED_PREFIX), (
        f"Instance document {json_file} must declare a '$schema' starting with "
        f"'{PUBLISHED_PREFIX.rstrip('/')}', got: {meta_url!r}"
    )

    # Map the published meta-schema URL to a local file under the repo root.
    relative_path = meta_url[len(PUBLISHED_PREFIX):]
    meta_schema_path = os.path.normpath(os.path.join(SCHEMA_DIR, os.pardir, relative_path))
    assert os.path.isfile(meta_schema_path), (
        f"Meta-schema file for {json_file} not found locally: {meta_schema_path} "
        f"(from $schema {meta_url})"
    )

    with open(meta_schema_path, "r", encoding="utf-8") as f:
        meta_schema = json.load(f)

    validator = _make_meta_schema_validator(meta_schema)
    errors = sorted(validator.iter_errors(doc), key=lambda e: list(e.path))
    if errors:
        first = errors[0]
        location = "/".join(str(p) for p in first.path) or "<root>"
        pytest.fail(
            f"Instance {json_file} failed validation against meta-schema "
            f"{meta_schema_path} at '{location}': {first.message}"
        )


@pytest.mark.parametrize("json_file", list(find_json_files(SCHEMA_DIR)))
def test_document_is_recognized(json_file):
    """Every fabric json must be a recognized document type (category 1 or 2).

    Guards against a new/unknown document silently passing by being mistaken for
    an instance: a file that is neither a JSON Schema document nor a recognized
    definitionStructure instance fails loudly here.
    """
    with open(json_file, "r", encoding="utf-8") as f:
        try:
            doc = json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON in {json_file}: {e}")

    if is_json_schema_document(doc) or is_recognized_instance(doc):
        return

    schema_uri = doc.get("$schema") if isinstance(doc, dict) else None
    pytest.fail(
        f"Unrecognized document type in {json_file}: not a JSON Schema document "
        f"($schema is not json-schema.org) and not a recognized definitionStructure "
        f"instance ($schema does not start with the definition-structure meta-schema "
        f"URL '{DEFINITION_STRUCTURE_PREFIX}'). Got $schema={schema_uri!r}. "
        f"If this is a new instance type, extend the classifier."
    )