import copy
import json
from pathlib import Path
import unittest

from jsonschema.validators import validator_for


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "copilot" / "declarative-agent" / "v1.10" / "schema.json"
BASELINE_PATH = ROOT / "copilot" / "declarative-agent" / "v1.9" / "schema.json"


class PluginsCapabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        cls.validator_class = validator_for(cls.schema)
        cls.validator = cls.validator_class(cls.schema)

    def manifest(self, capability):
        return {
            "version": "v1.10",
            "name": "Plugin search agent",
            "description": "Search selected plugin sources.",
            "capabilities": [capability],
        }

    def capability(self, plugin):
        return {"name": "Plugins", "plugins": [plugin]}

    def test_schema_and_local_references_are_valid(self):
        self.validator_class.check_schema(self.schema)

        def check_refs(value):
            if isinstance(value, dict):
                if "$ref" in value:
                    self.assertTrue(value["$ref"].startswith("#/"))
                    target = self.schema
                    for part in value["$ref"][2:].split("/"):
                        target = target[part.replace("~1", "/").replace("~0", "~")]
                for child in value.values():
                    check_refs(child)
            elif isinstance(value, list):
                for child in value:
                    check_refs(child)

        check_refs(self.schema)

    def test_minimal_and_unscoped_capabilities(self):
        for capability in (
            {"name": "Plugins"},
            self.capability({"plugin_id": "plugin-id"}),
            {"name": "Plugins", "plugins": [
                {"plugin_id": "first"}, {"plugin_id": "second"},
            ]},
        ):
            with self.subTest(capability=capability):
                self.validator.validate(self.manifest(capability))

    def test_all_plugin_scope_fields(self):
        plugin = {
            "plugin_id": "plugin-id",
            "items_by_connector_id": ["connector-id"],
            "items_by_connection_id": ["connection-id"],
            "additional_search_terms": "status:active",
            "items_by_external_url": [{"url": "https://example.com/item"}],
            "items_by_external_id": [{"item_id": "item-id"}],
            "items_by_path": [{"path": "/incidents"}],
            "items_by_container_name": [{"container_name": "incidents"}],
            "items_by_container_url": [{"container_url": "https://example.com"}],
        }
        self.validator.validate(self.manifest(self.capability(plugin)))

    def test_invalid_plugins_are_rejected(self):
        invalid = [
            {"name": "Plugins", "plugins": []},
            {"name": "Plugins", "plugins": {}},
            {"name": "Plugins", "plugins": None},
            {"name": "Plugins", "connections": []},
            {"name": "Plugins", "unknown": True},
            self.capability({}),
            self.capability({"plugin_id": 123}),
            self.capability({"plugin_id": None}),
            self.capability({"plugin_id": "id", "unknown": True}),
            self.capability({"plugin_id": "id", "connection_id": "id"}),
            {"name": "UnknownCapability"},
        ]
        for field in ("items_by_connector_id", "items_by_connection_id"):
            for value in ("id", [123], [None]):
                invalid.append(self.capability({"plugin_id": "id", field: value}))
        for field, required_key in (
            ("items_by_external_url", "url"),
            ("items_by_external_id", "item_id"),
            ("items_by_path", "path"),
            ("items_by_container_name", "container_name"),
            ("items_by_container_url", "container_url"),
        ):
            for value in ("item", [{}], [{required_key: 123}]):
                invalid.append(self.capability({"plugin_id": "id", field: value}))
        invalid.append(self.capability({
            "plugin_id": "id", "additional_search_terms": ["not a string"],
        }))
        for capability in invalid:
            with self.subTest(capability=capability):
                self.assertFalse(self.validator.is_valid(self.manifest(capability)))

    def test_existing_capabilities_remain_unchanged(self):
        old_definitions = self.baseline["$defs"]["capabilities"]
        new_definitions = self.schema["$defs"]["capabilities"]
        for name, definition in old_definitions.items():
            if name != "base-capability":
                with self.subTest(capability=name):
                    self.assertEqual(definition, new_definitions[name])
        for name, definition in self.baseline["$defs"].items():
            if name != "capabilities":
                self.assertEqual(definition, self.schema["$defs"][name])
        for capability in (
            {"name": "GraphConnectors"},
            {"name": "GraphConnectors", "connections": [{"connection_id": "id"}]},
            {"name": "WebSearch"},
            {"name": "People"},
            {"name": "OneDriveAndSharePoint"},
        ):
            self.validator.validate(self.manifest(capability))
        combined = self.manifest(self.capability({"plugin_id": "id"}))
        combined["capabilities"].append({"name": "GraphConnectors"})
        self.validator.validate(combined)

    def test_shared_scopes_match_graph_connectors(self):
        connection_fields = self.schema["$defs"]["connection"]["properties"]
        plugin_fields = self.schema["$defs"]["plugin"]["properties"]
        for field, definition in connection_fields.items():
            if field != "connection_id":
                self.assertEqual(definition, plugin_fields[field])

    def test_empty_optional_scopes_and_duplicate_container_rules(self):
        plugin = {"plugin_id": "id", "items_by_connector_id": [],
                  "items_by_connection_id": [], "items_by_path": []}
        self.validator.validate(self.manifest(self.capability(plugin)))
        for field, key in (
            ("items_by_container_name", "container_name"),
            ("items_by_container_url", "container_url"),
        ):
            scoped = copy.deepcopy(plugin)
            scoped[field] = [{key: "same"}, {key: "same"}]
            self.assertFalse(self.validator.is_valid(self.manifest(self.capability(scoped))))

    def test_version_identity_is_enforced(self):
        manifest = self.manifest({"name": "Plugins"})
        manifest["version"] = "v1.9"
        self.assertFalse(self.validator.is_valid(manifest))


if __name__ == "__main__":
    unittest.main()
