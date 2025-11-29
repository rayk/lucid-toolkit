---
description: List all projects in the current workspace
argument-hint: [--verbose | --json]
---

<objective>
Display all projects registered in the current workspace with their metadata and status.

This command provides:
- Quick overview of workspace projects
- Project types and roles
- Dependency relationships
- Optional detailed or JSON output
</objective>

<context>
Workspace file: @workspace.json
</context>

<process>
1. **Load Workspace Configuration**:
   - Find `workspace.json` in current directory or parent directories
   - If not found: Inform user no workspace is configured
   - Parse workspace configuration

2. **Determine Output Format**:
   - If $ARGUMENTS contains `--json`: Output raw JSON
   - If $ARGUMENTS contains `--verbose`: Output detailed view
   - Otherwise: Output summary table

3. **Gather Project Status** (for verbose mode):
   - Check if each project path exists
   - Detect git status if applicable
   - Note any missing or inaccessible projects

4. **Display Projects**:

   **Summary Format (default)**:
   ```
   Workspace: [name] ([type])

   Projects ([count]):
   ┌─────────────────┬──────────┬───────────┬─────────┐
   │ Name            │ Type     │ Role      │ Path    │
   ├─────────────────┼──────────┼───────────┼─────────┤
   │ project-name    │ service  │ primary   │ ./path  │
   └─────────────────┴──────────┴───────────┴─────────┘
   ```

   **Verbose Format**:
   ```
   Workspace: [name]
   Description: [description]
   Type: [type]

   Projects:

   1. [project-name]
      Path: [path]
      Type: [type] | Role: [role]
      Description: [description]
      Tags: [tags]
      Dependencies: [list or "none"]
      Dependents: [list or "none"]
      Status: [accessible | missing | git-dirty]
   ```

   **JSON Format**:
   Output workspace.json content directly

5. **Show Dependency Graph** (verbose only):
   - Visual representation of inter-project dependencies
   - Highlight circular dependencies if any
</process>

<success_criteria>
- Workspace configuration loaded successfully
- All projects listed with requested detail level
- Output format matches user request
- Missing projects clearly indicated
- Dependency relationships shown (verbose mode)
</success_criteria>

<output_format>
## TOON Format (for machine consumption)

```toon
@type: ItemList
@id: workspace/{workspace-id}
name: {workspace-name}
x-type: {monorepo|multi-repo|hybrid}
numberOfItems: {count}

itemListElement[N]{name,@type,x-role,path|tab}:
project-1	service	primary	./path/to/project-1
project-2	library	supporting	./path/to/project-2
project-3	application	primary	./path/to/project-3
```

**Use TOON when:**
- Returning project list to subagents
- Providing data for cross-plugin consumption
- Token efficiency is critical

**Use markdown when:**
- Final user-facing output
- Verbose mode with detailed descriptions
- Interactive selection required
</output_format>

<output>
Displayed to user:
- Workspace name and type
- Project list in requested format
- Dependency graph (if verbose)
- Any warnings about missing projects
</output>

