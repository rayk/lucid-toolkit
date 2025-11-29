---
description: Validate workspace configuration files and cross-references
argument-hint: [--schemas | --refs | --all]
---

<objective>
Deep validation of workspace configuration, schemas, @ references, and structural integrity.

This command:
- Validates JSON schemas for all tracking files
- Checks @ file references in instruction files
- Verifies project map compliance
- Reports validation errors with file:line references
</objective>

<context>
Workspace home: @../../shared/workspaces/{workspace-id}/
Schemas: @schemas/workspace_schema.json, @schemas/project_map_schema.json
</context>

<process>
## Validation Modes

### Schema Validation (--schemas)
Validates all tracking files against their schemas:

1. **Workspace Files**
   - `workspaces.json` against `workspaces_schema.json`
   - `project_map.json` against `project_map_schema.json`

2. **Capability Files**
   - `capability_track.json` against `capability_track_schema.json`
   - `capability_summary.json` against schema

3. **Outcome Files**
   - `outcome_track.json` against `outcome_track_schema.json`
   - `outcome_summary.json` against schema

4. **Project Map Validation**
   Required fields per project:
   - name, path, description
   - technology (languages[], frameworks[], buildTool)
   - keyDirectories (source, tests, documentation, configuration, build)
   - entryPointFiles (name, path, purpose)

### Reference Validation (--refs)
Validates all @ file references:

1. **Scan Files**
   - Commands (*.md)
   - Skills (*/SKILL.md)
   - Agents (*.md)

2. **Resolve References**
   For each `@path/to/file`:
   - Check workspace root + path
   - Check .claude/ + path
   - Check for SKILL.md or README.md variants
   - Skip schema.org keywords (type, return, etc.)

3. **Validate Shared Module References**
   - Check `@shared/status-line/` module is configured in project
   - Verify module path exists: `shared/status-line/`
   - Verify entry point exists: `shared/status-line/status_line.py`
   - Report missing modules with recommendation to run `/workspace:init`

4. **Report Broken References**
   ```
   path/to/file:line - @broken/reference
   ```

### Full Validation (--all or default)
Runs both schema and reference validation.
</process>

<output_format>
## TOON Format (for machine consumption)

```toon
@type: Action
name: workspace-validation
actionStatus: {CompletedActionStatus|FailedActionStatus}

schemaResults[N]{file,actionStatus,error}:
workspaces.json,CompletedActionStatus,-
project_map.json,CompletedActionStatus,-
capability_track.json,FailedActionStatus,missing purpose

brokenRefs[N]{file,line,ref}:
commands/create.md,15,@templates/missing.md
skills/analyze/SKILL.md,42,@research/nonexistent.md
```

**Use TOON when:**
- Returning validation results to subagents
- Integrating with CI/CD pipelines
- Automated fix workflows
- Token efficiency is critical

## Markdown Schema Validation Results
```
Schema Validation:
✓ workspaces.json - valid
✓ project_map.json - valid
✗ capabilities/auth/capability_track.json - missing required field 'purpose'
✓ outcomes/queued/001-setup/outcome_track.json - valid

Errors: 1
- capabilities/auth/capability_track.json:
  - Missing required property: purpose
  - Invalid maturity value: must be 0-100
```

## Markdown Reference Validation Results
```
Reference Validation:
Checked 24 files

Found 2 broken references:
  commands/create.md:15 - @templates/missing-template.md
  skills/analyze/SKILL.md:42 - @research/nonexistent.md

Valid references: 87
Broken references: 2
```

## Combined Report
```
Workspace Validation Report
===========================

Schema Validation: 1 error
Reference Validation: 2 broken

Total Issues: 3

Recommendations:
- Add 'purpose' field to auth capability
- Update or remove broken @ references
```
</output_format>

<validation_rules>
## Project Map Required Fields

| Field | Type | Description |
|-------|------|-------------|
| name | string | Project name |
| path | string | Relative path |
| description | string | Purpose |
| technology.languages | array | Programming languages |
| technology.frameworks | array | Frameworks used |
| technology.buildTool | string | Build system |
| keyDirectories | object | Standard directories |
| entryPointFiles | array | Key entry files |

## Naming Patterns

| Entity | Pattern | Example |
|--------|---------|---------|
| Capability ID | `^[a-z0-9]+(-[a-z0-9]+)*$` | auth-system |
| Outcome Dir | `^[0-9]+-[a-z0-9-]+$` | 001-setup-auth |
| Child Outcome | `^[0-9]+\.[0-9]+-[a-z0-9-]+$` | 001.1-oauth |
| Module ID | `^[a-z][a-z0-9_]*$` | neo4j_service |
</validation_rules>

<success_criteria>
- All requested validations executed
- Errors reported with file:line references
- `@shared/status-line/` module configuration validated
- Actionable recommendations provided
- Exit code reflects validation status (0=pass, 1=errors)
</success_criteria>

