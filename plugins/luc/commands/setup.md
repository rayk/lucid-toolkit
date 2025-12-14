---
description: Idempotent project setup - detects state, generates project-info.toon, validates CLAUDE.md
argument-hint: (none - operates on current directory)
allowed-tools: [Task, AskUserQuestion]
---

<objective>
Configure foundational Claude Code settings for any project through an idempotent command that detects current state and performs the appropriate action: initialize, repair, migrate, or report.

This command delegates to a setup specialist agent that:
1. Establishes `.claude/` directory and `project-info.toon`
2. Configures Claude Code status line
3. Validates CLAUDE.md contains required behavioral instructions for plugin effectiveness
</objective>

<context>
Current state:
- Project info exists: !`test -f .claude/project-info.toon && echo "yes" || echo "no"`
- CLAUDE.md exists: !`test -f CLAUDE.md && echo "yes" || echo "no"`
- Git status: !`git status --short 2>/dev/null | head -5`
- Current branch: !`git branch --show-current 2>/dev/null || echo "not a git repo"`
- Settings statusLine: !`jq -r '.statusLine // "not configured"' ~/.claude/settings.json 2>/dev/null || echo "no settings file"`
</context>

<process>
## Immediate User Notification

```
Starting project setup scan...
```

## Delegate to Setup Specialist

Launch setup-specialist agent to handle the full workflow:

```
Task(subagent_type="luc:setup-specialist", prompt="""
Execute idempotent project setup for the current directory.

Current state from context:
- project-info.toon: {exists or not from context}
- CLAUDE.md: {exists or not from context}
- Git branch: {from context}
- Status line: {configured or not from context}

Perform:
1. Detect state (virgin/healthy/outdated/corrupted)
2. Execute appropriate action (INITIALIZE/REPORT/MIGRATE/REPAIR)
3. Validate CLAUDE.md behavioral coverage
4. Report results with coverage percentages

If CLAUDE.md needs updates, use AskUserQuestion to confirm before modifying.

Template for new/updated CLAUDE.md: ~/.claude/plugins/luc@lucid-toolkit/templates/CLAUDE.md.template
""")
```

## Present Results

Report the agent's findings to the user with:
- State detected and action taken
- Files generated/modified
- CLAUDE.md coverage status
- Any user decisions needed
</process>

<verification>
After agent completes:
- .claude/project-info.toon exists and is valid TOON format
- Status line configured in ~/.claude/settings.json
- CLAUDE.md coverage percentage reported
- User informed of any missing behavioral sections
</verification>

<success_criteria>
**Idempotency:**
- Running multiple times produces same result
- Existing valid configuration preserved
- Only regenerates when needed

**Delegation:**
- All complex logic handled by setup-specialist agent
- Main context preserved for user communication
- Agent handles state detection, scanning, file generation

**User Communication:**
- Clear progress indication
- Summary of actions taken
- CLAUDE.md coverage percentage shown
- Missing sections explicitly listed
</success_criteria>

<schema_reference>
## Schema / Instance Relationship

**Schema**: `luc/schemas/project-info-schema.toon` (read-only reference)
**Instance**: `.claude/project-info.toon` (generated output)
**Template**: `luc/templates/CLAUDE.md.template` (CLAUDE.md source)

The schema defines structure with type annotations:
- `→const` - Fixed value, copy exactly
- `→string` - Text value
- `→string?` - Optional (can be null)
- `→int` - Integer
- `→datetime` - ISO-8601 timestamp
- `→enum[Name]` - One of defined values
</schema_reference>

<output>
Files created/modified by agent:
- `.claude/project-info.toon` - Project metadata in TOON format
- `~/.claude/settings.json` - Status line configuration (if not already set)
- `CLAUDE.md` - Behavioral instructions (only if user accepts)
</output>
