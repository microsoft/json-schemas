# PostgreSQL database definition

The Microsoft Fabric `PostgreSQLDatabase` item uses the `pgschema` definition format. This document describes the current definition version `1.0.0` and its representations. The JSON Schema in this directory validates only the decoded `manifest.json` part, not the complete item.

## Workload files

The complete workload definition requires one `manifest.json` and one `main.sql` at its root. The [layout descriptor](./definitionStructure/1.0.0/definitionStructure.json) records these required singleton files and eleven optional SQL groups. Other workload-owned file types are not part of this bundle contract.

### Expanded Git and default workload representation

Git integration and the default workload export emit the workload files individually as expanded text parts. In Git, they appear as individual files, not as `definition.pgschema`. A representative item directory is:

```text
Example.PostgreSQLDatabase\
|-- .platform                 # Fabric-owned metadata, not a workload file
|-- manifest.json             # Required workload manifest
|-- main.sql                  # Required workload SQL
|-- domains\
|   `-- example.sql            # Optional SQL file
|-- functions\
|   `-- example.sql            # Optional SQL file
|-- tables\
|   `-- example.sql            # Optional SQL file
|-- types\
|   `-- example.sql            # Optional SQL file
`-- views\
    `-- example.sql            # Optional SQL file
```

This directory tree shows a subset of the optional SQL groups. SQL filenames are illustrative; the complete group inventory is listed below.

### Public `pgschema` workload representation

The public `pgschema` workload export emits **one workload part**, named `definition.pgschema`, with `payloadType` set to `InlineBase64`. Base64-decoding its `payload` produces a ZIP archive containing the same required root `manifest.json` and `main.sql` and any optional SQL files at their relative paths.

The ZIP does **not** contain `.platform`. It is the per-item workload ZIP, not a platform-level export container. One workload part does not mean that the complete REST response has only one part: Fabric metadata is handled separately.

## Definition layout metadata

The [definitionStructure.json descriptor](./definitionStructure/1.0.0/definitionStructure.json) uses the [common definition-structure schema](https://developer.microsoft.com/json-schemas/fabric/common/definition-structure/1.0.0/schema.json). Its root `version` is `1.0.0` and its `format` is `pgschema`. It is layout metadata, not a workload payload or an additional member of the expanded Git definition or workload ZIP.

The descriptor records `manifest.json` as JSON with a reference to the [manifest schema](./definition/manifest/1.0.0/schema.json), and `main.sql` as the SQL include and index entry script. Both have `minCount: 1` and `maxCount: 1`. Only the JSON manifest has a `schemaRef`; SQL entries have `type: sql` and no JSON schema reference.

All eleven optional groups have `minCount: 0`, with no maximum count specified:

| Path pattern | Contents |
| --- | --- |
| `types/*.sql` | Database type declarations. |
| `domains/*.sql` | Database domain declarations. |
| `sequences/*.sql` | Structural sequence declarations. |
| `functions/*.sql` | Database routine source. |
| `procedures/*.sql` | Stored procedure declarations and source. |
| `aggregates/*.sql` | Aggregate declarations. |
| `tables/*.sql` | Table declarations and associated constraints, indexes, and triggers. |
| `views/*.sql` | View declarations. |
| `materialized_views/*.sql` | Materialized view declarations and associated indexes and comments. |
| `privileges/*.sql` | Object and column GRANT and REVOKE statements. |
| `default_privileges/*.sql` | Schema-scoped default GRANT and REVOKE statements. |

The descriptor describes file paths and cardinality; it does not validate SQL contents or establish dependency ordering or import behavior.

## Manifest part schema

The decoded `manifest.json` is:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/postgreSQLDatabase/definition/manifest/1.0.0/schema.json",
  "format": "pgschema",
  "version": "1.0.0"
}
```

All three properties are required strings with the exact, case-sensitive values shown. Property order is insignificant, and no other properties are allowed. The required `$schema` marker is a URI fixed to the manifest schema identifier. The `version` also follows a three-component, no-leading-zero pattern; its fixed value remains `1.0.0`, so the pattern does not enable other versions. The [inline example](./definition/manifest/1.0.0/examples/inline.json) contains exactly these three values.

The manifest schema's canonical identifier is:

<https://developer.microsoft.com/json-schemas/fabric/item/postgreSQLDatabase/definition/manifest/1.0.0/schema.json>

The schema document declares the Draft-07 dialect through its own `$schema` and the canonical identifier through `$id`. In contrast, the manifest's required `$schema` property identifies that manifest schema, not the Draft-07 meta-schema.

JSON Schema validation covers only the parsed manifest object, not the layout descriptor. It does not validate SQL grammar, SQL include or object dependencies, required filesystem or ZIP members, archive safety, `.platform`, or the REST envelope. Neither manifest validation nor layout metadata proves SQL semantics, import behavior, dependency ordering, ZIP safety, or publication of these artifacts. Consumers must check the complete bundle separately; a valid manifest alone is not a valid complete item definition.

## Fabric metadata and REST transport

Fabric owns the separate `.platform` metadata file. Use the existing [platform properties 2.0.0 schema](https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json) for that file, not the manifest schema. The [Git source code format](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/source-code-format) describes the platform-owned files and public item-directory naming conventions.

The generic REST `definition.parts[]` envelope transports parts using `path`, `payload`, and `payloadType`. It is separate from both the workload files and their per-item ZIP. With the public `pgschema` representation, `definition.pgschema` is the workload part in that envelope; `.platform` is a separate platform part, not an archive member. See [item definition overview](https://learn.microsoft.com/en-us/rest/api/fabric/articles/item-management/definitions/item-definition-overview) for platform metadata handling and [Get Item Definition](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/get-item-definition) for the transport envelope.

These platform references establish shared metadata and transport conventions, not the PostgreSQL workload's file format.

## Version domains

| Version | Meaning |
| --- | --- |
| Manifest `version`: `1.0.0` | The `pgschema` definition format version validated here. |
| `pgschema` generator/tool version | The version of the tool producing the SQL; it is not the manifest definition version. |
| `.platform` `config.version` | The Fabric metadata format version; it is independent of the workload definition and generator versions. |

This schema documents the current manifest contract. It does not add legacy import support or change exported bytes, SQL format, workload behavior, or the definition version.
