---
description: Initialize a new workspace project (the workspace IS the project)
argument-hint: [workspace-name]
---

<objective>
Initialize the current directory as an IntelliJ workspace project. The workspace itself IS a project that contains capabilities, outcomes, plans, research, and status directories. Other projects are added to this workspace via `/workspace:add` or IntelliJ's "Add project to workspace".

This command creates:
- `workspace.json` at workspace root - defines workspace identity and lists member projects
- `project-map.json` at workspace root - comprehensive source map for all projects
- Standard directories: capabilities/, outcomes/, plans/, research/, status/, schemas/
- IntelliJ integration via `.idea/` configuration
</objective>

<context>
Workspace schema: @schemas/workspace_schema.json
Project workspace schema: @schemas/project_workspace_schema.json
Project map schema: @schemas/project_map_schema.json
Actor summary schema: @schemas/actor_summary_schema.json
</context>

<process>
1. **Verify Workspace Location**:
   - Confirm current directory should be the workspace project
   - Check for existing `workspace.json` to prevent re-initialization
   - Verify `.idea/` directory exists (IntelliJ project)

2. **Gather Workspace Identity**:
   - If $ARGUMENTS provided: Use as workspace name
   - Otherwise: Ask user for workspace name
   - Generate workspace ID from name: lowercase, hyphenated (pattern: `^[a-z0-9]+(-[a-z0-9]+)*$`)
   - Current directory becomes workspace root

3. **Capture Workspace Metadata**:
   - **Name**: Human-readable workspace name
   - **Description**: Purpose and scope of this workspace
   - **Type**: monorepo | multi-repo | hybrid
   - **Primary Stack**: Main technology focus (e.g., Python, TypeScript)

4. **Create Workspace Directories**:
   ```
   {workspace-root}/
   ├── capabilities/           # Strategic capabilities by domain
   ├── outcomes/               # Work units by state
   │   ├── queued/
   │   ├── ready/
   │   ├── in-progress/
   │   ├── blocked/
   │   └── completed/
   ├── plans/                  # Roadmaps and execution plans
   ├── research/               # Domain research and analysis
   ├── status/                 # Summary indexes
   └── schemas/                # JSON schemas for validation
   ```

5. **Create workspace.json**:
   Write workspace configuration at root:
   ```json
   {
     "$schema": "./schemas/workspace_schema.json",
     "id": "{workspace-id}",
     "name": "{Workspace Name}",
     "description": "{description}",
     "type": "{monorepo|multi-repo|hybrid}",
     "rootPath": "{absolute-path}",
     "primaryStack": "{stack}",
     "directories": {
       "capabilities": "capabilities/",
       "outcomes": "outcomes/",
       "plans": "plans/",
       "research": "research/",
       "status": "status/",
       "schemas": "schemas/"
     },
     "intellij": {
       "ideaDirectory": ".idea/",
       "workspaceFile": ".idea/jb-workspace.xml",
       "modulesFile": ".idea/modules.xml"
     },
     "projects": [],
     "projectMap": "project-map.json",
     "settings": {
       "defaultShell": "/bin/zsh",
       "sharedConfigs": [],
       "syncOnChange": true
     },
     "metadata": {
       "created": "{ISO 8601 timestamp}",
       "updated": "{ISO 8601 timestamp}",
       "createdBy": "{user}",
       "version": "2.0.0"
     }
   }
   ```

6. **Create project-map.json**:
   Initialize project map for source navigation:
   ```json
   {
     "$schema": "./schemas/project_map_schema.json",
     "workspace": {
       "name": "{workspace-name}",
       "rootDirectory": "{absolute-path}",
       "workspaceFile": ".idea/jb-workspace.xml",
       "description": "{description}",
       "lastUpdated": "{ISO 8601 timestamp}"
     },
     "scopes": {
       "workspaceOperations": {
         "capabilities": {
           "directory": "capabilities/",
           "description": "Strategic capabilities organized by domain with maturity tracking"
         },
         "outcomes": {
           "baseDirectory": "outcomes/",
           "subdirectories": {
             "queued": "outcomes/queued/",
             "ready": "outcomes/ready/",
             "inProgress": "outcomes/in-progress/",
             "blocked": "outcomes/blocked/",
             "completed": "outcomes/completed/"
           },
           "description": "Work units organized by execution state"
         },
         "plans": {
           "directory": "plans/",
           "description": "Strategic roadmaps and execution plans"
         },
         "research": {
           "directory": "research/",
           "description": "Domain research and technology evaluation"
         },
         "status": {
           "directory": "status/",
           "description": "Summary indexes for quick artifact lookup",
           "keyFiles": [
             {"name": "capability_summary.json", "purpose": "All capabilities index"},
             {"name": "outcome_summary.json", "purpose": "All outcomes index"},
             {"name": "actor_summary.json", "purpose": "Stakeholder registry"}
           ]
         }
       },
       "configuration": {
         "workspace": [
           {"name": "workspace.json", "purpose": "Workspace configuration"},
           {"name": "project-map.json", "purpose": "Project source mapping"}
         ]
       }
     },
     "projects": [],
     "tempFileManagement": {
       "location": "temp",
       "maxAgeHours": 24,
       "autoCleanup": true
     }
   }
   ```

7. **Initialize Status Files**:
   Create `status/actor_summary.json`:
   ```json
   {
     "$schema": "../schemas/actor_summary_schema.json",
     "version": "1.0.0",
     "actors": [],
     "indexByType": {},
     "indexByDomain": {},
     "summary": {
       "totalActors": 0,
       "actorsByType": {},
       "actorsByDomain": {},
       "lastUpdated": "{ISO 8601 timestamp}"
     }
   }
   ```

8. **Update IntelliJ Configuration**:
   - Verify `.idea/jb-workspace.xml` has workspace flag
   - If missing, create with:
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <project version="4">
     <component name="WorkspaceSettings">
       <option name="workspace" value="true" />
     </component>
   </project>
   ```

9. **Scan for Existing Projects**:
   - Look for sibling directories with git repos
   - Check for IntelliJ module references in `.idea/modules.xml`
   - Present discovered projects to user
   - Offer to add them via `/workspace:add`
</process>

<success_criteria>
- `workspace.json` created at workspace root
- `project-map.json` created at workspace root
- All directories created: capabilities/, outcomes/, plans/, research/, status/, schemas/
- Outcome subdirectories: queued/, ready/, in-progress/, blocked/, completed/
- `status/actor_summary.json` initialized
- IntelliJ workspace flag set in `.idea/jb-workspace.xml`
- Workspace ID follows pattern `^[a-z0-9]+(-[a-z0-9]+)*$`
- Files validate against respective schemas
</success_criteria>

<output_format>
## TOON Format (for machine consumption)

```toon
@type: CreateAction
actionStatus: CompletedActionStatus
@id: workspace/{workspace-id}
name: {workspace-name}
x-type: {monorepo|multi-repo|hybrid}
x-rootPath: {absolute-path}
result: Workspace initialized

directoriesCreated[10]: capabilities/,outcomes/,outcomes/queued/,outcomes/ready/,outcomes/in-progress/,outcomes/blocked/,outcomes/completed/,plans/,research/,status/,schemas/
filesCreated[3]: workspace.json,project-map.json,status/actor_summary.json
```

**Use TOON when:**
- Returning results to subagents
- Automated workspace setup
- Token efficiency needed

**Use markdown when:**
- User-facing output
- Interactive setup
</output_format>

<output>
Directories created:
- `capabilities/` - Strategic capabilities by domain
- `outcomes/` - Work units (queued/, ready/, in-progress/, blocked/, completed/)
- `plans/` - Roadmaps and execution plans
- `research/` - Domain research and analysis
- `status/` - Summary indexes
- `schemas/` - JSON validation schemas

Files created:
- `workspace.json` - Workspace configuration
- `project-map.json` - Project source mapping
- `status/actor_summary.json` - Empty stakeholder registry

Summary:
- Workspace: {name} ({id})
- Type: {monorepo|multi-repo|hybrid}
- Root: {absolute-path}
- Projects: 0 (use /workspace:add to add projects)
</output>

<verification>
Before completing, verify:
- [ ] Current directory confirmed as workspace location
- [ ] workspace.json created with valid schema reference
- [ ] project-map.json created with valid schema reference
- [ ] All directories created and accessible
- [ ] status/actor_summary.json initialized
- [ ] IntelliJ .idea/jb-workspace.xml has workspace flag
- [ ] Workspace ID is valid format
- [ ] Schema validation passes for all JSON files
</verification>
