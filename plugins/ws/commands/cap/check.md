---
description: Validate a capability statement against workspace standards using capability-checker agent
argument-hint: <capability-id>
---

<objective>
Validate a capability statement for schema compliance, content quality, and cross-reference integrity using the capability-checker agent. After validation, sync workspace indexes to reflect any status changes.

This ensures capability statements meet workspace standards before being used in planning or execution.
</objective>

<context>
Workspace config: @.claude/workspace-info.toon
Capability-checker agent: @agents/capability-checker.md
Output patterns: Follow [output-patterns.md](../../references/output-patterns.md) for consistent formatting
</context>

<process>

## Phase 1: Locate Capability

1. **Read workspace-info.toon** to get `capabilities.path`
2. **Validate capability exists** at `{capabilities.path}/$ARGUMENTS/capability-statement.md`
3. **If not found**: Report error with available capability IDs

## Phase 2: Run Validation

4. **Invoke capability-checker agent**:
   ```
   Task(
     subagent_type="ws:capability-checker",
     prompt="Validate capability at {capabilities.path}/$ARGUMENTS"
   )
   ```

5. **Process validation result**:
   - VALID → Report success
   - NEEDS_ATTENTION → Show warnings, ask if user wants to fix
   - INVALID → Show critical issues, offer to help fix

## Phase 3: Sync Indexes

6. **Update workspace indexes** to reflect validation status:
   ```
   Skill("capability-index-sync")
   ```

</process>

<output_format>
```toon
@type: AssessAction
actionStatus: CompletedActionStatus
@id: $ARGUMENTS

validationStatus: {VALID|NEEDS_ATTENTION|INVALID}
checksPerformed: 7
issues.critical: {count}
issues.warning: {count}
issues.info: {count}

indexesSynced: true
```
</output_format>

<success_criteria>
- Capability located and validated
- All 7 evaluation areas checked (file_structure, frontmatter, content, placeholders, cross-refs, spelling, markdown)
- Validation status clearly reported
- If INVALID: failure report created at capability path
- Workspace indexes synced to reflect current validation status
</success_criteria>
