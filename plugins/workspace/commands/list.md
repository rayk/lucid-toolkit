---
description: List all projects in the current workspace with sync status
argument-hint: [--verbose | --json]
---

<objective>
Display all projects registered in the workspace with their metadata, sync status, and module information.

This command provides:
- Quick overview of workspace projects from workspace.json
- Project types, roles, and languages
- Sync status (whether project's .claude/workspace.json is up-to-date)
- Module counts from project-map.json
- Optional detailed or JSON output
</objective>

<context>
Workspace file: @workspace.json
Project map: @project-map.json
</context>

<process>
1. **Load Workspace Configuration**:
   - Check for `workspace.json` in current directory
   - If not found and in a project: Check `.claude/workspace.json` for workspace path
   - If still not found: Error - not in a workspace context
   - Parse workspace.json and project-map.json

2. **Determine Output Format**:
   - If $ARGUMENTS contains `--json`: Output raw JSON
   - If $ARGUMENTS contains `--verbose`: Output detailed view
   - Otherwise: Output summary table

3. **Gather Project Status**:
   For each project in workspace.json:
   - Check if project directory exists
   - Check if `.claude/workspace.json` exists
   - Compare sync.lastSync with workspace status file timestamps
   - Count modules from project-map.json
   - Get git status (clean/dirty/ahead/behind)

4. **Display Projects**:

   **Summary Format (default)**:
   ```
   Workspace: {name} ({type})
   Root: {rootPath}

   Projects ({count}):
   ┌─────────────────┬──────────┬───────────┬──────────┬────────┬─────────┐
   │ Name            │ Type     │ Role      │ Language │ Sync   │ Modules │
   ├─────────────────┼──────────┼───────────┼──────────┼────────┼─────────┤
   │ lucid-knowledge │ library  │ primary   │ Python   │ ✓      │ 4       │
   │ lucid-toolkit   │ tool     │ supporting│ Markdown │ ⚠ stale│ 2       │
   └─────────────────┴──────────┴───────────┴──────────┴────────┴─────────┘

   Artifacts:
   - Capabilities: {N} ({M} domains)
   - Outcomes: {N} ({queued} queued, {in-progress} in-progress)
   - Plans: {N}
   - Research: {N}
   ```

   **Verbose Format**:
   ```
   Workspace: {name}
   ID: {id}
   Description: {description}
   Type: {type}
   Root: {rootPath}

   Directories:
   - capabilities/  - Strategic capabilities
   - outcomes/      - Work units by state
   - plans/         - Roadmaps and execution plans
   - research/      - Domain research
   - status/        - Summary indexes

   Projects ({count}):

   1. {project-name}
      ID: {id}
      Path: {path} ({absolutePath})
      Type: {type} | Role: {role}
      Language: {language} | Framework: {framework}
      Description: {description}
      Git: {gitRemote} ({defaultBranch})
      Sync Status: {✓ synced | ⚠ stale (last: {date}) | ✗ missing}
      Modules ({N}):
        - {module_id}: {description} ({type})
        - {module_id}: {description} ({type})
      Status: {active | archived | deprecated}

   Workspace Artifacts:
   - Capabilities: {N} across {domains}
     - Average maturity: {N}%
     - Active: {N}, Stalled: {N}
   - Outcomes: {N} total
     - Queued: {N}, In-progress: {N}, Completed: {N}
   - Plans: {N} items
   - Research: {N} documents
   ```

   **JSON Format**:
   Merge workspace.json with status information:
   ```json
   {
     "workspace": {...},
     "projects": [
       {
         ...projectFromConfig,
         "syncStatus": "synced|stale|missing",
         "lastSync": "ISO 8601",
         "moduleCount": N,
         "gitStatus": "clean|dirty"
       }
     ],
     "artifacts": {
       "capabilities": {...},
       "outcomes": {...},
       "plans": {...},
       "research": {...}
     }
   }
   ```
</process>

<success_criteria>
- Workspace configuration loaded successfully
- All projects listed with sync status
- Module counts accurate from project-map.json
- Artifact summaries from status files
- Output format matches user request
- Missing or stale projects clearly indicated
</success_criteria>

<output_format>
## TOON Format (for machine consumption)

```toon
@type: ItemList
@id: workspace/{workspace-id}
name: {workspace-name}
x-type: {monorepo|multi-repo|hybrid}
x-rootPath: {absolute-path}
numberOfItems: {count}

itemListElement[N]{name,@type,x-role,x-language,x-sync,x-modules,path|tab}:
lucid-knowledge	library	primary	Python	synced	4	../lucid-knowledge
lucid-toolkit	tool	supporting	Markdown	stale	2	../lucid-toolkit

artifacts{name,count}:
capabilities	31
outcomes	11
plans	0
research	0
```

**Use TOON when:**
- Returning project list to subagents
- Token efficiency critical

**Use markdown when:**
- User-facing output
- Verbose mode
</output_format>

<output>
Displayed to user:
- Workspace identity (name, type, root)
- Project table with sync status
- Artifact counts
- Any warnings about missing/stale projects
</output>
