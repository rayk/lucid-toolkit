---
description: Delete a capability from the workspace
argument-hint: <capability-id> [--force]
---

<objective>
Remove a capability and its directory from the workspace, updating all references and indexes.
</objective>

<context>
**Files to Read:**
| Purpose | Path |
|---------|------|
| Workspace config | `.claude/workspace-info.toon` |
| Target capability | `{capabilities.path}/{capability-id}/` |
</context>

<process>

## Phase 1: Validate Deletion

1. **Read workspace-info.toon** to get capabilities.path
2. **Verify capability exists** at `{capabilities.path}/{capability-id}/`
3. **Check for dependencies**:
   - Scan other capabilities for `relationships.prerequisites` referencing this ID
   - Scan for `relationships.enables` referencing this ID
   - If dependencies found and `--force` not specified: ABORT with list

## Phase 2: Confirm Deletion

4. **If dependencies exist**: Show warning with dependent capabilities
5. **Ask for confirmation** (unless `--force` specified):
   - "Delete capability '{capability-id}'? This cannot be undone."

## Phase 3: Execute Deletion

6. **Remove capability directory**:
   ```bash
   rm -rf {capabilities.path}/{capability-id}/
   ```

7. **Update dependent capabilities** (if `--force` was used):
   - Remove deleted capability from their prerequisites/enables lists
   - Log which capabilities were updated

</process>

<output_format>
```toon
@type: DeleteAction
actionStatus: CompletedActionStatus
@id: {capability-id}
result: Deleted capability

dependentsUpdated[N]: {cap1},{cap2}
```
</output_format>

<epilogue>
After successful capability deletion, sync workspace indexes:

```
Skill("capability-index-sync")
```

This ensures capabilities-info.toon and project-info.toon no longer reference the deleted capability.
</epilogue>
