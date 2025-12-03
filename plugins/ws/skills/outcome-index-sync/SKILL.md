---
name: outcome-index-sync
description: Synchronizes outcome indexes after outcome modifications. Invokes toon-specialist to regenerate outcomes-info.toon and update project-info.toon. Use after out/create, out/edit, out/delete, or stage transitions.
---

<objective>
Regenerate outcome index files after any outcome modification to keep workspace indexes in sync with outcome definitions. This is a cross-cutting concern invoked by all out/* commands.
</objective>

<quick_start>
After modifying an outcome, invoke this skill:

```
Skill("outcome-index-sync")
```

The skill will:
1. Scan all outcome-statement.md files across all stages
2. Regenerate outcomes-info.toon via toon-specialist
3. Update project-info.toon outcome summary
</quick_start>

<context>
<files_updated>
| File | Purpose |
|------|---------|
| `.claude/outcomes-info.toon` | Index of all outcomes with stage, priority, contributions |
| `.claude/project-info.toon` | Project summary including outcome counts |
</files_updated>

<trigger_commands>
This skill is invoked by:
- `out/create` - After new outcome created
- `out/edit` - After outcome modified
- `out/delete` - After outcome removed
- Stage transitions (queued → ready → in-progress → completed)
</trigger_commands>
</context>

<process>
<step_1>
**Read workspace configuration**

Read project-info.toon to get outcomes path:

```
Read(".claude/project-info.toon")
```

Extract `outcomes.path` for scanning.
</step_1>

<step_2>
**Scan all outcome directories**

Scan for outcome-statement.md files across all stages:

```
Glob(pattern="{outcomes.path}/*/outcome-statement.md")
Glob(pattern="{outcomes.path}/*/*/outcome-statement.md")  # For child outcomes
```
</step_2>

<step_3>
**Extract outcome data**

For each outcome-statement.md, extract YAML frontmatter:
- identifier
- name
- stage (queued/ready/in-progress/blocked/completed)
- priority (P1/P2/P3)
- capabilityContributions (list)
- parentOutcome (for child outcomes)
- tokenBudget
</step_3>

<step_4>
**Invoke toon-specialist to regenerate outcomes-info.toon**

```
Task(
  subagent_type="ws:toon-specialist",
  prompt="""
  @type: CreateAction
  name: produce
  object.schema: outcomes-info-schema.toon
  object.output: .claude/outcomes-info.toon
  object.data: {extracted outcome data as structured list}

  Include:
  - stages.summary with counts per stage (all 5 stages)
  - outcome.index with all outcomes
  - capability.contributions aggregated
  - outcome.hierarchy for parent/child relationships
  - recentActivity for last 7 days
  """
)
```
</step_4>

<step_5>
**Update project-info.toon outcome summary**

```
Task(
  subagent_type="ws:toon-specialist",
  prompt="""
  @type: UpdateAction
  name: convert
  object.source: .claude/project-info.toon
  object.target: .claude/project-info.toon
  object.schema: workspace-info-schema.toon

  Update these fields:
  - outcomes.count: {total count}
  - outcomes.inProgress: {in-progress count}
  - outcomes.completed: {completed count}
  - outcomes.blocked: {blocked count}
  """
)
```
</step_5>
</process>

<constraints>
- MUST use toon-specialist for all .toon file writes
- MUST preserve existing project-info.toon data (only update outcome summary)
- MUST include all 5 stages in stages.summary (even if count=0)
- MUST handle nested child outcomes (dot notation: 005.1-name)
- SHOULD complete in under 6 tool calls
</constraints>

<success_criteria>
- outcomes-info.toon reflects current state of all outcomes
- All 5 stages present in stages.summary
- Parent/child relationships captured in outcome.hierarchy
- Capability contributions aggregated correctly
- project-info.toon outcome summary is accurate
- toon-specialist confirms valid TOON output
</success_criteria>
