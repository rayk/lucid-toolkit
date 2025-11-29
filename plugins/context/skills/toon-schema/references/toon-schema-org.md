# TOON + Schema.org Integration Guide

## Overview

TOON (Token-Oriented Object Notation) combined with schema.org vocabulary creates a semantic, token-efficient format for structured data exchange with LLMs.

**Why this combination works:**
- TOON reduces tokens by 40-60% compared to JSON
- Schema.org types are pre-trained into LLMs (billions of web examples)
- Semantic types reduce reasoning overhead - LLMs recognize `@type: Action` without explanation

## TOON Format Basics

### Primitives

```toon
name: Ada                    # Unquoted string
age: 30                      # Number
active: true                 # Boolean
deleted: null                # Null
bio: "Has: special chars"    # Quoted when contains : or special chars
```

### Objects (Indentation-Based)

```toon
user:
  id: 123
  name: Ada
  profile:
    verified: true
```

### Arrays

**Primitive arrays (inline):**
```toon
tags[3]: admin,ops,dev
```

**Tabular arrays (uniform objects) - most common:**
```toon
items[2]{sku,qty,price}:
  A1,2,9.99
  B2,1,14.5
```

**Tab delimiter (more token-efficient):**
```toon
items[2]{sku,qty,price|tab}:
  A1	2	9.99
  B2	1	14.5
```

**Non-uniform arrays:**
```toon
items[3]:
  - 1
  - text value
  - nested: object
```

### Quoting Rules

Quote strings when they:
- Are empty or have leading/trailing whitespace
- Equal `true`, `false`, or `null`
- Contain `:`, `"`, `\`, brackets, braces
- Contain the delimiter (comma or tab)
- Start with hyphen followed by character

## Schema.org Integration

### Core Properties

| Property | Purpose | Example |
|----------|---------|---------|
| `@type` | Declares semantic type | `@type: CreateAction` |
| `@id` | Unique identifier | `@id: outcome/005-auth` |
| `name` | Human-readable name | `name: authentication-provider` |
| `description` | Detailed description | `description: Implements JWT auth` |
| `actionStatus` | Current state | `actionStatus: ActiveActionStatus` |
| `startTime` | ISO 8601 start | `startTime: 2025-11-18T10:00:00Z` |
| `endTime` | ISO 8601 end | `endTime: 2025-11-18T11:30:00Z` |
| `result` | Outcome of action | `result: Successfully completed` |
| `error` | Error details | `error: Context exhausted` |
| `agent` | Who performed | `agent: Claude` |
| `object` | What was acted upon | `object: outcome_track.json` |

### ActionStatusType Values

| Status | Meaning | Lucid Mapping |
|--------|---------|---------------|
| `PotentialActionStatus` | Not started | queued, pending, ready |
| `ActiveActionStatus` | In progress | in-progress, current, active |
| `CompletedActionStatus` | Finished successfully | completed, success |
| `FailedActionStatus` | Did not succeed | failed, blocked |

### Common Schema.org Types

| Type | Use For | Example |
|------|---------|---------|
| `Action` | Generic operations | State changes, completions |
| `CreateAction` | Work producing artifacts | Outcomes, implementations |
| `UpdateAction` | Modifications | Edits, maturity updates |
| `DeleteAction` | Removals | Cleanup operations |
| `ItemList` | Collections | Arrays of typed items |
| `HowToStep` | Procedural items | Tasks, steps |
| `Project` | Project containers | Workspace projects |
| `Intangible` | Abstract concepts | Capabilities |

## Lucid Extensions

Use `x-` prefix for domain-specific properties:

| Extension | Purpose | Example |
|-----------|---------|---------|
| `x-maturity` | Capability maturity % | `x-maturity: 47` |
| `x-target` | Target maturity % | `x-target: 80` |
| `x-tokens` | Token count | `x-tokens: 48500` |
| `x-contribution` | Maturity contribution % | `x-contribution: 15` |
| `x-domain` | Capability domain | `x-domain: Data Security` |
| `x-stored` | External storage path | `x-stored: shared/payloads/research.md` |

## Patterns

### Action Result

```toon
@type: Action
@id: complete/005-authentication
name: outcome-completion
actionStatus: CompletedActionStatus
result: Moved to 4-completed

x-capabilityId: authentication-system
x-contribution: 25
x-previousMaturity: 47
x-newMaturity: 72
```

### Outcome Status

```toon
@type: CreateAction
@id: outcome/005-authentication
name: authentication-provider
actionStatus: ActiveActionStatus
description: Implement JWT authentication with session management

x-tokens: 85000
x-contribution: 25

step[3]{name,actionStatus,x-tokens}:
01-A-jwt.md,CompletedActionStatus,48500
01-B-session.md,ActiveActionStatus,36500
02-tests.md,PotentialActionStatus,40000
```

### Capability List

```toon
@type: ItemList
name: capabilities
numberOfItems: 4

itemListElement[4]{name,x-domain,x-maturity,x-target,actionStatus}:
authentication-system,Data Security,47,80,ActiveActionStatus
tenant-isolation,Data Security,35,90,ActiveActionStatus
admin-portal,Product Lifecycle,100,80,CompletedActionStatus
data-export,Integration,0,70,PotentialActionStatus
```

### Task List (HowToStep)

```toon
step[4]{@type,name,position,actionStatus,x-tokens}:
HowToStep,01-A-implement-jwt.md,1,CompletedActionStatus,48500
HowToStep,01-B-implement-session.md,2,ActiveActionStatus,36500
HowToStep,02-A-unit-tests.md,3,PotentialActionStatus,35000
HowToStep,02-B-integration-tests.md,4,PotentialActionStatus,40000
```

### Validation Results

```toon
@type: Action
name: workspace-validation
actionStatus: FailedActionStatus

results[3]{file,actionStatus,error}:
workspaces.json,CompletedActionStatus,-
project_map.json,CompletedActionStatus,-
capability_track.json,FailedActionStatus,missing field 'purpose'

x-passed: 2
x-failed: 1
```

### Subagent Summary

```toon
@type: Action
actionStatus: CompletedActionStatus
name: research-findings
result: Found 3 relevant legislation sources

findings[3]{name,relevance}:
Strata Schemes Management Act 2015,high
Strata Schemes Management Regulation 2016,medium
NCAT Case Law 2023,medium

x-tokens: 12500
x-stored: shared/payloads/legislation-research.md
```

## Token Efficiency

### Comparison: JSON vs TOON

**JSON (180 tokens):**
```json
{"outcome":{"id":5,"name":"authentication-provider","state":"in-progress","description":"Implement JWT"},"tasks":[{"fileName":"01-A-jwt.md","state":"success","tokens":50000},{"fileName":"01-B-session.md","state":"current","tokens":40000}]}
```

**TOON + Schema.org (65 tokens):**
```toon
@type: CreateAction
@id: outcome/005-authentication-provider
name: authentication-provider
actionStatus: ActiveActionStatus

step[2]{name,actionStatus,x-tokens}:
01-A-jwt.md,CompletedActionStatus,50000
01-B-session.md,ActiveActionStatus,40000
```

**Savings: 64%**

### When TOON Excels

- Arrays of uniform objects (tabular format)
- Status summaries with multiple items
- Subagent returns to main context
- Lists of outcomes, capabilities, tasks

### When TOON Adds Overhead

- Deeply nested objects (>3 levels)
- Arrays of arrays
- Single primitive values
- Human-facing final output (use markdown instead)

## Best Practices

1. **Use `@type` first** - LLMs recognize this as schema.org marker
2. **Prefer tabular arrays** - Maximum token savings
3. **Use tab delimiter** for large tables - Even more efficient
4. **Use `x-` prefix** for custom properties - Clear extension convention
5. **Map to ActionStatusType** - Consistent status vocabulary
6. **Include `@id`** when items need to be referenced

## References

- TOON Format: https://toonformat.dev/
- Schema.org: https://schema.org/
- ActionStatusType: https://schema.org/ActionStatusType
