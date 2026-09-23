---
title: PolicySet item definition
description: Learn how to create a PolicySet item definition when using the Microsoft Fabric REST API.
author: "[AUTHOR]"
ms.author: "[AUTHOR]"
ms.title: PolicySet item definition
ms.service: fabric
ms.date: "[CURRENT_DATE]"
---

# PolicySet definition

This article provides a breakdown of the structure for PolicySet definition items.

## Supported formats

PolicySet items support the JSON format.

## Definition parts

This table lists the PolicySet definition parts.

| Definition part path | Type | Required | Description |
|---|---|---|---|
| `{fileName}` | PolicySet (JSON) | {required_placeholder} | {description_placeholder} |

## Definition example

```json
{
  "parts": [
    {
      "path": "{fileName}",
      "payload": "{base64_placeholder}",
      "payloadType": "InlineBase64"
    }
  ]
}
```

## PolicySet

Schema version: `1.0.0`. Source: `schema.json` in this folder. The schema uses JSON Schema draft-07.

| Property | Type | Required | Description |
|---|---|---|---|
| `$schema` | string | true | Defines the schema to use for a policy set definition. Must be the URI `https://developer.microsoft.com/json-schemas/fabric/item/policySet/definition/1.0.0/schema.json`. |
| `properties` | object | true | Defines the properties of the policy set. See the nested properties below. |
| `policyRules` | policyRule[] | true | Defines the rules in the policy set. |

The root object and every object explicitly defined in this schema disallow additional properties. The arrays `policyRules`, `conditions`, `effects`, and `values` have no minimum or maximum item counts and no uniqueness constraint in this schema. Required arrays must be present, but may be empty under schema validation; platform requirements might be stricter.

### properties

This inline object is the root-level `properties` value, not a named schema definition.

| Property | Type | Required | Description |
|---|---|---|---|
| `scope` | object | true | Defines the scope of the policy set. |

### properties.scope

This inline object specifies the scope of the policy set.

| Property | Type | Required | Description |
|---|---|---|---|
| `type` | string | true | The scope type. Supported values and length restrictions are defined by the policy platform rather than constrained by this schema. |

### policyRule

| Property | Type | Required | Description |
|---|---|---|---|
| `displayName` | string | true | The display name of the policy rule. Free-form text with no length restrictions imposed by this schema. |
| `description` | string | false | An optional description of the policy rule. Free-form text with no length restrictions imposed by this schema. |
| `policy` | string (ExternalDataSharing, ItemCreation) | true | The policy type governed by the rule. |
| `conditions` | condition[] | true | Defines the conditions of the policy rule. Each item must match exactly one condition variant. |
| `effects` | effect[] | true | Defines the effects of the policy rule. |

### condition

No description provided.

This is a complex `oneOf` definition with effective type `object`. It does not declare properties or a required array directly. Each condition must match exactly one of the following definitions; required properties are specified by the selected definition.

| Variant | Type | Description |
|---|---|---|
| staticCondition | object | A static condition whose `type` must be `Static`. |
| dynamicCondition | object | A dynamic condition whose `type` must be `Dynamic`, with a required target property and predicate. |

### staticCondition

| Property | Type | Required | Description |
|---|---|---|---|
| `type` | string | true | Identifies a static condition. Only `Static` is permitted. |

### dynamicCondition

| Property | Type | Required | Description |
|---|---|---|---|
| `type` | string | true | Identifies a dynamic condition. Only `Dynamic` is permitted. |
| `targetProperty` | string | true | The property evaluated by the condition, expressed as an identifier or a dot-separated property path. Each segment must start with an ASCII letter or underscore, followed by ASCII letters, digits, or underscores. |
| `predicate` | predicate | true | Defines the comparison applied to the target property. |

The `targetProperty` pattern is `^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$`. For example, `item.type` matches this pattern. Matching the pattern does not establish that a property is supported by the policy platform.

### predicate

| Property | Type | Required | Description |
|---|---|---|---|
| `operator` | string (AnyOf, NoneOf) | true | The comparison operator applied to the target property and the supplied values. |
| `values` | string[] | true | The values used for comparison with the target property. Each item is a comparison value. Allowed values and length restrictions depend on the target property and are not constrained by this schema. |

### effect

| Property | Type | Required | Description |
|---|---|---|---|
| `type` | string | true | Identifies the effect of the policy rule. Only `Allow` is permitted. |

### PolicySet file example

This example illustrates both condition variants using two rules. The scope type, target property, and comparison value are illustrative strings that satisfy the schema constraints, not a statement of supported platform values. Replace them with values supported by the policy platform before use. Rule evaluation behavior is not specified by this schema.

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/policySet/definition/1.0.0/schema.json",
  "properties": {
    "scope": {
      "type": "{scope_type_placeholder}"
    }
  },
  "policyRules": [
    {
      "displayName": "External data sharing static rule",
      "description": "Illustrates a static condition with an Allow effect.",
      "policy": "ExternalDataSharing",
      "conditions": [
        {
          "type": "Static"
        }
      ],
      "effects": [
        {
          "type": "Allow"
        }
      ]
    },
    {
      "displayName": "External data sharing dynamic rule",
      "description": "Illustrates a property comparison with an Allow effect.",
      "policy": "ExternalDataSharing",
      "conditions": [
        {
          "type": "Dynamic",
          "targetProperty": "item.type",
          "predicate": {
            "operator": "AnyOf",
            "values": [
              "{comparison_value_placeholder}"
            ]
          }
        }
      ],
      "effects": [
        {
          "type": "Allow"
        }
      ]
    }
  ]
}
```
