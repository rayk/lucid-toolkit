---
name: toon-schema
description: MANDATORY token-efficient output format. ALWAYS use TOON with schema.org types when returning structured data (lists, status, results, summaries). Triggers on ANY structured output to minimize context consumption. Provides 40-60% token savings vs JSON.
---

<objective>
TOON (Token-Oriented Object Notation) with schema.org types provides 40-60% token savings for structured data.

**This is not optional.** All structured output (lists, status reports, search results, summaries) MUST use TOON format.

**Key insight:** Claude already knows TOON syntax and schema.org types from training data. This skill provides conventions for consistent usage across lucid-toolkit.

**Full reference:** See `references/toon-schema-org.md` for complete patterns and examples.
</objective>

<quick_start>
**Basic TOON syntax:**

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
```

**Always declare `@type`** for semantic meaning:
```toon
@type: ItemList
name: results
itemListElement[3]{name,status}:
  item-a,active
  item-b,pending
  item-c,completed
```
</quick_start>

<schema_org_types>
Use `@type` to declare semantic type. LLMs recognize these without explanation.

| Type | Use For |
|------|---------|
| `Action` | Operations, state changes, completions |
| `CreateAction` | Work producing new artifacts (outcomes) |
| `ItemList` | Arrays of typed items |
| `HowToStep` | Tasks, steps, procedures |
| `Project` | Project containers |
| `Intangible` | Capabilities, abstract concepts |

<status_values>
ActionStatusType values:

| Status | Meaning |
|--------|---------|
| `PotentialActionStatus` | Not started, queued |
| `ActiveActionStatus` | In progress |
| `CompletedActionStatus` | Finished successfully |
| `FailedActionStatus` | Did not succeed |
</status_values>
</schema_org_types>

<lucid_extensions>
Extensions with `x-` prefix for domain-specific properties:

| Extension | Purpose |
|-----------|---------|
| `x-maturity` | Capability maturity % |
| `x-tokens` | Token count |
| `x-contribution` | Maturity contribution % |
| `x-domain` | Capability domain |
</lucid_extensions>

<examples>
<example_outcome_status>
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
</example_outcome_status>

<example_capability_list>
```toon
@type: ItemList
name: capabilities

itemListElement[3]{name,x-maturity,x-target,actionStatus}:
authentication-system,47,80,ActiveActionStatus
tenant-isolation,35,90,ActiveActionStatus
admin-portal,100,80,CompletedActionStatus
```
</example_capability_list>

<example_action_result>
```toon
@type: Action
name: outcome-completion
actionStatus: CompletedActionStatus
result: Moved to 4-completed
x-capabilityId: authentication-system
x-contribution: 25
x-newMaturity: 72
```
</example_action_result>
</examples>

<when_to_use>
<apply_when>
- **Subagent returns** - Compact summaries back to main context
- **Status displays** - Lists of outcomes, capabilities, tasks
- **Action results** - Completion summaries, state transitions
- **Validation reports** - Structured error/success lists
- **Search results** - File matches, grep output, findings
</apply_when>

<do_not_apply>
- Human-facing final output (use markdown)
- Small single-value responses
- Narrative explanations
</do_not_apply>
</when_to_use>

<success_criteria>
**TOON output is correct when:**

- Uses schema.org `@type` declaration at top
- Follows TOON syntax (proper quoting, comma delimiters)
- Tabular arrays use header declarations `{field,field}`
- ActionStatusType values correctly mapped
- Token count reduced by 40-60% vs equivalent JSON
- Structure is parseable and semantically clear

**Anti-success indicators (format failure):**

- JSON used instead of TOON for uniform data
- Missing `@type` declaration
- Tabular array without header declaration
- Wrong ActionStatusType value
- Verbose structure that could be more compact
</success_criteria>
