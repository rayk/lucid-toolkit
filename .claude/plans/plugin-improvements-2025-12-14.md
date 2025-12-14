# Plugin Improvement Plan - 2025-12-14 (Evidence-Based Revision)

Based on analysis of 50+ sessions, 607 tool calls, 16 discovered patterns, and cross-checked against official Claude Code documentation.

**Last Verified**: 2025-12-14 | **Status**: Ready for Implementation

## Sources

- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) - Official Anthropic docs
- [Claude Code Subagents](https://code.claude.com/docs/en/sub-agents) - Official Claude Code docs
- [Claude Code Hooks Guide](https://code.claude.com/docs/en/hooks-guide) - Official hook documentation
- [Managing Claude Code Context](https://mcpcat.io/guides/managing-claude-code-context/) - Community best practices
- [CLAUDE.md Mastery](https://claudefa.st/blog/guide/mechanics/claude-md-mastery) - Configuration patterns

---

## Executive Summary

| Metric | Current | Target |
|--------|---------|--------|
| Delegation rate | 0-3% | >50% |
| Plugin invocations/session | 0.26 | >2 |
| Context at compaction | 95% (auto) | 70-75% (manual) |
| Compaction events | 5 in 2 days | <1/week |

---

## Evidence-Based Solutions

### Key Insight from Official Docs

> "The `description` field enables Skill discovery and should include both what the Skill does and when to use it."
> — [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

> "Descriptions control delegation. If they're vague, the main agent keeps the work for itself. Direct phrasing works best. Use strong cues like 'MUST BE USED' or 'ONLY FOR'."
> — [Claude Code Subagents](https://code.claude.com/docs/en/sub-agents)

---

## Priority 1: Critical (This Week)

### 1.1 Rewrite Skill Descriptions (Evidence-Based)

**Problem**: Skills not invoked because descriptions don't include "when to use" triggers.

**Evidence from data**:
- 244 plan file operations with 0 `/plan` invocations
- 8 ADR file operations with 0 `/architect adr` invocations
- 10 WebSearches on IdeaVim → 0 `analyst:research` invocations

**Official guidance** (from Claude docs):

> "Be specific and include key terms. Include both what the Skill does and specific triggers/contexts for when to use it."

> "**Always write in third person**. The description is injected into the system prompt, and inconsistent point-of-view can cause discovery problems."

**Correct format** (per official docs):
```yaml
---
name: skill-name
description: |
  [What it does in third person]. Triggers when [condition 1], [condition 2],
  or when user mentions [keyword]. MUST BE USED for [critical scenario].
---
```

**Requirements**:
- ✅ Third person voice (e.g., "Selects and applies..." not "Select and apply...")
- ✅ Under 1024 characters
- ✅ Includes both "what" and "when"

**Specific skill rewrites needed**:

| Skill | Current Gap | Evidence-Based Rewrite (Third Person) |
|-------|-------------|---------------------------------------|
| `analyst/consider` | No trigger language | `Selects and applies mental models for structured analysis. Triggers when user asks "why", "what if", "how should we", or needs systematic problem-solving. MUST BE USED when comparing options or making decisions.` |
| `analyst/research` | MCP-tool references only | `Orchestrates systematic research using Firecrawl for authoritative sources. Triggers when user needs to investigate a topic, gather information from multiple sources, or verify facts. Activates PROACTIVELY when 3+ related searches would be needed.` |
| `plan/execution-prompt-generator` | Hidden in description body | `Generates TDD-style execution prompts from design documents. Triggers when reading files in /plans/ directories, when user mentions "execute plan", "TDD prompt", or "implementation prompt". MUST BE USED before implementing from specification.md files.` |
| `impl-flutter/dart-flutter-mcp` | No user triggers | `Provides Flutter and Dart development workflows using dart-mcp tools. Triggers when working with .dart files, pubspec.yaml, or when user mentions Flutter, widget, Riverpod, Freezed, or Dart. MUST BE USED for Flutter project work.` |

---

### 1.2 Rewrite Agent Descriptions with Proactive Triggers

**Problem**: Agents not auto-selected because descriptions lack "MUST BE USED" cues.

**Official guidance** (from Claude docs):

> "Ensure your agent's description field clearly indicates when it should be used, for example: 'Use PROACTIVELY when code changes might impact performance. MUST BE USED for optimization tasks.'"

**Correct examples from docs**:
- `"Use PROACTIVELY after code changes. Perform security, style, and maintainability review."`
- `"Plan Laravel features. Use PROACTIVELY after a new request."`
- `"MUST BE USED for optimization tasks."`

**Note**: Agent descriptions use imperative voice with "Use PROACTIVELY" per official subagent docs (different from skill third-person requirement).

**Specific agent rewrites needed**:

| Agent | Current Description | Evidence-Based Rewrite |
|-------|---------------------|------------------------|
| `architect:architecture-reviewer` | Good but lacks PROACTIVELY | `Reviews architecture for LCA compliance and structural consistency. Use PROACTIVELY when user mentions "architect", "review design", or "architecture review". MUST BE USED when reading ARCHITECTURE.md or modifying component boundaries.` |
| `impl-flutter:flutter-env` | Only covers failures | `Flutter environment diagnostics and lifecycle management. Use PROACTIVELY for "check environment", "verify setup", "start emulator", or when builds fail. MUST BE USED before running Flutter on device.` |
| `analyst:research` (agent) | No proactive cue | `Authoritative research using Firecrawl MCP. Use PROACTIVELY when investigation is needed before action. MUST BE USED when user says "research", "investigate", or "find out about".` |

**Verification Status**: ✅ Confirmed - "PROACTIVELY" and "MUST BE USED" are documented trigger cues per [Subagents Guide](https://www.lexo.ch/blog/2025/11/claude-code-subagents-guide-build-specialized-ai-teams/)

---

### 1.3 Add Path-Based Rules to Target Project CLAUDE.md Files

**Problem**: No path-conditional guidance triggers plugins.

**Official mechanism**: CLAUDE.md supports `paths:` frontmatter for conditional rules.

**Verification Status**: ✅ Confirmed - [Memory docs](https://code.claude.com/docs/en/memory) document this feature with glob pattern support.

**Evidence**: 8 ADR file operations in `architecture/decisions/` without plugin use.

**Solution**: Add to lucid-apps/CLAUDE.md and other target projects:

```markdown
---
paths: architecture/decisions/**
---

# ADR Work
When creating or editing Architecture Decision Records:
- Use `/architect adr` for new ADR creation
- Use `architect:adr-writer` agent for structured documentation
- Follow ADR template in adr-000-template.md

---
paths: **/plans/**
---

# Plan Work
When working with execution plans or specifications:
- Use `/plan validate` after editing plan files
- Use `plan:execution-prompt-generator` skill before implementation
- Ensure TDD structure is maintained

---
paths: **/*.dart
---

# Flutter Development
For Dart/Flutter file work:
- Use `impl-flutter:flutter-coder` for feature implementation
- Use `impl-flutter:flutter-tester` for test writing
- Use `impl-flutter:flutter-env` for environment issues
```

---

## Priority 2: High (This Week)

### 2.1 Add Delegation Patterns to CLAUDE.md (Pattern-Based, Not Count-Based)

**Problem**: Original plan proposed "25+ tool threshold" but Claude cannot count its own tools.

**Official guidance**:

> "Central AI should conserve context by delegating file explorations and low-lift tasks to sub-agents, reserving context for coordination, user communication, and strategic decisions."

**Evidence-based solution** (pattern recognition, not counting):

```markdown
## Delegation Patterns

### Recognize These Patterns → Delegate Immediately

| User Request Pattern | Delegate To |
|---------------------|-------------|
| "find where X", "search for Y", "what files" | Task(Explore) |
| "update all", "fix across", "refactor everywhere" | Task(general-purpose) |
| "implement [feature]" in Flutter project | Task(impl-flutter:flutter-coder) |
| "review architecture", "architect review" | Task(architect:architecture-reviewer) |
| "research [topic]", "investigate", "find out" | Task(analyst:research) |
| "analyze", "think through", "consider options" | Skill(analyst:consider) |

### After Completing Work Units
When you've finished a coherent phase (exploration, initial implementation):
- Pause and assess: "Should the next phase be delegated?"
- Prefer delegation for: multi-file changes, long edit sequences, research phases

### Context Protection Rule
If you notice you've done 5+ sequential Edit operations on related files,
delegate remaining edits to a subagent to protect main context.
```

---

### 2.2 Implement Manual Compaction Strategy

**Problem**: 5 compactions at 95% threshold caused context quality issues.

**Verification Status**: ✅ Confirmed - Manual compaction at natural breakpoints is documented best practice.

**Community evidence**:

> "Sessions that stop at 75% utilization produce less total output but higher-quality, more maintainable code that actually ships."
> — [Managing Claude Code Context](https://mcpcat.io/guides/managing-claude-code-context/)

> "Don't wait for the auto-compact to kick in. When you've finished a feature, run `/compact` yourself."
> — [Claude Code Compaction Guide](https://stevekinney.com/courses/ai-development/claude-code-compaction)

**Add to CLAUDE.md**:

```markdown
## Context Management

### Proactive Compaction (Target: 70-75%)
- Check `/context` after completing each work unit
- Run `/compact` manually when approaching 70% capacity
- Use custom summaries: `/compact preserve the architectural decisions and file patterns`

### Sub-Agent Context Protection
Each subagent gets its own context window. Use this to:
- Offload exploration (Task(Explore))
- Offload multi-file implementations (Task(general-purpose))
- Keep main context for coordination and user communication

### High-Context-Cost Activities (Delegate These)
- Reading large files (>300 lines)
- Test output analysis
- Multi-file exploration
- Long Edit/Read cycles
```

---

### 2.3 Document Explore-then-Implement Workflow

**Problem**: Best workflow pattern not documented.

**Evidence**: Session `a4dde869` showed ideal pattern:
```
Task(Explore) → Task(Explore) → flutter-env → flutter-data → flutter-ux → flutter-coder
```

**Official guidance**:

> "Rely on clear subagent descriptions and focused system prompts to improve automatic selection accuracy. Use automatic delegation in interactive sessions."

**Create**: `docs/workflows/explore-then-implement.md`

```markdown
# Explore-then-Implement Workflow

## The Pattern (Evidence-Based)
From session a4dde869 (successful 5-agent implementation):

1. **Explore first**: Delegate understanding to Explore agents
2. **Review results**: Human reviews exploration findings
3. **Implement in phases**: Use specialized agents per phase
4. **Verify**: Test and validate

## Example Implementation

### Phase 1: Exploration
```
Task(Explore): "Find existing auth patterns, user model, and infrastructure"
Task(Explore): "Identify all files that will need modification"
```

### Phase 2: Human Review
Review exploration results. Identify approach and sequence.

### Phase 3: Phased Implementation
```
Task(impl-flutter:flutter-env): "Set up Firebase Auth dependencies"
Task(impl-flutter:flutter-data): "Create auth service and state providers"
Task(impl-flutter:flutter-ux): "Implement login/signup UI screens"
Task(impl-flutter:flutter-coder): "Wire auth flow and navigation"
```

### Phase 4: Verification
```
Task(impl-flutter:flutter-tester): "Write auth flow integration tests"
```

## Why This Works
- Each agent has isolated context (no pollution)
- Main context reserved for coordination
- Parallel execution possible
- Clear phase boundaries for review
```

---

## Priority 3: Medium (Next Week)

### 3.1 Add PostToolUse Hook for Auto-Suggestions

**Problem**: No automated suggestions when plugin-relevant patterns detected.

**Official mechanism**: PostToolUse hooks can trigger after tool completion.

**Example from docs**:

> "PostToolUse runs immediately after a tool completes successfully."

**⚠️ Implementation Note**: The hook mechanism is verified, but the UX of stderr output may not achieve the desired "prompt" effect. Consider testing whether hook stdout/stderr messages appear contextually to Claude or only to the user terminal.

**Implementation**: Add to `.claude/settings.json` in target projects:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "type": "command",
        "command": "python3 .claude/hooks/suggest_plugin.py \"$TOOL_INPUT\""
      }
    ]
  }
}
```

**Hook script** (`.claude/hooks/suggest_plugin.py`):
```python
#!/usr/bin/env python3
import sys
import json

tool_input = json.loads(sys.argv[1])
file_path = tool_input.get("file_path", "")

suggestions = []
if "adr-" in file_path or "architecture/decisions" in file_path:
    suggestions.append("Consider using /architect adr for ADR management")
if "/plans/" in file_path:
    suggestions.append("Consider using /plan validate after plan edits")

if suggestions:
    # Note: stderr output appears as warning to user, may not influence Claude
    # Test whether stdout or a different mechanism better achieves the goal
    print("\n".join(suggestions), file=sys.stderr)
```

**Verification Status**: ⚠️ Mechanism correct, UX needs testing in isolated environment first

---

### 3.2 Create Plugin Discovery Command

**Problem**: Users unaware of available plugins.

**Solution**: Add `/luc plugins` command showing installed plugins and triggers.

```markdown
---
name: plugins
description: Show installed plugins and when to use them
---

# Available Plugins

## architect (v1.1.0)
**Trigger phrases**: "architect", "review design", "ADR", "architecture"
**Commands**: /architect init, /architect adr, /architect review
**Agents**: architecture-reviewer, adr-writer, component-analyzer

## analyst (v2.0.0)
**Trigger phrases**: "analyze", "consider", "think through", "research"
**Commands**: /consider, /assess, /reflect, /debate
**Agents**: research, model-* (mental models)

## impl-flutter (v2.1.0)
**Trigger phrases**: "flutter", "dart", "widget", "implement feature"
**Agents**: flutter-coder, flutter-tester, flutter-ux, flutter-env, flutter-data

## plan (v2.1.0)
**Trigger phrases**: "plan", "TDD", "execute", "specification"
**Commands**: /plan generate, /plan analyze, /plan validate
```

---

### 3.3 Add Parallel Execution Guidance

**Problem**: 12 of 19 sessions showed 0% parallel execution.

**Official guidance**:

> "When you have multiple agents, they won't coordinate unless you give them a shared log. progress.md works as that link."

**Add to CLAUDE.md**:

```markdown
## Parallel Execution

### Parallelize Independent Operations
Launch multiple Task agents simultaneously for independent work:
```
Task(impl-flutter:flutter-coder): "Implement login screen"
Task(impl-flutter:flutter-tester): "Write auth unit tests"
Task(impl-flutter:flutter-ux): "Design onboarding flow"
```

### Coordinate via progress.md
Create `progress.md` at project root for multi-agent coordination:
```markdown
# Progress Log

## Active Tasks
- [ ] Login screen implementation (flutter-coder)
- [ ] Auth unit tests (flutter-tester)

## Completed
- [x] Auth service setup
```

### Read Operations (Always Parallelize)
Instead of sequential reads (one tool call per message):
```
Message 1: Read file1.dart → Wait for response
Message 2: Read file2.dart → Wait for response
Message 3: Read file3.dart → Wait for response
```

Use parallel (multiple tool calls in single message):
```
Single message with 3 Read tool invocations:
- Read file1.dart
- Read file2.dart
- Read file3.dart
All execute before Claude continues.
```

**Note**: Claude Code processes multiple tool calls in a single response in parallel automatically.
```

---

## Implementation Checklist

### Week 1 (Critical + High)
- [ ] Rewrite 4 skill SKILL.md description fields (integrated triggers)
- [ ] Rewrite 3 agent description fields (MUST BE USED/PROACTIVELY)
- [ ] Add path-based rules to lucid-apps CLAUDE.md
- [ ] Add path-based rules to lucid-knowledge CLAUDE.md
- [ ] Add delegation pattern table to CLAUDE.md templates
- [ ] Add compaction strategy to CLAUDE.md templates
- [ ] Document explore-then-implement workflow

### Week 2 (Medium)
- [ ] Implement PostToolUse suggestion hook
- [ ] Create /luc plugins discovery command
- [ ] Add parallel execution guidance to CLAUDE.md
- [ ] Add progress.md coordination pattern
- [ ] Test trigger detection with sample prompts

### Validation
- [ ] Test each skill rewrite with trigger phrases
- [ ] Verify path rules activate on file access
- [ ] Measure delegation rate after changes
- [ ] Track compaction frequency

---

## Success Metrics

| Metric | Current | Week 1 | Week 2 | Month 1 |
|--------|---------|--------|--------|---------|
| Delegation rate | 0-3% | 20% | 40% | >50% |
| Plugin invocations/session | 0.26 | 1.0 | 2.0 | 3.0 |
| Compaction at 95% | 5/2days | 2/week | 1/week | <1/week |
| Manual compact at 70% | 0% | 30% | 60% | 80% |

---

## Evidence Cross-Reference

| Issue (from data) | Root Cause | Solution | Source |
|-------------------|------------|----------|--------|
| 244 plan ops, 0 invokes | Description lacks triggers | Rewrite with "Use when" | [Skill best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) |
| 8 ADR ops, 0 invokes | No path-based guidance | CLAUDE.md `paths:` rules | [CLAUDE.md Mastery](https://claudefa.st/blog/guide/mechanics/claude-md-mastery) |
| 136 tools, 0 delegation | No pattern recognition | Delegation pattern table | [Subagents docs](https://code.claude.com/docs/en/sub-agents) |
| 5 compactions at 95% | Waiting for auto-compact | Manual at 70% | [Context guide](https://mcpcat.io/guides/managing-claude-code-context/) |
| 10 WebSearches, no research | Description MCP-only | Add "PROACTIVELY" cue | [Subagents docs](https://code.claude.com/docs/en/sub-agents) |
| 0% parallel execution | No guidance | Parallel patterns section | [Task distribution](https://claudefa.st/blog/guide/agents/task-distribution) |

---

## Key Corrections from Original Plan

| Original Proposal | Why Wrong | Corrected Approach |
|-------------------|-----------|-------------------|
| Separate "INVOKE WHEN" sections | Not read during discovery | Integrate into `description:` field |
| plugin.json `triggers` feature | Feature doesn't exist | Use CLAUDE.md `paths:` rules |
| "25+ tool threshold" | Claude can't count tools | Pattern recognition table |
| "Monitor 150K tokens" | Claude can't see tokens | Work unit checkpoints + manual /compact |

---

## Appendix: Official Description Format

From [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices):

```yaml
# CORRECT - Integrated triggers
description: |
  Extract text and tables from PDF files, fill forms, merge documents.
  Use when working with PDF files or when the user mentions PDFs, forms,
  or document extraction.

# WRONG - Separate section (won't be read)
description: Brief description.

INVOKE when:  # ← This is body content, not description!
- condition 1
```

From [Claude Code Subagents](https://code.claude.com/docs/en/sub-agents):

```yaml
# CORRECT - Proactive cue in description
description: |
  Use PROACTIVELY after code changes. Perform security, style,
  and maintainability review. MUST BE USED for code review tasks.

# WRONG - Vague description
description: Reviews code.  # ← No trigger cues
```

---

## Appendix: Verification Summary

**Verified 2025-12-14** against official documentation and session data.

### Fix Verification Status

| Fix | Status | Confidence | Notes |
|-----|--------|------------|-------|
| 1.1 Skill description rewrites | ✅ VERIFIED | High | Updated to third-person voice |
| 1.2 Agent description rewrites | ✅ VERIFIED | High | PROACTIVELY/MUST BE USED confirmed |
| 1.3 Path-based CLAUDE.md rules | ✅ VERIFIED | High | `paths:` frontmatter documented |
| 2.1 Pattern-based delegation | ✅ VERIFIED | High | Correct approach vs count-based |
| 2.2 Manual compaction strategy | ✅ VERIFIED | High | Aligns with community best practices |
| 2.3 Explore-then-implement workflow | ✅ VERIFIED | High | Session evidence supports |
| 3.1 PostToolUse hook | ⚠️ PARTIAL | Medium | Mechanism correct, UX needs testing |
| 3.2 Plugin discovery command | ✅ VERIFIED | High | Good discoverability improvement |
| 3.3 Parallel execution guidance | ✅ VERIFIED | High | Notation corrected |

### Documentation Sources Consulted

1. [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) - Official Anthropic
2. [Claude Code Subagents](https://code.claude.com/docs/en/sub-agents) - Official Claude Code
3. [Claude Code Memory](https://code.claude.com/docs/en/memory) - paths: frontmatter docs
4. [Claude Code Compaction](https://stevekinney.com/courses/ai-development/claude-code-compaction) - Community guide
5. [Claude Code Subagents Guide](https://www.lexo.ch/blog/2025/11/claude-code-subagents-guide-build-specialized-ai-teams/) - Community patterns

### Key Corrections Made During Verification

| Original | Issue | Corrected |
|----------|-------|-----------|
| "Use when user asks" | Imperative voice | "Triggers when user asks" (third person) |
| `[Read(...), Read(...)]` notation | Not actual syntax | Prose description of parallel tool calls |
| stderr hook output | May not influence Claude | Added warning, needs UX testing |
