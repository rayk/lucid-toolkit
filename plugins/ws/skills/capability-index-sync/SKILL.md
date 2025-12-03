---
name: capability-index-sync
description: Synchronizes capability indexes after capability modifications. Invokes toon-specialist to regenerate capabilities-info.toon and update workspace-info.toon. Use after cap/create, cap/edit, cap/delete, cap/merge, or cap/split completes.
---

<objective>
Regenerate capability index files after any capability modification to keep workspace indexes in sync with capability definitions. This is a cross-cutting concern invoked by all cap/* commands.
</objective>

<quick_start>
After modifying a capability, invoke this skill:

```
Skill("capability-index-sync")
```

The skill will:
1. Scan all capability-statement.md files
2. Regenerate capabilities-info.toon via toon-specialist
3. Update workspace-info.toon capability summary
</quick_start>

<context>
<files_updated>
| File | Purpose |
|------|---------|
| `.claude/capabilities-info.toon` | Index of all capabilities with maturity, status |
| `.claude/workspace-info.toon` | Workspace summary including capability count |
</files_updated>

<trigger_commands>
This skill is invoked by:
- `cap/create` - After new capability created
- `cap/edit` - After capability modified
- `cap/delete` - After capability removed
- `cap/merge` - After capabilities merged
- `cap/split` - After capability split
</trigger_commands>
</context>

<process>
<step_1>
**Scan capabilities directory**

Read workspace-info.toon to get capabilities path, then scan for all capability-statement.md files:

```
Glob(pattern="{capabilities.path}/*/capability-statement.md")
```
</step_1>

<step_2>
**Extract capability data**

For each capability-statement.md, extract YAML frontmatter:
- identifier
- name
- type (atomic/composed)
- status (active/deprecated/planned)
- domain
- maturity.current
- maturity.target
</step_2>

<step_3>
**Invoke toon-specialist to regenerate capabilities-info.toon**

```
Task(
  subagent_type="ws:toon-specialist",
  prompt="""
  @type: CreateAction
  name: produce
  object.schema: capabilities-info-schema.toon
  object.output: .claude/capabilities-info.toon
  object.data: {extracted capability data as structured list}
  """
)
```
</step_3>

<step_4>
**Update workspace-info.toon capability summary**

```
Task(
  subagent_type="ws:toon-specialist",
  prompt="""
  @type: UpdateAction
  name: convert
  object.source: .claude/workspace-info.toon
  object.target: .claude/workspace-info.toon
  object.schema: workspace-info-schema.toon

  Update these fields:
  - capabilities.count: {total count}
  - capabilities.activeCount: {active count}
  - capabilities.avgMaturity: {average current maturity}%
  """
)
```
</step_4>
</process>

<constraints>
- MUST use toon-specialist for all .toon file writes
- MUST preserve existing workspace-info.toon data (only update capability summary)
- MUST handle missing capabilities directory gracefully
- SHOULD complete in under 5 tool calls
</constraints>

<success_criteria>
- capabilities-info.toon reflects current state of all capabilities
- workspace-info.toon capability summary is accurate
- No orphaned or missing capability entries
- toon-specialist confirms valid TOON output
</success_criteria>
