# JSON Schema Tests

This directory contains automated tests to validate the JSON schemas in this repository.

## Prerequisites

- Python 3.7 or higher
- pytest

Install pytest if you haven't already:

```powershell
pip install pytest
```

## Running Tests

### Run all tests

```powershell
pytest tests/validate-fabric-schemas_test.py
```

### Run with verbose output

```powershell
pytest tests/validate-fabric-schemas_test.py -v
```

### Run with detailed failure information

```powershell
pytest tests/validate-fabric-schemas_test.py -vv
```

## Contributing New Tests

When adding new schema validation tests:

1. Follow the existing pattern using `@pytest.mark.parametrize` to run tests against all JSON files
2. Use the `find_json_files()` helper to discover schema files
3. Provide clear error messages that include the file path and specific issue
4. Update this README with documentation for your new test

### Current Test Scope

The tests currently validate schemas in the `fabric` directory. To change the scope, modify the `SCHEMA_DIR` constant in `validate-fabric-schemas_test.py`.

## CI/CD Integration

These tests are designed to run in automated pipelines to ensure schema quality before changes are merged.
