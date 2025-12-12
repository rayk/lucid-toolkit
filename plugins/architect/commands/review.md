---
description: Review architecture against LCA principles. Analyzes code and documentation for compliance with composition, containment, immutability, and data strategy tenets.
argument-hint: [scope: full|documentation|code]
allowed-tools:
  - Read
  - Grep
  - Glob
  - Task
  - Skill
---

<objective>
Review the current project's architecture against Lucid Composite Architecture (LCA) principles. Identifies violations, recommendations, and positive patterns across five dimensions: Composition, Containment, Immutability, Simplicity, and Data Strategy.
</objective>

<phase_1_scope>
**Determine review scope:**

Parse `$ARGUMENTS` for scope:
- `full` (default): Review documentation, code, AND hierarchy consistency
- `documentation`: Focus on ARCHITECTURE.md and ADRs
- `code`: Focus on codebase structure and patterns
- `consistency`: Focus on hierarchy conflicts and LCA compliance

If no argument provided, default to `full` review.
</phase_1_scope>

<phase_1b_discover_hierarchy>
**Discover architecture file hierarchy:**

Search for all architecture documents:
```
Glob: **/ARCHITECTURE.md
Glob: **/architecture.md
Glob: **/arc-dec.md
```

Build hierarchy tree based on directory depth:
```
LCA Core Principles (this plugin - immutable)
    ↓
Platform: architecture/ARCHITECTURE.md (if exists)
    ↓
Repository: ./ARCHITECTURE.md
    ↓
Service: services/*/architecture.md
    ↓
Component: services/*/components/*/architecture.md
```

**Inheritance Rule**: Lower levels inherit from above. They may EXTEND or ELABORATE but NEVER OVERRIDE or RELAX constraints from higher levels.
</phase_1b_discover_hierarchy>

<phase_2_documentation>
**Review architecture documentation:**

If scope includes documentation:

1. Find architecture documents:
   ```
   Glob: **/ARCHITECTURE.md
   Glob: **/architecture.md
   Glob: **/arc-dec.md
   ```

2. Check documentation structure:
   - Hierarchy level declared
   - Navigation headers present (↑ ← ↓)
   - Maturity status accurate
   - Required sections present
   - Quality markers tracked

3. Review ADRs:
   ```
   Glob: **/adr/adr-*.md
   ```
   - Check numbering sequence (no gaps)
   - Verify status field current
   - Check for superseded without successor
   - Verify negative consequences present

4. Compile documentation findings
</phase_2_documentation>

<phase_3_code>
**Review codebase:**

If scope includes code:

Use Task tool with architecture-reviewer agent:

```
Review this codebase against LCA principles:

1. Composition over Inheritance
   - Check for behavior inheritance anti-patterns
   - Verify composition patterns

2. Radical Containment
   - Check failure isolation
   - Verify scope boundaries

3. Functional Immutability
   - Check for mutable state
   - Verify pure function patterns
   - Check for immutability libraries

4. Simplicity Default
   - Check for premature optimization
   - Verify complexity is encapsulated

5. Data Strategy
   - Check boundary types
   - Verify internal model design

Technology stack: {detected from project}
Focus areas: {based on project type}
```

Capture analysis results.
</phase_3_code>

<phase_4_component_mapping>
**Map component structure:**

Use Task tool with component-analyzer agent:

```
Analyze current project structure:
- Identify Atoms, Composites, Conduits, Deployable Units
- Flag any components that don't fit LCA taxonomy
- Note boundary violations
```

Compare against documented architecture (if exists).
</phase_4_component_mapping>

<phase_4b_consistency>
**Check hierarchy consistency:**

Use Task tool with consistency-checker agent:

```
Check architecture hierarchy for conflicts:

1. Build hierarchy tree from discovered files
2. For each constraint in higher level:
   - Check if lower levels contradict
   - Check if lower levels relax/weaken
   - Check if required elements are missing

3. Check all files against LCA immutable principles:
   - Composition over Inheritance
   - Radical Containment
   - Functional Immutability
   - Protocol Buffers for Conduits
   - Schema.org at Boundaries
   - Single Subject Types Internally
   - Versioned Conduits
   - Uni-directional Dependencies

4. Classify findings:
   - OVERRIDE: Lower contradicts higher (VIOLATION)
   - RELAXATION: Lower weakens constraint (VIOLATION)
   - LCA_VIOLATION: Contradicts core principle (CRITICAL)
   - EXTENSION: Adds detail (ALLOWED)
   - ELABORATION: Explains how (ALLOWED)
```

Capture consistency findings.
</phase_4b_consistency>

<phase_5_report>
**Generate review report:**

Compile findings into structured report:

```markdown
# Architecture Review Report

**Date**: {today}
**Scope**: {full|documentation|code}
**Project**: {project name}

## Executive Summary

**Overall Score**: {0-100}/100

| Principle | Score | Status |
|-----------|-------|--------|
| Composition | {score} | {pass/warn/fail} |
| Containment | {score} | {pass/warn/fail} |
| Immutability | {score} | {pass/warn/fail} |
| Simplicity | {score} | {pass/warn/fail} |
| Data Strategy | {score} | {pass/warn/fail} |

## Documentation Review

**Maturity Status**: {claimed} → {actual assessment}
**Completeness**: {score}%

{Findings list}

## Code Review

### Violations (Must Fix)

{Prioritized violation list with file:line references}

### Recommendations (Should Consider)

{Improvement suggestions}

### Positive Patterns

{Good practices found - balance the criticism}

## Component Analysis

| Type | Count | Status |
|------|-------|--------|
| Atoms | {N} | {documented/undocumented} |
| Composites | {N} | {documented/undocumented} |
| Conduits | {N} | {documented/undocumented} |
| Deployable Units | {N} | {documented/undocumented} |

{Discrepancies between docs and code}

## Hierarchy Consistency

**Architecture Files Found**:
```
LCA Core Principles (immutable)
    ↓
{list of architecture files in hierarchy order}
```

**LCA Principle Compliance**:

| Principle | Status | Evidence |
|-----------|--------|----------|
| Composition over Inheritance | {pass/fail} | {file:line if violation} |
| Radical Containment | {pass/fail} | {evidence} |
| Functional Immutability | {pass/fail} | {evidence} |
| Versioned Conduits | {pass/fail} | {evidence} |
| Schema.org at Boundaries | {pass/fail} | {evidence} |

**Hierarchy Conflicts**:

| Type | Higher Level | Lower Level | Issue |
|------|--------------|-------------|-------|
| {override/relaxation} | {file:line} | {file:line} | {description} |

**Valid Extensions**: {count} (lower levels properly extending higher)

## Action Items

Priority order:
1. {Critical violation}
2. {High-priority fix}
3. {Medium-priority improvement}
...

## Next Steps

Recommended actions based on findings:
- {Specific actionable recommendation}
- {Specific actionable recommendation}
```
</phase_5_report>

<phase_6_output>
**Present results:**

Display the review report in chat.

Offer follow-up actions:

"Review complete. What would you like to do?"

Options:
1. **Fix violations** - Start addressing identified issues
2. **Update documentation** - Bring docs in sync with code
3. **Create ADR** - Document decision to address findings
4. **Export report** - Save report to file
5. **Done** - Review later
</phase_6_output>

<success_criteria>
- All five LCA principles assessed
- Documentation and code reviewed (per scope)
- Violations have specific file:line references
- Scores reflect actual findings
- Positive patterns acknowledged
- Actionable next steps provided
</success_criteria>
