---
description: Guide efficient subagent invocation with schema.org vocabulary and token budgets
argument-hint: [optional context about the subagent task]
allowed-tools: Skill(coordinate-subagents)
---

<objective>
Delegate subagent coordination guidance to the coordinate-subagents skill: $ARGUMENTS

This routes to specialized skill containing schema.org patterns, token budget guidance, and efficient prompt structuring for Task tool invocations.
</objective>

<process>
1. Use Skill tool to invoke coordinate-subagents skill
2. Pass user's request: $ARGUMENTS
3. Let skill provide structured guidance for efficient subagent invocation
</process>

<success_criteria>
- Skill successfully invoked
- Guidance provided for schema.org-based prompts
- Token budgets appropriate for task complexity
- Output format explicitly specified
</success_criteria>
