# TOON Specialist Subagent Design

## Overview

A dedicated subagent that consolidates all schema.org/TOON knowledge, handling production, validation, and parsing of TOON files. Returns results in TOON format since Claude natively understands schema.org vocabulary.

## Problem Statement

Current issues with TOON file generation:
1. **Format knowledge scattered** - Every command embeds TOON rules in prompts
2. **Inconsistent output** - Haiku models interpret instructions differently
3. **Schema drift** - No single source of truth for format rules
4. **Validation gaps** - No consistent validation before write
5. **Wasted tokens** - Repeated format specifications in every prompt

## Design Principles

1. **Single Source of Truth** - One agent owns TOON format knowledge
2. **Schema-Aware** - Deep knowledge of all workspace schemas
3. **Self-Validating** - Validates output before returning
4. **Native Format** - Returns TOON, not JSON (Claude understands schema.org)
5. **Composable** - Works with Explore agents via coordinator pattern

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         TOON Specialist                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │    PARSE     │  │   PRODUCE    │  │   VALIDATE   │               │
│  │              │  │              │  │              │               │
│  │ TOON → Dict  │  │ Dict → TOON  │  │ Check syntax │               │
│  │ JSON → TOON  │  │ Schema-aware │  │ Check schema │               │
│  │ Detect fmt   │  │ Template-use │  │ Check types  │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                     SCHEMA REGISTRY                           │   │
│  │                                                               │   │
│  │  workspace-info-schema.toon     capabilities-info-schema.toon│   │
│  │  outcomes-info-schema.toon      execution-info-schema.toon   │   │
│  │  core-values-schema.toon        actor-registry-schema.toon   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Subagent Definition

**File:** `plugins/ws/agents/toon-specialist.md`

```yaml
---
name: toon-specialist
description: >
  Schema.org/TOON format specialist. Produces, validates, and parses TOON files
  using schema.org vocabulary. Use for any TOON file operations to ensure format
  consistency. Returns results in TOON format.
tools: [Read, Write, Edit, Glob, Bash]
model: sonnet
---
```

## Capabilities

### 1. PRODUCE - Generate TOON Files

**Input:**
```toon
@type: CreateAction
name: produce
object.schema: capabilities-info-schema.toon
object.output: .claude/capabilities-info.toon
object.data@type: ItemList
object.data.capabilities[3]{id,name,maturity|tab}:
auth	Authentication	45
data	Data Pipeline	20
user	User Management	65
```

**Output:**
```toon
@type: CreateAction
actionStatus: CompletedActionStatus
result.path: .claude/capabilities-info.toon
result.lines: 87
result.valid: true
```

### 2. VALIDATE - Check TOON Files

**Input:**
```toon
@type: AssessAction
name: validate
object.path: .claude/workspace-info.toon
object.schema: workspace-info-schema.toon
```

**Output:**
```toon
@type: AssessAction
actionStatus: CompletedActionStatus
result.valid: true
result.errors[0]:
result.warnings[1]{line,message|tab}:
54	Custom property "customField" should use x- prefix
```

### 3. PARSE - Read TOON to Structured Data

**Input:**
```toon
@type: AnalyzeAction
name: parse
object.path: .claude/capabilities-info.toon
object.extract[3]: summary.totalCapabilities,summary.averageMaturity,capability.index
```

**Output:**
```toon
@type: AnalyzeAction
actionStatus: CompletedActionStatus
result.summary.totalCapabilities: 31
result.summary.averageMaturity: 42%
result.capability.index[31]{identifier,name,maturity|tab}:
auth-system	Authentication	45%
data-pipeline	Data Pipeline	20%
...
```

### 4. CONVERT - Transform Between Formats

**Input:**
```toon
@type: UpdateAction
name: convert
object.source: data.json
object.target: data.toon
object.schema: capabilities-info-schema.toon
```

**Output:**
```toon
@type: UpdateAction
actionStatus: CompletedActionStatus
result.path: data.toon
result.format: toon
result.lines: 45
```

## TOON Format Specification (Embedded Knowledge)

The specialist has deep knowledge of TOON syntax:

### Syntax Rules

| Element | Syntax | Example |
|---------|--------|---------|
| Context | `@context: https://schema.org` | Required header |
| Type | `@type: TypeName` | `@type: ItemList` |
| ID | `@id: identifier` | `@id: workspace/my-project` |
| Property | `key: value` | `name: My Project` |
| Nested | `parent.child: value` | `workspace.name: lucid` |
| Typed nested | `parent@type: Type` | `workspace@type: Project` |
| Null | `key: null` | `optional: null` |
| Boolean | `key: true` or `key: false` | `enabled: true` |
| Array header | `key{col1,col2\|tab}:` | `items{id,name\|tab}:` |
| Array row | `val1\tval2` | `001\tWidget` |
| Inline array | `key[N]: a,b,c` | `tags[3]: red,green,blue` |
| Comment | `# text` | `# This is a comment` |

### Anti-Patterns (Reject These)

| Wrong | Correct | Why |
|-------|---------|-----|
| `key = value` | `key: value` | Use `:` not `=` |
| `{ nested { } }` | `parent.child:` | Use dot notation |
| `[ item1, item2 ]` | `key{col\|tab}:` | Use tabular format |
| `key:value` | `key: value` | Space after colon |
| Indentation nesting | Flat with prefixes | TOON is line-oriented |

### Schema.org Vocabulary

The specialist knows common schema.org types:

**Action Types:**
- `Action`, `CreateAction`, `UpdateAction`, `DeleteAction`
- `AnalyzeAction`, `AssessAction`, `ChooseAction`
- `ActionStatusType`: `PotentialActionStatus`, `ActiveActionStatus`, `CompletedActionStatus`, `FailedActionStatus`

**Container Types:**
- `ItemList` (with `numberOfItems`, tabular arrays)
- `PropertyValue` (for summary statistics)
- `DefinedTerm` (for capabilities, outcomes)

**Project Types:**
- `Project`, `SoftwareSourceCode`, `SoftwareApplication`
- `WebApplication`, `MobileApplication`, `APIReference`

### Schema Registry

The specialist knows all workspace schemas:

| Schema | Purpose | Instance Location |
|--------|---------|-------------------|
| `workspace-info-schema.toon` | Workspace environment | `.claude/workspace-info.toon` |
| `capabilities-info-schema.toon` | Capabilities index | `.claude/capabilities-info.toon` |
| `outcomes-info-schema.toon` | Outcomes tracking | `.claude/outcomes-info.toon` |
| `execution-info-schema.toon` | Execution logs | `.claude/execution-info.toon` |
| `core-values-schema.toon` | Reference data | (no instance) |
| `actor-registry-schema.toon` | Reference data | (no instance) |

**Schema Location:** `plugins/ws/templates/data/`

## Integration Pattern

### Coordinator Pattern with Explore Agents

```
Main Context (enviro.md)
    │
    ├─► Task(Explore) → "Scan capabilities/"
    │       Returns: JSON/structured data
    │
    ├─► Task(Explore) → "Scan outcomes/"
    │       Returns: JSON/structured data
    │
    └─► Task(toon-specialist) → "Produce files from data"
            │
            ├── Reads schemas from registry
            ├── Validates input data
            ├── Generates valid TOON
            ├── Writes to .claude/
            └── Returns: TOON status report
```

### Direct Usage

```
Task(subagent_type="toon-specialist", prompt="""
@type: CreateAction
name: produce
object.schema: capabilities-info-schema.toon
object.output: .claude/capabilities-info.toon
object.data: {structured data from previous scan}
""")
```

## Validation Rules

### Syntax Validation
- Required `@context: https://schema.org` header
- Valid `@type` declarations
- Proper key-value syntax (`:` separator, space after)
- Tab-delimited arrays match column count
- No forbidden patterns (`=`, `{}` nesting, `[]` arrays)

### Schema Validation
- Required fields present (marked `→const`)
- Optional fields correctly null-able (`TYPE?`)
- Enums match allowed values
- Array row counts match `numberOfItems`
- All 5 outcome stages present (workspace-info)

### Type Validation
- `→int` fields are integers
- `→datetime` fields are ISO-8601
- `→path` fields are valid relative paths
- `→url` fields are valid URLs
- `→percent` fields include `%` suffix

## Response Format

All responses from the specialist are in TOON:

```toon
@type: {ActionType}
actionStatus: {CompletedActionStatus|FailedActionStatus}
name: {operation-name}

# Success result
result.path: {output-path}
result.valid: true
result.lines: {line-count}

# Or failure result
error.message: {what-went-wrong}
error.line: {line-number-if-applicable}
error.expected: {what-was-expected}
error.found: {what-was-found}
```

## Error Handling

| Error Type | Response |
|------------|----------|
| Schema not found | `error.message: Schema not found: {path}` |
| Invalid syntax | `error.message: Syntax error at line {n}: {detail}` |
| Missing required | `error.message: Missing required field: {field}` |
| Type mismatch | `error.message: Type error: {field} expected {type}` |
| Write failed | `error.message: Write failed: {reason}` |

## Implementation Checklist

### Phase 1: Core Subagent
- [ ] Create `plugins/ws/agents/toon-specialist.md`
- [ ] Embed TOON specification in prompt
- [ ] Embed schema registry knowledge
- [ ] Implement PRODUCE operation
- [ ] Implement VALIDATE operation

### Phase 2: Integration
- [ ] Update `enviro.md` to use coordinator pattern
- [ ] Update other commands to delegate TOON writing
- [ ] Add PARSE operation for reading TOON files
- [ ] Add CONVERT operation for format transformation

### Phase 3: Validation Hook
- [ ] Create post-write hook using `toon_parser.py`
- [ ] Validate all `.toon` files on write
- [ ] Report validation errors in TOON format

### Phase 4: Documentation
- [ ] Document TOON format in plugin README
- [ ] Add examples for each operation
- [ ] Create troubleshooting guide for format errors

## File Structure

```
plugins/ws/
├── agents/
│   └── toon-specialist.md      # NEW: Subagent definition
├── templates/
│   └── data/
│       ├── workspace-info-schema.toon
│       ├── capabilities-info-schema.toon
│       ├── outcomes-info-schema.toon
│       ├── execution-info-schema.toon
│       ├── core-values-schema.toon
│       └── actor-registry-schema.toon
├── commands/
│   └── enviro.md               # MODIFY: Use coordinator pattern
└── hooks/
    └── validate_toon.py        # NEW: Post-write validation

shared/cli-commons/
└── src/lucid_cli_commons/
    └── toon_parser.py          # EXISTING: Python parser
```

## Success Criteria

1. **Consistency**: All generated TOON files pass validation
2. **No Format Drift**: Single source of truth prevents variations
3. **Reduced Prompts**: Commands don't need embedded format specs
4. **Native Output**: Results in TOON, not JSON
5. **Schema Awareness**: Specialist reads and applies schemas correctly
6. **Error Recovery**: Clear error messages enable quick fixes

## Open Questions

1. **Model Choice**: Sonnet for reliability, or Haiku for speed?
   - Recommendation: Sonnet - format precision is critical

2. **Schema Embedding**: Embed schemas in prompt, or read dynamically?
   - Recommendation: Read dynamically - schemas may evolve

3. **Validation Strictness**: Warn vs error on custom properties?
   - Recommendation: Warn with `x-` prefix suggestion

4. **Python Integration**: Use `toon_parser.py` in hooks?
   - Recommendation: Yes - provides programmatic validation
