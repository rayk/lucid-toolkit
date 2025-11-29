---
description: Add a project to the current workspace
argument-hint: [project-path or git-url]
---

<objective>
Add an existing project or repository to the current workspace configuration.

This command:
- Registers a new project in `workspace.json`
- Configures project metadata and role
- Updates inter-project dependency mappings
- Optionally clones remote repositories
</objective>

<context>
Workspace registry: @../../shared/workspaces/workspaces.json
Project config: @.lucid/workspace.json (if local mode)
Schema validation: @schemas/workspace_schema.json
</context>

<process>
1. **Validate Workspace Exists**:
   - Check for `workspace.json` in current directory or parent directories
   - If not found: Prompt user to run `workspace:init` first
   - Load existing workspace configuration

2. **Resolve Project Source**:
   - If $ARGUMENTS is a URL (git://, https://, git@):
     - Ask user for target directory name
     - Clone repository to workspace
     - Use cloned path as project path
   - If $ARGUMENTS is a path:
     - Validate path exists and is a directory
     - Check if it's a valid project (has recognizable project files)
   - If no $ARGUMENTS:
     - Prompt user for project path or URL

3. **Detect Project Type**:
   - Scan for project indicators:
     - `package.json` → Node.js/JavaScript
     - `pyproject.toml` / `setup.py` → Python
     - `Cargo.toml` → Rust
     - `go.mod` → Go
     - `pom.xml` / `build.gradle` → Java
     - `*.csproj` → .NET
   - Identify project structure type: library | service | application | tool | docs

4. **Gather Project Metadata**:
   - **Name**: Project identifier (default: directory name)
   - **Description**: Brief project purpose
   - **Role**: primary | supporting | shared
   - **Tags**: Categorization labels

5. **Map Dependencies**:
   - Check if project depends on other workspace projects
   - Check if other projects depend on this one
   - Update dependency graph in workspace.json

6. **Update Workspace Configuration**:
   - Add project entry to `workspace.json`
   - Recalculate build order if dependencies changed
   - Validate against schema
   - Save updated configuration
</process>

<success_criteria>
- Project successfully added to workspace.json
- Project path is valid and accessible
- No duplicate project entries
- Dependencies correctly mapped
- Schema validation passes
</success_criteria>

<output_format>
## TOON Format (for machine consumption)

```toon
@type: CreateAction
actionStatus: CompletedActionStatus
@id: project/{project-name}
name: {project-name}
x-type: {library|service|application|tool|docs}
x-role: {primary|supporting|shared}
path: {relative-path}
result: Project added to workspace

dependenciesDiscovered[N]: {dep1},{dep2}
dependentsDiscovered[N]: {dependent1}
filesUpdated[1]: workspace.json
```

**Use TOON when:**
- Returning project addition results to subagents
- Automated project onboarding workflows
- Token efficiency is critical

**Use markdown when:**
- Final user-facing output with detailed setup info
- Interactive project discovery process
</output_format>

<output>
Updated file:
- `workspace.json` - Updated with new project entry

Summary displayed:
- Project name and path
- Detected project type
- Dependency relationships discovered
- Updated project count in workspace
</output>

<verification>
Before completing, verify:
- [ ] Workspace configuration loaded successfully
- [ ] Project path resolved and valid
- [ ] Project not already in workspace
- [ ] Project metadata captured correctly
- [ ] Dependencies mapped (if any)
- [ ] workspace.json updated and valid
</verification>
