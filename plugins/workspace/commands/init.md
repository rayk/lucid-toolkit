---
description: Initialize a new multi-project workspace configuration
argument-hint: [workspace-name]
---

<objective>
Initialize a new workspace for managing multiple related projects/repositories as a unified development environment.

This command creates:
- A workspace entry in the shared registry (`shared/workspaces/workspaces.json`)
- A workspace home directory (`shared/workspaces/{workspace-id}/`)
- Standard subdirectories for capabilities, outcomes, and status
- Automatic subscription for the current project as admin
</objective>

<context>
Shared registry: @../../shared/workspaces/workspaces.json
Schema validation: @../../shared/workspaces/workspaces_schema.json
Local schema: @schemas/workspace_schema.json
</context>

<process>
1. **Load Shared Registry**:
   - Read `shared/workspaces/workspaces.json`
   - If registry doesn't exist: Initialize with empty workspaces array
   - Check for existing workspace with same ID to prevent duplicates

2. **Gather Workspace Identity**:
   - If $ARGUMENTS provided: Use as workspace name
   - Otherwise: Ask user for workspace name
   - Generate workspace ID following pattern: `^[a-z0-9]+(-[a-z0-9]+)*$`
   - Determine workspace root directory (current directory or specified path)
   - Verify ID is unique in shared registry

3. **Capture Workspace Metadata**:
   - **Name**: Human-readable workspace name
   - **Description**: Purpose and scope of this workspace
   - **Type**: monorepo | multi-repo | hybrid
   - **Primary Language/Stack**: Main technology focus

4. **Configure Initial Projects**:
   - Scan current directory for existing projects (look for package.json, pyproject.toml, Cargo.toml, go.mod, etc.)
   - Present discovered projects to user for confirmation
   - For each project capture:
     - **Path**: Relative path from workspace root
     - **absolutePath**: Resolved absolute path
     - **Name**: Project identifier
     - **Type**: library | service | application | tool | docs
     - **Role**: primary | supporting | shared

5. **Establish Workspace Settings**:
   - **Default shell**: Shell to use for workspace commands
   - **Shared configurations**: List of shared config files (.editorconfig, .prettierrc, etc.)
   - **Build order**: Dependency-based project build sequence (if applicable)

6. **Create Workspace Home Directory**:
   - Create directory: `shared/workspaces/{workspace-id}/`
   - Create subdirectory: `shared/workspaces/{workspace-id}/capabilities/`
   - Create subdirectory: `shared/workspaces/{workspace-id}/outcomes/`
   - Create subdirectory: `shared/workspaces/{workspace-id}/outcomes/queued/`
   - Create subdirectory: `shared/workspaces/{workspace-id}/outcomes/in-progress/`
   - Create subdirectory: `shared/workspaces/{workspace-id}/outcomes/completed/`
   - Create subdirectory: `shared/workspaces/{workspace-id}/status/`

7. **Register in Shared Registry**:
   - Create workspace entry in `shared/workspaces/workspaces.json`:
     ```json
     {
       "id": "{workspace-id}",
       "name": "{Workspace Name}",
       "homePath": "shared/workspaces/{workspace-id}/",
       "rootPath": "{absolute-path-to-code}",
       "directories": {
         "capabilities": "capabilities/",
         "outcomes": "outcomes/",
         "status": "status/"
       },
       "projects": [...],
       "subscribers": [...]
     }
     ```
   - Add current project as first subscriber with admin access
   - Set created/updated timestamps
   - Validate against workspaces_schema.json
   - Save registry

8. **Initialize Cross-References**:
   - Map inter-project dependencies
   - Identify shared modules or libraries
   - Document project boundaries
</process>

<success_criteria>
- Workspace registered in shared registry
- Workspace home directory created at `shared/workspaces/{workspace-id}/`
- Subdirectories created: capabilities/, outcomes/, status/
- Outcomes subdirectories created: queued/, in-progress/, completed/
- Workspace ID follows naming pattern `^[a-z0-9]+(-[a-z0-9]+)*$`
- Workspace ID is unique (no duplicates in registry)
- At least one project registered in workspace
- Current project subscribed as admin
- Workspace type correctly identified
- All discovered projects presented for user review
- Document validates against workspaces_schema.json
</success_criteria>

<output>
Directories created:
- `shared/workspaces/{workspace-id}/`
- `shared/workspaces/{workspace-id}/capabilities/`
- `shared/workspaces/{workspace-id}/outcomes/`
- `shared/workspaces/{workspace-id}/outcomes/queued/`
- `shared/workspaces/{workspace-id}/outcomes/in-progress/`
- `shared/workspaces/{workspace-id}/outcomes/completed/`
- `shared/workspaces/{workspace-id}/status/`

Files updated:
- `shared/workspaces/workspaces.json` - New workspace added to registry

Summary displayed:
- Workspace name, ID, and type
- Workspace home path
- Number of projects registered
- Detected inter-project dependencies
- Subscription confirmation (admin access)
</output>

<verification>
Before completing, verify:
- [ ] Shared registry loaded/created
- [ ] Workspace ID is unique in registry
- [ ] Workspace ID is valid (lowercase, hyphenated)
- [ ] Workspace home directory created
- [ ] All subdirectories created (capabilities, outcomes, status)
- [ ] Outcomes subdirectories created (queued, in-progress, completed)
- [ ] All intended projects are registered with absolute paths
- [ ] Current project added as admin subscriber
- [ ] Project paths are correct and accessible
- [ ] Workspace type matches actual structure
- [ ] Schema validation passes
- [ ] Registry saved successfully
</verification>
