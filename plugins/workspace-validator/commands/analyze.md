---
description: Deep analysis of workspace claude prompts, configurations, and scripts.
---

<objective>
Produce a detailed report about the status of the Claude Code CLI configurations, prompts,
scripts and schemas. Detail all issues and offer validated solutions that can be immediately
applied to address those problems.
</objective>

<context>
```
.claude/
├── commands/               # Slash commands for workflow automation
│   ├── cap/               # Capability-related commands
│   ├── out/               # Outcome-related commands
│   └── tools/             # Tool commands (this file is in tools/)
├── prompts/               # Reusable prompt templates
├── schema/                # JSON schemas for validation
├── settings.json          # Claude Code hook configuration
├── shared/                # Shared resources
│   ├── hook_scripts/      # Python hook implementations
│   └── templates/         # Shared templates
├── skills/                # Skill definitions
│   ├── command-builder/   # Command building skill
│   ├── coordinate-subagents/  # Subagent coordination skill
│   └── skill-builder/     # Skill building skill
└── temp/                  # Temporary files (auto-cleaned)
    └── outcap/            # Outcome/capability temp work
```
</context>

<workflow>

<step name="analyze_commands">
**Analyze Commands**
- Glob for commands/**/*.md
- For each command, verify:
  - YAML frontmatter valid (description field present)
  - No broken @ references
  - If uses arguments, has argument-hint in frontmatter
  - Pure XML structure (no markdown headings ## in body)
</step>

<step name="analyze_skills">
**Analyze Skills**
- Glob for skills/*/SKILL.md
- For each skill, verify:
  - YAML frontmatter valid (name, description fields)
  - Pure XML structure (no markdown headings in body)
  - Required tags present (objective, quick_start, success_criteria)
  - Line count < 500 (progressive disclosure)
  - References directory exists if referenced
</step>

<step name="analyze_agents">
**Analyze Agents**
- Glob for agents/*.md
- For each agent, verify:
  - YAML frontmatter valid (name, description, tools, model)
  - All @ references resolve to existing files
  - Pure XML structure
  - Model selection appropriate (haiku/sonnet/opus)
</step>

<step name="analyze_schemas">
**Analyze Schemas**
- Glob for schemas/*.json
- For each schema, verify:
  - Valid JSON syntax
  - $ref references resolve to existing schemas
  - Required properties defined
</step>

<step name="analyze_hooks">
**Analyze Hook Scripts**
- Read .claude/settings.json
- For each hook configured:
  - Verify hook command/script exists
  - Test script for Python syntax errors
  - Check for proper error handling
</step>

</workflow>

<output_format>
Produce report in this structure:

**Workspace Analysis Report**

**Summary**
- Commands: X total, Y issues
- Skills: X total, Y issues
- Agents: X total, Y issues
- Schemas: X total, Y issues
- Hooks: X total, Y issues

**Critical Issues** (must fix)
1. [File:line] - Issue description
   - Fix: [specific action]

**Recommendations** (should fix)
1. [File:line] - Issue description
   - Fix: [specific action]

**Healthy** (passing validation)
- [List of files passing all checks]
</output_format>

<success_criteria>
- All 5 analysis steps completed
- Every issue has file:line reference
- Every issue has specific, actionable fix
- Report is scannable and prioritized
- No false positives (verified issues only)
</success_criteria>
