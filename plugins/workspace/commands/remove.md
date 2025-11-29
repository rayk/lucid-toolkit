---
description: Remove a project from the current workspace
argument-hint: [project-name]
---

<objective>
Remove a project from the workspace configuration without deleting the actual project files.

This command:
- Removes project entry from `workspace.json`
- Updates dependency mappings
- Preserves the actual project directory
</objective>

<context>
Workspace file: @workspace.json
Schema validation: @schemas/workspace_schema.json
</context>

<process>
1. **Validate Workspace Exists**:
   - Check for `workspace.json` in current directory or parent directories
   - If not found: Inform user no workspace is configured
   - Load existing workspace configuration

2. **Identify Project to Remove**:
   - If $ARGUMENTS provided: Match against project names
   - If no match or no $ARGUMENTS: Present list of workspace projects for selection
   - Confirm project selection with user

3. **Check Dependencies**:
   - Identify projects that depend on the project being removed
   - If dependencies exist:
     - Warn user about dependent projects
     - List affected projects
     - Ask for confirmation to proceed

4. **Remove Project**:
   - Remove project entry from workspace.json
   - Update dependency graph (remove references)
   - Recalculate build order
   - Validate updated configuration against schema

5. **Preserve Project Files**:
   - Do NOT delete project directory
   - Inform user the project files remain on disk
   - Suggest `rm -rf` command if user wants to delete files
</process>

<success_criteria>
- Project removed from workspace.json
- Dependency graph updated correctly
- Build order recalculated
- Project files NOT deleted
- User informed of remaining files
- Schema validation passes
</success_criteria>

<output_format>
## TOON Format (for machine consumption)

```toon
@type: Action
actionStatus: CompletedActionStatus
@id: project/{project-name}
name: remove-project
object: {project-name}
result: Project removed from workspace (files preserved)

affectedDependents[N]: {dep1},{dep2}
filesUpdated[1]: workspace.json
x-filesPreserved: true
```

**Use TOON when:**
- Returning removal results to subagents
- Automated project cleanup workflows
- Token efficiency is critical

**Use markdown when:**
- Final user-facing output with warnings
- Interactive removal confirmation
</output_format>

<output>
Updated file:
- `workspace.json` - Updated with project removed

Summary displayed:
- Removed project name
- Updated project count
- Warning about any broken dependencies
- Note about preserved project files
</output>

<verification>
Before completing, verify:
- [ ] Project identified correctly
- [ ] User confirmed removal (especially if dependencies exist)
- [ ] Project entry removed from workspace.json
- [ ] Dependency references cleaned up
- [ ] Build order updated
- [ ] Project directory NOT deleted
- [ ] workspace.json valid after update
</verification>
