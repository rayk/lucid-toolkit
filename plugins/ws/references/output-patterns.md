# Output Patterns Reference

Standard patterns for rendering structured data to terminal in the ws plugin. All commands and skills should follow these patterns for consistent CLI output.

## Quick Reference
### TOON Output
Render TOON data directly as a code block:

```toon
@type: ItemList
@id: outcome-list-result
numberOfItems: 11

summary.total: 11
summary.queued: 3
summary.completed: 5

outcome{id,name,stage|tab}:
005-auth	Implement Auth	in-progress
006-mgmt	User Management	ready
```

Always use `toon` language tag for syntax highlighting.


### Status Output
For action results, use this compact format:

```
[action] [target] [result]

feat(ws): add out/list command
0.9.2 → 0.9.3 (minor)
✓ Committed, pushed, synced
```

Symbols: `✓` success, `✗` failure, `⚠` warning, `→` transition


### Table Output
For tabular data, use markdown tables:

```markdown
| ID          | Name           | Stage       | Priority |
|-------------|----------------|-------------|----------|
| 005-auth    | Implement Auth | in-progress | P1       |
| 006-mgmt    | User Management| ready       | P2       |
```

Keep columns minimal. Truncate long values with `...`



## Output Patterns
### Pattern Selection
Choose pattern based on data type:

| Data Type | Pattern | When to Use |
|-----------|---------|-------------|
| Structured data | TOON block | Returning data to subagents, machine-readable |
| Lookup results | Markdown table | Human-readable comparisons, listings |
| Action result | Status line | Single operation outcome |
| Multiple actions | Status list | Batch operation results |
| Validation | Box report | Multi-check validation with pass/fail |
| Summary | Compact stats | Counts, distributions, aggregates |


### TOON Pattern
**When**: Returning data to subagents, serializing structured results

```toon
@type: [SchemaType]
@id: [unique-identifier]
[scalar properties]

[table]{columns|tab}:
[row1 tab-separated]
[row2 tab-separated]
```

Rules:
- Always include `@type` and `@id`
- Use tab-separated tables for arrays
- Prefer flat structure (avoid nesting >2 levels)
- No prose - data only


### Table Pattern
**When**: Human-readable listings, comparisons

```markdown
| Column1 | Column2 | Column3 |
|---------|---------|---------|
| value1  | value2  | value3  |
```

Rules:
- Max 6 columns (truncate or split if more)
- Align columns consistently
- Truncate cells >30 chars with `...`
- Right-align numbers


### Status Pattern
**When**: Single action outcome

```
✓ [action verb] [target]: [brief result]
```

Examples:
```
✓ Created outcome 005-auth in queued/
✓ Synced capabilities-info.toon (12 capabilities)
✗ Validation failed: 3 critical issues
⚠ Index stale, auto-syncing...
```


### Box Pattern
**When**: Validation reports, multi-section results

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Title]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Section1:     [✓/✗] [details]
Section2:     [✓/✗] [details]
Section3:     [✓/✗] [details]

Overall: [PASS ✓ / FAIL ✗]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Use box drawing: `━` (horizontal), `│` (vertical), `┌┐└┘` (corners)


### Summary Pattern
**When**: Counts, distributions, quick stats

```
Summary: 11 total | 3 queued | 2 ready | 1 in-progress | 5 completed
         9 parent | 2 child | P1: 6 | P2: 4 | P3: 1
```

Rules:
- Single line for simple counts
- Two lines max for distributions
- Use `|` separator
- Align related groups


### Distribution Pattern
**When**: Visual distribution of values

```
Maturity Distribution:
  0-29%:   ### (3)
  30-59%:  ##### (5)
  60-79%:  ### (3)
  80-100%: # (1)
```

Rules:
- Use `#` for bar chart
- Include count in parentheses
- Align labels and bars



## Adaptive Styling
### Simple Output
Use plain text for:
- Single status lines
- Short lists (<5 items)
- Simple counts

Example:
```
✓ Created 3 outcomes
  - 005-auth (queued)
  - 006-mgmt (queued)
  - 007-report (queued)
```


### Complex Output
Use box drawing for:
- Validation reports (>3 checks)
- Multi-section summaries
- Error reports with details

Example:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Validation Report: 005-auth
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Schema:         ✓ Valid YAML frontmatter
Achievement:    ✓ Behavioral focus
Effects:        ✓ 3 Given-When-Then
Capabilities:   ✓ Links valid
Actors:         ⚠ 1 unknown actor ID

Overall: NEEDS_ATTENTION ⚠
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```



## Symbols
Standard symbols for consistent output:

| Symbol | Meaning | Unicode |
|--------|---------|---------|
| ✓ | Success/pass | U+2713 |
| ✗ | Failure/fail | U+2717 |
| ⚠ | Warning/attention | U+26A0 |
| → | Transition/arrow | U+2192 |
| • | Bullet point | U+2022 |
| ━ | Horizontal line | U+2501 |
| │ | Vertical line | U+2502 |
| ┌ | Top-left corner | U+250C |
| ┐ | Top-right corner | U+2510 |
| └ | Bottom-left corner | U+2514 |
| ┘ | Bottom-right corner | U+2518 |


## Anti-Patterns
### Avoid
- **Excessive whitespace**: Don't add blank lines between every element
- **Nested boxes**: Don't put boxes inside boxes
- **Mixed styles**: Don't combine table + box in same output
- **Emoji overuse**: Stick to standard symbols (✓✗⚠), not emoji
- **Long prose**: Output should be data-focused, not explanatory
- **Missing language tags**: Always tag code blocks (`toon`, `markdown`, etc.)
- **Inconsistent alignment**: Align columns and values consistently


### Prefer
- Compact, scannable output
- Consistent symbol usage
- Clear visual hierarchy
- Machine-parseable where possible (TOON)
- Human-readable where needed (tables, reports)



## Examples
### Outcome List
```
Outcomes Overview (synced: 2025-12-02T10:30:00Z)

Summary: 11 total | 3 queued | 2 ready | 1 in-progress | 0 blocked | 5 completed

Current Focus: 005-implement-auth (in-progress)

| ID                 | Name              | Stage       | Priority | Capabilities    |
|--------------------|-------------------|-------------|----------|-----------------|
| 005-implement-auth | Implement Auth    | in-progress | P1       | auth-system:30% |
| 006-user-mgmt      | User Management   | ready       | P2       | user-mgmt:25%   |
| 007-reporting      | Reporting         | queued      | P3       | reporting:20%   |

Blocked: None
```


### Action Result
```
ws Plugin Published

4745a58 feat(ws): add out/list command
0.9.2 → 0.9.3 (minor)

✓ Committed, pushed, synced
```


### TOON Return
```toon
@type: AssessAction
actionStatus: CompletedActionStatus
@id: 005-auth

validationStatus: VALID
checksPerformed: 10
issues.critical: 0
issues.warning: 1

indexesSynced: true
```



## Success Criteria
Output meets quality standards when:

- Appropriate pattern selected for data type
- Consistent symbol usage throughout
- No excessive whitespace or blank lines
- Code blocks have language tags
- Tables stay under 6 columns
- Box reports used only for complex validation
- TOON used for machine-readable returns
- Human output is scannable in <5 seconds

