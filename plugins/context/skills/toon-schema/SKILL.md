---
name: toon-schema
description: Token-efficient output using TOON format with schema.org vocabulary. Use when returning structured data to minimize context consumption.
---

<overview>
TOON (Token-Oriented Object Notation) with schema.org types provides 40-60% token savings for structured data.

**When to use:** Returning structured data (lists, status, results) where token efficiency matters.

**Key insight:** Claude already knows TOON syntax and schema.org types from training data. This skill provides conventions for consistent usage across lucid-toolkit.

**Full reference:** See `references/toon-schema-org.md` for complete patterns and examples.
</overview>

<toon_basics>
## TOON Syntax

```toon
# Objects - key: value with indentation
name: Ada
user:
  id: 123
  active: true

# Primitive arrays - inline
tags[3]: admin,ops,dev

# Tabular arrays - header declares fields
items[2]{name,status,count}:
  widget-a,active,5
  widget-b,pending,3

# Tab delimiter for efficiency
items[2]{name,status|tab}:
  widget-a	active
  widget-b	pending
```
</toon_basics>

<schema_org_types>
## Schema.org Types

Use `@type` to declare semantic type. LLMs recognize these without explanation.

| Type | Use For |
|------|---------|
| `Action` | Operations, state changes, completions |
| `CreateAction` | Work producing new artifacts (outcomes) |
| `ItemList` | Arrays of typed items |
| `HowToStep` | Tasks, steps, procedures |
| `Project` | Project containers |
| `Intangible` | Capabilities, abstract concepts |

## Status Values (ActionStatusType)

| Status | Meaning |
|--------|---------|
| `PotentialActionStatus` | Not started, queued |
| `ActiveActionStatus` | In progress |
| `CompletedActionStatus` | Finished successfully |
| `FailedActionStatus` | Did not succeed |
</schema_org_types>

<lucid_extensions>
## Lucid Extensions (x- prefix)

| Extension | Purpose |
|-----------|---------|
| `x-maturity` | Capability maturity % |
| `x-tokens` | Token count |
| `x-contribution` | Maturity contribution % |
| `x-domain` | Capability domain |
</lucid_extensions>

<examples>
## Example: Outcome Status

```toon
@type: CreateAction
@id: outcome/005-authentication
name: authentication-provider
actionStatus: ActiveActionStatus
x-tokens: 85000

step[3]{name,actionStatus}:
01-A-jwt.md,CompletedActionStatus
01-B-session.md,ActiveActionStatus
02-tests.md,PotentialActionStatus
```

## Example: Capability List

```toon
@type: ItemList
name: capabilities

itemListElement[3]{name,x-maturity,x-target,actionStatus}:
authentication-system,47,80,ActiveActionStatus
tenant-isolation,35,90,ActiveActionStatus
admin-portal,100,80,CompletedActionStatus
```

## Example: Action Result

```toon
@type: Action
name: outcome-completion
actionStatus: CompletedActionStatus
result: Moved to 4-completed
x-capabilityId: authentication-system
x-contribution: 25
x-newMaturity: 72
```
</examples>

<usage>
## When to Apply

1. **Subagent returns** - Compact summaries back to main context
2. **Status displays** - Lists of outcomes, capabilities, tasks
3. **Action results** - Completion summaries, state transitions
4. **Validation reports** - Structured error/success lists

## When NOT to Apply

- Human-facing final output (use markdown)
- Small single-value responses
- Narrative explanations
</usage>
