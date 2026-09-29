# PostgreSQL database definition

The Microsoft Fabric `PostgreSQLDatabase` item uses the `pgschema` definition format. This document describes the current definition version `1.0.0` and its representations. The JSON Schema in this directory validates only the decoded `manifest.json` part, not the complete item.

## Workload files

The complete workload definition requires `manifest.json` and `main.sql` at its root. It can also contain additional `.sql` files at relative paths, including subdirectories. Other workload-owned file types are not part of this bundle contract.

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

The optional directories, SQL filenames, and file counts are illustrative, not a required or exhaustive inventory. Additional SQL files can use other relative paths.

### Public `pgschema` workload representation

The public `pgschema` workload export emits **one workload part**, named `definition.pgschema`, with `payloadType` set to `InlineBase64`. Base64-decoding its `payload` produces a ZIP archive containing the same required root `manifest.json` and `main.sql` and any optional SQL files at their relative paths.

The ZIP does **not** contain `.platform`. It is the per-item workload ZIP, not a platform-level export container. One workload part does not mean that the complete REST response has only one part: Fabric metadata is handled separately.

## Manifest part schema

The decoded `manifest.json` is:

```json
{
  "format": "pgschema",
  "version": "1.0.0"
}
```

Both properties are required strings with the exact, case-sensitive values shown. Property order is insignificant. No other properties, including an instance-level `$schema`, are allowed.

Associate `manifest.json` with this schema externally in the consuming editor or validation tool:

<https://developer.microsoft.com/json-schemas/fabric/item/postgreSQLDatabase/definition/manifest/1.0.0/schema.json>

The schema document declares the Draft-07 dialect and its own `$id`; those declarations are not manifest properties. Leave the manifest contents unchanged when associating the schema.

Validation covers only the parsed manifest object. It does not validate SQL grammar, SQL include or object dependencies, required filesystem or ZIP members, archive safety, `.platform`, or the REST envelope. Consumers must check the complete bundle separately; a valid manifest alone is not a valid complete item definition.

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
