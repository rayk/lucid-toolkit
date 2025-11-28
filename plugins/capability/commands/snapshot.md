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
   echo '{}' | python3 hooks/capability_snapshot/hooks/regenerate_snapshot.py
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
