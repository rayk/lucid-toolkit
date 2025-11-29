---
description: Leave the current workspace (removes project's workspace.json)
argument-hint: [--keep-in-workspace]
---

<objective>
Disconnect the current project from its workspace. Removes `.claude/workspace.json` from the project.

By default, also removes the project from workspace.json and project-map.json. Use `--keep-in-workspace` to only remove the local configuration while keeping the project registered in the workspace.
</objective>

<context>
Project workspace config: @.claude/workspace.json
</context>

<process>
1. **Validate Project Connection**:
   - Check for `.claude/workspace.json` in current directory
   - If not found: Error - project not connected to a workspace
   - Load workspace configuration from the file

2. **Confirm Action**:
   - Display workspace being left
   - Show what will be removed
   - Ask for confirmation unless --force flag

3. **Parse Options**:
   - `--keep-in-workspace`: Only remove local config, keep project in workspace
   - Default: Remove from both local and workspace

4. **Remove Local Configuration**:
   - Delete `.claude/workspace.json`
   - Optionally remove `.claude/` if empty

5. **Update Workspace** (unless --keep-in-workspace):
   - Load workspace.json from workspace path
   - Remove project entry from projects array
   - Remove project mapping from project-map.json
   - Update all other projects' workspace.json:
     - Remove this project from their projects arrays
   - Update workspace metadata.updated timestamp

6. **Report Results**:
   - Confirm disconnection
   - Show remaining workspace projects (if applicable)
</process>

<success_criteria>
- `.claude/workspace.json` removed from project
- Project removed from workspace.json (unless --keep-in-workspace)
- Project removed from project-map.json (unless --keep-in-workspace)
- Other projects' workspace.json updated to remove this project
- Workspace remains functional for remaining projects
</success_criteria>

<output_format>
## TOON Format

```toon
@type: LeaveAction
actionStatus: CompletedActionStatus
@id: project/{project-id}
x-workspace: {workspace-id}
x-keepInWorkspace: {true|false}
result: Left workspace

filesDeleted[1]: .claude/workspace.json
filesUpdated[N]: {workspace}/workspace.json,{workspace}/project-map.json,{sibling}/.claude/workspace.json
```
</output_format>

<output>
Removed files:
- `.claude/workspace.json`

Left workspace: {workspace-name}

{If not --keep-in-workspace}:
- Removed from workspace.json
- Removed from project-map.json
- Updated {N} sibling projects

{If --keep-in-workspace}:
- Project still registered in workspace
- Can rejoin with /workspace:join
</output>

<verification>
Before completing, verify:
- [ ] .claude/workspace.json existed
- [ ] User confirmed action
- [ ] .claude/workspace.json deleted
- [ ] Project removed from workspace (unless --keep-in-workspace)
- [ ] Sibling projects updated (unless --keep-in-workspace)
- [ ] Workspace remains valid
</verification>
