# Critical Review: Plugin Improvement Plan

**Date**: 2025-12-14
**Reviewer**: Usage Analysis + Claude Code Best Practices Cross-Check

---

## Executive Summary

After cross-referencing the improvement plan against:
1. **Current plugin prompts** (7 skills/agents analyzed)
2. **Claude Code official documentation** (skills, agents, memory)
3. **Raw pattern data** (16 patterns from 19 sessions)
4. **Usage analysis reports** (50 sessions, 1873 tool calls)

**Verdict**: The plan correctly identifies the problems but proposes solutions that **partially misunderstand how Claude Code trigger detection works**.

### Key Finding

> Claude Code invokes skills/agents based on the **description field** in YAML frontmatter.
> Separate "INVOKE WHEN..." sections **will not be read** during invocation decisions.
> The description must integrate BOTH "what it does" AND "when to use it" in one field.

---

## Issue-by-Issue Analysis

### Issue 1: Plugins Not Being Invoked

**Reported Evidence**:
- 244 plan file operations → 0 `/plan` invocations
- 8 ADR file operations → 0 `/architect adr` invocations
- 3-10 WebSearches → 0 `analyst:research` invocations

**Proposed Solution (from plan)**:
```yaml
---
name: skill-name
description: Brief description.

  INVOKE THIS SKILL when user:
  - [keyword 1]
  - [keyword 2]
---
```

**Critical Problem**: This structure puts INVOKE triggers **outside the description field**. Claude Code reads ONLY the `description:` value for invocation decisions.

**Correct Structure** (per official docs):
```yaml
---
name: skill-name
description: |
  Brief description of what it does. Use when user mentions
  [keyword 1], [keyword 2], or works with [pattern 3].
  MUST BE USED when [critical condition].
---
```

**Evidence from current prompts**:
- `manage-architecture` already has good structure: "architect review", "architecture review" in description
- `consider` skill lacks any trigger language in description
- `research` agent has no user-facing triggers - only MCP tool references

**Revised Recommendation**:
Rewrite descriptions to integrate triggers, not add separate sections.

---

### Issue 2: plugin.json "triggers" Feature

**Proposed Solution (from plan)**:
```json
{
  "triggers": {
    "file_patterns": ["**/adr-*.md"],
    "suggest": "/architect adr"
  }
}
```

**Critical Problem**: This feature **does not exist** in Claude Code. There is no `triggers` field in plugin.json schema.

**How Claude Code Actually Works**:
- Plugins define: commands, skills, agents, hooks
- There is no auto-detection based on file patterns in plugin.json
- The only mechanism for path-based behavior is **CLAUDE.md rules with `paths:` frontmatter**

**Correct Approach**:
Use CLAUDE.md rules in target projects:
```markdown
---
paths: architecture/decisions/**
---

When working with ADR files, use `/architect adr` for creation and validation.
```

Or create a **hook** that runs on file events (but this is complex and may be overkill).

---

### Issue 3: Delegation Rules in CLAUDE.md

**Proposed Solution (from plan)**:
```markdown
## Delegation Requirements

### Mandatory Delegation (MUST use Task)
- **25+ tool threshold**: If sequential tool count exceeds 25, delegate...
```

**Assessment**: This is **correct in principle** but has implementation issues.

**Problem**: Claude cannot count its own tool calls during a session. The instruction "if tool count exceeds 25" is not actionable because:
1. Claude doesn't track cumulative tool count
2. This would require a hook or external mechanism

**Correct Approach**:
Frame as recognizable patterns, not counts:
```markdown
## Delegation Requirements

### Recognize These Patterns → Delegate
- **Exploration requests**: "find where", "search for", "what files" → Task(Explore)
- **Multi-file changes**: "update across", "refactor all", "fix everywhere" → Task(general-purpose)
- **Long Edit cycles**: After 5+ sequential Edit operations, delegate remaining to subagent
```

---

### Issue 4: Context Compaction Prevention

**Reported Evidence**:
- 5 compactions at 155K-160K tokens
- Heavy Edit/Read cycles before compaction
- All in lucid-apps project

**Proposed Solution (from plan)**:
- Break Edit cycles at 10 operations
- Monitor sessions approaching 150K tokens

**Assessment**: Partially correct, but:
1. Claude cannot monitor its own token count
2. "10 operations" is arbitrary without mechanistic backing

**Better Approach**:
```markdown
## Context Protection Patterns

### High-Risk Activities (delegate early)
- Reading large files (>300 lines)
- Test output (use background execution)
- Multiple sequential edits to related files

### Delegation Checkpoints
After completing a coherent unit of work:
- "I've finished the exploration phase. Before implementing, let me delegate..."
- "I've made 5 related edits. Let me have a subagent continue..."
```

---

## Cross-Check: Will Solutions Address Identified Issues?

### Issue: 136 tool calls with no delegation (session ec369a72)

| Proposed Solution | Will It Work? | Why/Why Not |
|-------------------|---------------|-------------|
| INVOKE triggers in skills | Partial | Only if in description field |
| 25+ tool threshold rule | No | Claude can't count tools |
| Plugin.json triggers | No | Feature doesn't exist |
| Pattern recognition in CLAUDE.md | Yes | If patterns are recognizable |

### Issue: Manual ADR work (session 0cb101e2)

| Proposed Solution | Will It Work? | Why/Why Not |
|-------------------|---------------|-------------|
| /architect adr suggestion | Partial | Only if user sees suggestion |
| Path-based CLAUDE.md rules | Yes | Will activate on file read |
| Plugin.json file_patterns | No | Feature doesn't exist |

### Issue: 10 WebSearches without research agent

| Proposed Solution | Will It Work? | Why/Why Not |
|-------------------|---------------|-------------|
| "3+ WebSearches" trigger | No | Claude can't count searches retroactively |
| Enhanced research description | Yes | If keywords match user intent |
| CLAUDE.md pattern guidance | Yes | "For research tasks, use analyst:research" |

---

## Revised Improvement Structure

### What Actually Works in Claude Code

1. **Description field** - The ONLY mechanism for skill/agent discovery
2. **CLAUDE.md rules** - Path-conditional guidance via `paths:` frontmatter
3. **Hooks** - Pre/post tool execution, but complex to implement
4. **Explicit user invocation** - `/command` or "use [agent]"

### What Doesn't Work

1. **Separate INVOKE sections** - Not read during invocation
2. **plugin.json triggers** - Feature doesn't exist
3. **Tool counting** - Claude can't track cumulative counts
4. **Auto-detection hooks** - Would need custom implementation

---

## Recommended Revisions to Plan

### Priority 1: Fix Skill/Agent Descriptions

**Current approach** (incorrect):
```yaml
description: Brief description.

INVOKE THIS SKILL when user:
- keyword 1
```

**Correct approach**:
```yaml
description: |
  [What it does]. Use when user mentions [keyword 1],
  [keyword 2], or works with [pattern]. MUST BE USED
  for [critical scenarios].
```

**Specific changes needed**:

| File | Current Gap | Correct Description |
|------|-------------|---------------------|
| analyst/consider | No trigger language | "Mental model analysis. Use when user asks 'why', 'what if', 'how should we', or needs structured thinking about a problem." |
| analyst/research | MCP-tool only | "Systematic research orchestrator. Use when user needs to investigate a topic, gather information from multiple sources, or verify facts before action." |
| plan/execution-prompt-generator | Hidden in description | "TDD execution prompt generation. MUST BE USED when reading plan files in /plans/ directories or when user mentions 'execute plan', 'TDD', or 'implementation prompt'." |
| impl-flutter/dart-flutter-mcp | No user triggers | "Flutter/Dart development workflows. Use when working with .dart files, pubspec.yaml, or user mentions Flutter, widget, Riverpod, or Dart." |

### Priority 2: Replace plugin.json triggers with CLAUDE.md rules

**For target projects (lucid-apps, etc.), add to CLAUDE.md**:

```markdown
---
paths: architecture/decisions/**
---
# ADR Work
When creating or editing ADR files, use `/architect adr` for structured creation.

---
paths: **/plans/**
---
# Plan Work
When working with execution plans, use `/plan validate` after edits.
```

### Priority 3: Replace tool counting with pattern recognition

**Replace**:
```markdown
- **25+ tool threshold**: If sequential tool count exceeds 25...
```

**With**:
```markdown
## Delegation Patterns

### Recognize → Delegate
| User Request Pattern | Action |
|---------------------|--------|
| "find where X", "search for Y" | Task(Explore) |
| "update all", "fix across", "refactor" | Task(general-purpose) |
| "implement [feature]" | Task(impl-flutter:flutter-coder) |
| "review architecture" | Task(architect:architecture-reviewer) |

### After Completing Work Units
When you've finished a coherent phase (exploration, initial implementation, etc.),
consider delegating the next phase to preserve context.
```

---

## Validation: Mapping Solutions to Evidence

| Evidence (from data) | Root Cause | Correct Solution |
|---------------------|------------|------------------|
| 244 plan ops, 0 invocations | No triggers in plan skill description | Rewrite description with "plan", "TDD", "execute" keywords |
| 8 ADR ops, 0 invocations | No path-based guidance | Add CLAUDE.md rule for `architecture/decisions/**` |
| 136 tools, 0 delegation | No recognizable delegation patterns | Add pattern table to CLAUDE.md |
| 5 compactions | Long Edit cycles | Add "after coherent unit" checkpoint guidance |
| 10 WebSearches, no research | research agent description MCP-only | Rewrite with user-intent keywords |

---

## Conclusion

The improvement plan correctly identifies **what** is broken:
- Plugins not invoked despite relevant work
- Context exhaustion from lack of delegation
- Manual work in plugin domains

But the proposed **how** needs revision:
1. ❌ Separate INVOKE sections → ✅ Integrated descriptions
2. ❌ plugin.json triggers → ✅ CLAUDE.md path rules
3. ❌ Tool count thresholds → ✅ Pattern recognition tables
4. ❌ Token monitoring → ✅ Work unit checkpoints

**The structure is wrong; the intent is right.**

Implementing the corrections above will address the identified issues through mechanisms that Claude Code actually supports.
