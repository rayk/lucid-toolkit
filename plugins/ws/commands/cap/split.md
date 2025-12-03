---
description: Split a capability into multiple smaller capabilities
argument-hint: <source-id> --into <new-id1,new-id2,...>
---

<objective>
Decompose a large or complex capability into multiple focused capabilities, redistributing actors, values, and relationships appropriately.
</objective>

<context>
**Files to Read:**
| Purpose | Path |
|---------|------|
| Workspace config | `.claude/workspace-info.toon` |
| Source capability | `{capabilities.path}/{source-id}/` |
</context>

<process>

## Phase 1: Analyze Source

1. **Read workspace-info.toon** to get capabilities.path
2. **Read source capability-statement.md**
3. **Identify split boundaries**:
   - Distinct scope sections
   - Separable actor groups
   - Independent value propositions

## Phase 2: Plan Split

4. **For each new capability**:
   - Assign subset of scope inclusions
   - Assign relevant actors
   - Distribute coreValues (ensure each sums to 100%)
   - Allocate maturity milestones
   - Set appropriate maturity.target

5. **Handle relationships**:
   - Determine which prerequisites apply to which new capability
   - Determine which enables apply to which new capability
   - Add prerequisites between new capabilities if dependent

## Phase 3: Execute Split

6. **Create new capability directories and statements**
7. **Deprecate source capability**:
   - Set status: deprecated
   - Add note: "Split into {new-id1}, {new-id2}, ..."
8. **Update references**:
   - Find capabilities referencing source
   - Update to reference appropriate new capability(s)

## Phase 4: Validate

9. **Run capability-checker** on each new capability

</process>

<output_format>
```toon
@type: CreateAction
actionStatus: CompletedActionStatus
@id: {source-id}
result: Split capability

newCapabilities[N]: {new-id1},{new-id2}
referencesUpdated[N]: {cap1},{cap2}
```
</output_format>

<epilogue>
After successful capability split, sync workspace indexes:

```
Skill("capability-index-sync")
```

This ensures capabilities-info.toon reflects the new capabilities and deprecated source.
</epilogue>
