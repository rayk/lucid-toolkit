---
name: SKILL-NAME-HERE
description: Analysis or review skill that only reads and reports, never modifies files. Use when user asks to [trigger terms]. Perfect for audits, reviews, and analysis tasks.
allowed-tools:
  - Read
  - Grep
  - Glob
---

# SKILL NAME (Read-Only)

This skill analyzes/reviews [subject] without making any modifications.

## Purpose

Provide comprehensive analysis of [target] by examining existing code/files/documentation.

## When to Use

- User asks to review [subject]
- User wants analysis of [subject]
- User needs audit of [subject]

## Instructions

### 1. Discover Files

Use Glob and Grep to find relevant files:
- Pattern 1: `**/*.ext`
- Pattern 2: `grep "pattern"`

### 2. Read and Analyze

For each relevant file:
1. Use Read tool to examine contents
2. Check for [criteria 1]
3. Verify [criteria 2]
4. Note any issues or patterns

### 3. Generate Report

Compile findings into structured report:

```
## Analysis Report

### Summary
[High-level overview]

### Findings
1. [Finding 1]
   - Location: file:line
   - Severity: High/Medium/Low
   - Description: [details]

2. [Finding 2]
   - Location: file:line
   - Severity: High/Medium/Low
   - Description: [details]

### Recommendations
- [Recommendation 1]
- [Recommendation 2]

### Metrics
- Total files analyzed: X
- Issues found: Y
- Quality score: Z/10
```

## Reference Checklist

Use this checklist when analyzing:

- [ ] Check item 1
- [ ] Check item 2
- [ ] Check item 3
- [ ] Verify item 4
- [ ] Validate item 5

## Security Note

This skill is read-only by design:
- ✅ Can Read, Grep, Glob
- ❌ Cannot Write, Edit, Bash
- ❌ Makes zero modifications
- ✅ Safe for sensitive codebases
