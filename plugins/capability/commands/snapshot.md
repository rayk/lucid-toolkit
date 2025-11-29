---
description: Generate a concise snapshot of all capabilities showing structure, maturity, and key metrics
---

<objective>
Display the pre-computed capability snapshot showing hierarchical structure, maturity levels, and health indicators.

Performance: Displays cached snapshot in <100ms (vs ~16s for LLM generation).
</objective>

<context>
Pre-computed snapshot: @capabilities/SNAPSHOT.md
</context>

<process>
1. Check if capabilities/SNAPSHOT.md exists
2. If exists: Display its contents directly (no processing needed)
3. If missing: Run the regeneration hook, then display:
   ```bash
   echo '{}' | python3 hooks/hooks/regenerate_snapshot.py
   ```
   Then read and display capabilities/SNAPSHOT.md
</process>

<success_criteria>
- Snapshot displayed instantly from cache
- All capabilities shown with correct hierarchy
- Maturity percentages accurate
- Blocked and at-risk capabilities clearly flagged
- Output fits in terminal without horizontal scroll
</success_criteria>

<output_format>
When returning capability data to the main conversation or as a subagent response, use TOON format for structured data:

**Capability List (Subagent Return):**
```toon
@type: ItemList
name: capabilities
numberOfItems: 5
x-avgMaturity: 52

itemListElement[5]{name,x-maturity,x-target,actionStatus,x-domain|tab}:
authentication-system	47	80	ActiveActionStatus	Data Security & Privacy
tenant-isolation	35	90	ActiveActionStatus	Data Security & Privacy
admin-portal	100	80	CompletedActionStatus	Product Lifecycle
api-gateway	60	75	ActiveActionStatus	Integration
logging-system	75	90	ActiveActionStatus	Operations
```

**ActionStatusType Mapping:**
- Capabilities with maturity < target: `ActiveActionStatus`
- Capabilities at target maturity: `CompletedActionStatus`
- Blocked capabilities: `FailedActionStatus`

**TOON Format Notes:**
- Use tab delimiter (`|tab`) for x-domain field since domain descriptions may contain spaces
- numberOfItems provides quick count without parsing array
- x-avgMaturity shows portfolio health at a glance
- Keep narrative/markdown format for human-facing snapshot display
- Use TOON only for machine-to-machine data exchange
</output_format>

