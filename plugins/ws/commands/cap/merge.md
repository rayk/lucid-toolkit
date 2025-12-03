---
description: Merge two or more capabilities into one
argument-hint: <target-id> --sources <source-id1,source-id2,...>
---

<objective>
Combine multiple related capabilities into a single capability, consolidating their definitions, actors, values, and relationships.
</objective>

<context>
**Files to Read:**
| Purpose | Path |
|---------|------|
| Workspace config | `.claude/workspace-info.toon` |
| Target capability | `{capabilities.path}/{target-id}/` |
| Source capabilities | `{capabilities.path}/{source-id}/` for each source |
</context>

<process>

## Phase 1: Validate Merge

1. **Read workspace-info.toon** to get capabilities.path
2. **Verify target exists** (or will be created)
3. **Verify all sources exist**
4. **Check for conflicts**:
   - Overlapping actor relationships
   - Incompatible types (atomic + composed)

## Phase 2: Plan Merge

5. **Combine YAML frontmatter**:
   - Union of actors (deduplicate by ID)
   - Union of coreValues (recalculate contributions to sum 100%)
   - Merge relationships.prerequisites (deduplicate)
   - Merge relationships.enables (deduplicate)
   - Use higher maturity.target of sources
   - Sum maturity.current weighted by source sizes

6. **Combine markdown body**:
   - Merge scope inclusions/exclusions
   - Combine value propositions
   - Merge maturity milestones

## Phase 3: Execute Merge

7. **Create/update target capability-statement.md**
8. **Mark source capabilities as deprecated**:
   - Set status: deprecated
   - Add note: "Merged into {target-id}"
9. **Update references**:
   - Find capabilities referencing sources in prerequisites/enables
   - Update to reference target instead

## Phase 4: Validate

10. **Run capability-checker** on target

</process>

<output_format>
```toon
@type: UpdateAction
actionStatus: CompletedActionStatus
@id: {target-id}
result: Merged capabilities

sourcesMerged[N]: {source1},{source2}
referencesUpdated[N]: {cap1},{cap2}
```
</output_format>

<epilogue>
After successful capability merge, sync workspace indexes:

```
Skill("capability-index-sync")
```

This ensures capabilities-info.toon reflects the merged capability and deprecated sources.
</epilogue>
