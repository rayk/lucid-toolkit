---
description: Add a project to the workspace and update project-map.json
argument-hint: [project-path or git-url]
---

<objective>
Add an existing project to this workspace. Updates `workspace.json` with project reference and `project-map.json` with comprehensive source mapping (directories, modules, entry points).

This command:
- Adds project entry to `workspace.json` with path and metadata
- Maps project source structure in `project-map.json` (src, tests, modules)
- Creates `.claude/workspace.json` in the project with indexes to workspace artifacts
- Syncs current capability/outcome indexes to the project
</objective>

<context>
Workspace config: @workspace.json
Project map: @project-map.json
Workspace schema: @schemas/workspace_schema.json
Project workspace schema: @schemas/project_workspace_schema.json
Project map schema: @schemas/project_map_schema.json
</context>

<process>
1. **Validate Workspace Exists**:
   - Check for `workspace.json` in current directory
   - If not found: Error - must run from workspace root or use `workspace:init` first
   - Load workspace configuration

2. **Resolve Project Source**:
   - If $ARGUMENTS is a URL (git://, https://, git@):
     - Ask user for target directory (default: sibling to workspace)
     - Clone repository
     - Use cloned path as project path
   - If $ARGUMENTS is a relative/absolute path:
     - Resolve to absolute path
     - Validate path exists and is a directory
     - Verify it's a git repository or has project files
   - If no $ARGUMENTS:
     - Prompt user for project path or URL

3. **Detect Project Type**:
   - Scan for project indicators:
     - `package.json` → Node.js/TypeScript
     - `pyproject.toml` / `setup.py` → Python
     - `Cargo.toml` → Rust
     - `go.mod` → Go
     - `pubspec.yaml` → Flutter/Dart
   - Identify language, framework, build tool
   - Classify: library | service | application | tool | docs | config

4. **Gather Project Metadata**:
   - **id**: kebab-case identifier (default: directory name)
   - **name**: Human-readable name
   - **description**: Brief project purpose
   - **role**: primary | supporting | shared
   - **language**: Primary language
   - **framework**: Primary framework (if applicable)
   - **gitRemote**: Git remote URL
   - **defaultBranch**: main/master

5. **Map Project Structure**:
   - Identify key directories:
     - **source**: src/, lib/, app/
     - **tests**: tests/, test/, __tests__/
     - **docs**: docs/, documentation/
     - **config**: config/, .config/
     - **build**: dist/, build/, out/
   - Discover modules (major packages/services):
     - Scan source directory for subdirectories
     - Identify module type: app, service, library, package, data, config
     - Find entry points (main files, exported classes/functions)
   - Create entry point files list:
     - README.md
     - package.json / pyproject.toml / Cargo.toml
     - ARCHITECTURE.md (if exists)

6. **Update workspace.json**:
   Add to `projects` array:
   ```json
   {
     "id": "{project-id}",
     "name": "{Project Name}",
     "path": "{relative-path-from-workspace}",
     "absolutePath": "{absolute-path}",
     "type": "{library|service|application|tool|docs|config}",
     "role": "{primary|supporting|shared}",
     "description": "{description}",
     "language": "{language}",
     "framework": "{framework}",
     "gitRemote": "{git-url}",
     "defaultBranch": "main",
     "status": "active"
   }
   ```

7. **Update project-map.json**:
   Add to `projects` array:
   ```json
   {
     "name": "{project-name}",
     "path": "{relative-path}",
     "description": "{description}",
     "technology": {
       "languages": ["{language}"],
       "frameworks": ["{framework}"],
       "buildTool": "{npm|uv|cargo|go}"
     },
     "keyDirectories": {
       "source": "{path}/src",
       "tests": "{path}/tests",
       "documentation": "{path}/docs",
       "configuration": "{path}/config"
     },
     "entryPointFiles": [
       {"name": "README.md", "path": "README.md", "purpose": "Project overview"},
       {"name": "pyproject.toml", "path": "pyproject.toml", "purpose": "Dependencies and build"}
     ],
     "modules": [
       {
         "id": "{module_id}",
         "name": "{Module Name}",
         "path": "{relative-to-project}",
         "type": "{service|library|package}",
         "description": "{what it does}",
         "entryPoints": [
           {"name": "{ClassName}", "file": "{file.py}", "symbol": "{ClassName}"}
         ],
         "status": "active"
       }
     ],
     "scope": "{capability-domain}",
     "status": "active"
   }
   ```

8. **Create Project's workspace.json**:
   Create `.claude/workspace.json` in the added project:
   ```json
   {
     "$schema": "{workspace-path}/schemas/project_workspace_schema.json",
     "projectId": "{project-id}",
     "projectName": "{Project Name}",
     "workspaceId": "{workspace-id}",
     "workspaceName": "{Workspace Name}",
     "workspacePath": "{relative-path-to-workspace}",
     "workspaceAbsolutePath": "{absolute-path-to-workspace}",
     "indexes": {
       "capabilities": {
         "path": "capabilities/",
         "description": "Strategic capabilities with maturity tracking",
         "summaryFile": "status/capability_summary.json",
         "count": {N},
         "domains": ["{domain1}", "{domain2}"]
       },
       "outcomes": {
         "path": "outcomes/",
         "description": "Work units organized by state",
         "summaryFile": "status/outcome_summary.json",
         "states": {...},
         "counts": {...}
       },
       "plans": {
         "path": "plans/",
         "description": "Strategic roadmaps and execution plans",
         "items": []
       },
       "research": {
         "path": "research/",
         "description": "Domain research and technology evaluation",
         "items": []
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
       "syncedBy": "workspace:add"
     },
     "metadata": {
       "joinedAt": "{ISO 8601}",
       "schemaVersion": "1.0.0"
     }
   }
   ```

9. **Update IntelliJ (Optional)**:
   - If workspace has `.idea/modules.xml`, add project module reference
   - Inform user they can also add via IntelliJ UI
</process>

<success_criteria>
- Project added to workspace.json with correct path
- Project mapped in project-map.json with directories and modules
- `.claude/workspace.json` created in project with indexes
- Indexes populated with current capability/outcome summaries
- All sibling projects listed in project's workspace.json
- No duplicate project entries
- Schema validation passes for all files
</success_criteria>

<output_format>
## TOON Format

```toon
@type: CreateAction
actionStatus: CompletedActionStatus
@id: project/{project-id}
name: {project-name}
x-type: {library|service|application}
x-role: {primary|supporting|shared}
x-language: {language}
path: {relative-path}
result: Project added to workspace

modulesDiscovered[N]: {mod1},{mod2}
filesUpdated[2]: workspace.json,project-map.json
filesCreated[1]: {project-path}/.claude/workspace.json
```
</output_format>

<output>
Updated files:
- `workspace.json` - Added project entry
- `project-map.json` - Added source mapping

Created files:
- `{project-path}/.claude/workspace.json` - Project's workspace config with indexes

Summary:
- Project: {name} ({id})
- Type: {type} | Role: {role}
- Language: {language} | Framework: {framework}
- Path: {relative-path}
- Modules discovered: {N}
- Workspace now has {total} projects
</output>

<verification>
Before completing, verify:
- [ ] workspace.json exists in current directory
- [ ] Project path resolved and accessible
- [ ] Project not already in workspace
- [ ] Project type and language detected
- [ ] Modules discovered and mapped
- [ ] workspace.json updated with project entry
- [ ] project-map.json updated with source mapping
- [ ] Project's .claude/workspace.json created
- [ ] Indexes synced to project's workspace.json
- [ ] Schema validation passes
</verification>
