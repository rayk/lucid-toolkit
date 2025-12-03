---
description: Validate an outcome statement against workspace standards using outcome-checker agent
argument-hint: <outcome-id>
---

<objective>
Validate an outcome statement for schema compliance, content quality, Given-When-Then format, and cross-reference integrity using the outcome-checker agent. After validation, sync workspace indexes to reflect any status changes.

This ensures outcome statements meet workspace standards before being used in planning or execution.
</objective>

<context>
Workspace config: @.claude/project-info.toon
Outcome-checker agent: @agents/outcome-checker.md
</context>

<process>

## Phase 1: Locate Outcome

1. **Read project-info.toon** to get `outcomes.path`
2. **Search for outcome** across all stages:
   - `{outcomes.path}/queued/$ARGUMENTS/outcome-statement.md`
   - `{outcomes.path}/ready/$ARGUMENTS/outcome-statement.md`
   - `{outcomes.path}/in-progress/$ARGUMENTS/outcome-statement.md`
   - `{outcomes.path}/blocked/$ARGUMENTS/outcome-statement.md`
   - `{outcomes.path}/completed/$ARGUMENTS/outcome-statement.md`
3. **If not found**: Report error with available outcome IDs

## Phase 2: Run Validation

4. **Invoke outcome-checker agent**:
   ```
   Task(
     subagent_type="ws:outcome-checker",
     prompt="Validate outcome at {found-path}"
   )
   ```

5. **Process validation result**:
   - VALID ’ Report success
   - NEEDS_ATTENTION ’ Show warnings, ask if user wants to fix
   - INVALID ’ Show critical issues, offer to help fix

## Phase 3: Sync Indexes

6. **Update workspace indexes** to reflect validation status:
   ```
   Skill("outcome-index-sync")
   ```

</process>

<output_format>
```toon
@type: AssessAction
actionStatus: CompletedActionStatus
@id: $ARGUMENTS

validationStatus: {VALID|NEEDS_ATTENTION|INVALID}
stage: {current stage}
checksPerformed: 8
issues.critical: {count}
issues.warning: {count}
issues.info: {count}

indexesSynced: true
```
</output_format>

<success_criteria>
- Outcome located across stages and validated
- All evaluation areas checked (file_structure, frontmatter, achievement, effects, contributions, actors, dependencies, placeholders)
- Given-When-Then format validated for observable effects
- Validation status clearly reported
- If INVALID: failure report created at outcome path
- Workspace indexes synced to reflect current validation status
</success_criteria>
