---
description: Join an existing workspace (run from a project to connect it to a workspace)
argument-hint: [workspace-path]
---

<objective>
Join an existing workspace from within a project directory. Creates `.claude/workspace.json` in the current project with indexes to workspace artifacts and list of sibling projects.

This is the inverse of `/workspace:add`:
- `/workspace:add` - Run from workspace, add a project TO the workspace
- `/workspace:join` - Run from project, connect the project TO a workspace
</objective>

<context>
Project workspace schema: @schemas/project_workspace_schema.json
Workspace schema: @schemas/workspace_schema.json
</context>

<process>
1. **Validate Current Location**:
   - Confirm running from a project directory (not from a workspace)
   - Check for existing `.claude/workspace.json` to prevent re-joining
   - Verify project has git or project files (pyproject.toml, package.json, etc.)

2. **Resolve Workspace**:
   - If $ARGUMENTS provided: Use as workspace path
   - Otherwise: Search for workspace.json in:
     - Parent directories
     - Sibling directories
     - Present found workspaces for selection
   - Validate workspace.json exists at specified path
   - Load workspace configuration

3. **Calculate Paths**:
   - Compute relative path from project to workspace
   - Compute absolute path to workspace
   - Generate project ID from directory name (kebab-case)

4. **Gather Project Info**:
   - Detect project type (language, framework)
   - Get git remote URL if available
   - Ask user for:
     - Project description
     - Role: primary | supporting | shared

5. **Create .claude/workspace.json**:
   Create `.claude/` directory if needed, then workspace.json:
   ```json
   {
     "$schema": "{workspace-path}/schemas/project_workspace_schema.json",
     "projectId": "{project-id}",
     "projectName": "{Project Name}",
     "workspaceId": "{workspace-id}",
     "workspaceName": "{Workspace Name}",
     "workspacePath": "{relative-path-to-workspace}",
     "workspaceAbsolutePath": "{absolute-path}",
     "indexes": {
       "capabilities": {
         "path": "capabilities/",
         "description": "{read from workspace status}",
         "summaryFile": "status/capability_summary.json",
         "count": {N},
         "domains": [...]
       },
       "outcomes": {
         "path": "outcomes/",
         "description": "{read from workspace status}",
         "summaryFile": "status/outcome_summary.json",
         "states": {...},
         "counts": {...}
       },
       "plans": {
         "path": "plans/",
         "description": "Strategic roadmaps and execution plans",
         "items": [...]
       },
       "research": {
         "path": "research/",
         "description": "Domain research and technology evaluation",
         "items": [...]
       },
       "status": {
         "path": "status/",
         "description": "Summary indexes for quick lookup",
         "files": [...]
       }
     },
     "projects": [
       // All workspace projects including self
     ],
     "projectMap": {
       "path": "project-map.json",
       "resolvePrefix": "{project-id}"
     },
     "sync": {
       "lastSync": "{ISO 8601}",
       "autoSync": true,
       "syncedBy": "workspace:join"
     },
     "metadata": {
       "joinedAt": "{ISO 8601}",
       "schemaVersion": "1.0.0"
     }
   }
   ```

6. **Update Workspace** (if not already registered):
   - Check if project already in workspace.json projects array
   - If not, add project entry to workspace.json
   - Add project mapping to project-map.json
   - Update workspace metadata.updated timestamp

7. **Sync Indexes**:
   - Read capability_summary.json from workspace
   - Read outcome_summary.json from workspace
   - Scan plans/ and research/ directories
   - Populate indexes in project's workspace.json
</process>

<success_criteria>
- `.claude/workspace.json` created in current project
- Indexes populated from workspace status files
- All workspace projects listed in projects array
- Project added to workspace.json if not present
- Project added to project-map.json if not present
- Schema validation passes
</success_criteria>

<output_format>
## TOON Format

```toon
@type: JoinAction
actionStatus: CompletedActionStatus
@id: project/{project-id}
x-workspace: {workspace-id}
x-workspacePath: {relative-path}
result: Joined workspace

indexesSynced[5]: capabilities,outcomes,plans,research,status
projectsDiscovered[N]: {proj1},{proj2}
filesCreated[1]: .claude/workspace.json
filesUpdated[N]: {workspace}/workspace.json,{workspace}/project-map.json
```
</output_format>

<output>
Created files:
- `.claude/workspace.json` - Workspace configuration with indexes

Joined workspace:
- Workspace: {name} ({id})
- Path: {relative-path}

Indexes synced:
- Capabilities: {N} capabilities across {M} domains
- Outcomes: {N} total ({queued} queued, {in-progress} in-progress)
- Plans: {N} items
- Research: {N} items

Sibling projects: {list}
</output>

<verification>
Before completing, verify:
- [ ] Running from project directory (not workspace)
- [ ] Workspace.json found at specified path
- [ ] .claude/workspace.json created
- [ ] Indexes populated from workspace
- [ ] All workspace projects in projects array
- [ ] Project registered in workspace.json
- [ ] Project mapped in project-map.json
- [ ] Schema validation passes
</verification>
