---
description: Validate an outcome statement against workspace standards using outcome-checker agent
argument-hint: <outcome-id>
allowed-tools: Read, Glob, Task, Skill
---

<objective>
Validate an outcome statement for schema compliance, content quality, decomposition adequacy, and cross-reference integrity using the outcome-checker agent. After validation, sync workspace indexes (outcomes-info.toon and workspace-info.toon) to reflect any status changes.

This ensures outcomes created by `/ws:out:create` meet workspace standards before execution.
</objective>

<context>
Workspace config: @.claude/workspace-info.toon
Outcome-checker agent: @agents/outcome-checker.md
Output patterns: Follow [output-patterns.md](../../references/output-patterns.md) for consistent formatting
</context>

<argument_normalization>
## Argument Processing

Before using `$ARGUMENTS`, normalize the outcome-id:

1. **Strip prefixes**: Remove `@`, `outcomes/`, and stage names (`queued/`, `ready/`, `in-progress/`, `blocked/`, `completed/`)
2. **Strip trailing slashes**: Remove any trailing `/`
3. **Validate format**: Result must match `^[0-9]+(-[a-z0-9-]+)+$` (parent) or `^[0-9]+\.[0-9]+-[a-z0-9-]+$` (child)

| Input | Normalized |
|-------|------------|
| `@outcomes/ready/005-name/` | `005-name` |
| `outcomes/queued/002.1-child` | `002.1-child` |
| `005-ontology-workflow` | `005-ontology-workflow` |

If normalization fails, report error with expected format.
</argument_normalization>

<process>

## Phase 1: Locate Outcome

1. **Read workspace-info.toon** to get `outcomes.path`
2. **Search for outcome** matching `$ARGUMENTS`:
   - Check `{outcomes.path}/queued/$ARGUMENTS/outcome-statement.md`
   - Check `{outcomes.path}/ready/$ARGUMENTS/outcome-statement.md`
   - Check `{outcomes.path}/in-progress/$ARGUMENTS/outcome-statement.md`
   - Check `{outcomes.path}/blocked/$ARGUMENTS/outcome-statement.md`
   - Check `{outcomes.path}/completed/$ARGUMENTS/outcome-statement.md`
   - Support child outcomes: search recursively for `$ARGUMENTS` pattern (e.g., `005.1-child-name`)
3. **If not found**: Report error with available outcome IDs from all stages

## Phase 2: Run Validation

4. **Invoke outcome-checker agent**:
   ```
   Task(
     subagent_type="ws:outcome-checker",
     prompt="Validate outcome at {found-outcome-path}"
   )
   ```

5. **Process validation result**:
   - VALID → Report success with checks performed
   - NEEDS_ATTENTION → Show warnings, ask if user wants to fix
   - INVALID → Show critical issues, offer to help fix

## Phase 3: Sync Indexes

6. **Update workspace indexes** to reflect validation status:
   ```
   Skill("outcome-index-sync")
   ```
   This updates:
   - `outcomes-info.toon` - outcome registry with validation timestamp and status
   - `workspace-info.toon` - workspace summary with current outcome counts by stage

</process>

<output_format>
```toon
@type: AssessAction
actionStatus: CompletedActionStatus
@id: $ARGUMENTS

validationStatus: {VALID|NEEDS_ATTENTION|INVALID}
outcomeType: {parent|atomic|child}
stage: {queued|ready|in-progress|blocked|completed}
checksPerformed: 10
issues.critical: {count}
issues.warning: {count}
issues.info: {count}

indexesSynced: true
outcomesInfoUpdated: true
workspaceInfoUpdated: true
```
</output_format>

<success_criteria>
- Outcome located across all stage directories (including nested child outcomes)
- All 10 evaluation areas checked:
  - file_structure
  - schema_validation
  - achievement_focus
  - observable_effects_behavioral (Given-When-Then format)
  - capability_alignment (for parent/standalone)
  - child_contribution_validation (for children)
  - parent_decomposition (for parents - contribution math, scope coverage)
  - cross_reference_integrity
  - placeholder_detection
  - actor_validation
- Validation status clearly reported
- If parent outcome: child decomposition validated
- If INVALID: failure report created at outcome path
- outcomes-info.toon updated with validation timestamp and status
- workspace-info.toon synced to reflect current outcome state
</success_criteria>
