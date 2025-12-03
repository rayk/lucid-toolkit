---
description: Edit an existing capability statement
argument-hint: <capability-id> [--field <field-name>]
---

<objective>
Modify an existing capability statement while maintaining YAML frontmatter integrity and workspace schema compliance.
</objective>

<context>
**Files to Read:**
| Purpose | Path |
|---------|------|
| Workspace config | `.claude/workspace-info.toon` |
| Target capability | `{capabilities.path}/{capability-id}/capability-statement.md` |
</context>

<process>

## Phase 1: Load Capability

1. **Read workspace-info.toon** to get capabilities.path
2. **Validate capability exists** at `{capabilities.path}/{capability-id}/`
3. **Read capability-statement.md** - parse YAML frontmatter and body

## Phase 2: Determine Edit Scope

4. **If `--field` specified**: Focus on that specific field
   - Valid fields: name, type, status, domain, maturity, coreValues, actors, relationships

5. **If no field specified**: Ask user what to modify
   - Present current values for context
   - Allow multiple field edits in one session

## Phase 3: Apply Edits

6. **For YAML frontmatter fields**:
   - Validate new values against schema constraints
   - Actor IDs must be kebab-case
   - Maturity values 0-100
   - Status: active | deprecated | planned

7. **For markdown body sections**:
   - Maintain section structure
   - No TBD/TODO placeholders

8. **Save updated capability-statement.md**

## Phase 4: Validate

9. **Run capability-checker**:
   ```
   Task(
     subagent_type="ws:capability-checker",
     prompt="Validate capability at {path}"
   )
   ```

</process>

<output_format>
```toon
@type: UpdateAction
actionStatus: CompletedActionStatus
@id: {capability-id}
result: Updated capability

fieldsModified[N]: {field1},{field2}
validationStatus: VALID
```
</output_format>

<epilogue>
After successful capability edit, sync workspace indexes:

```
Skill("capability-index-sync")
```

This ensures capabilities-info.toon and workspace-info.toon reflect the changes.
</epilogue>
