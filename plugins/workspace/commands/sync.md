---
description: Synchronize workspace indexes to all member projects
argument-hint: [--project <id>] [--dry-run]
---

<objective>
Synchronize capability, outcome, plan, and research indexes from the workspace to all member projects' `.claude/workspace.json` files. Ensures all projects have current information about workspace artifacts.

This command:
- Reads current state from workspace status files
- Updates indexes in each project's `.claude/workspace.json`
- Updates the projects list in each project (for new/removed projects)
- Reports sync status and any issues
</objective>

<context>
Workspace config: @workspace.json
Capability summary: @status/capability_summary.json
Outcome summary: @status/outcome_summary.json
Project workspace schema: @schemas/project_workspace_schema.json
</context>

<process>
1. **Validate Workspace**:
   - Check for `workspace.json` in current directory
   - If not found: Error - must run from workspace root
   - Load workspace configuration

2. **Parse Options**:
   - `--project <id>`: Only sync to specified project
   - `--dry-run`: Show what would be synced without writing

3. **Gather Current State**:
   - Read `status/capability_summary.json`:
     - Extract total count
     - Extract domain list
     - Extract maturity metrics
   - Read `status/outcome_summary.json`:
     - Extract counts by state
     - Extract total count
   - Scan `plans/` directory:
     - List plan files with descriptions
   - Scan `research/` directory:
     - List research files with domains
   - Read `status/actor_summary.json`:
     - Extract actor count
     - Extract types and domains

4. **Build Index Updates**:
   ```json
   {
     "capabilities": {
       "path": "capabilities/",
       "description": "Strategic capabilities organized by domain with maturity tracking. Each capability has capability_track.json.",
       "summaryFile": "status/capability_summary.json",
       "count": {totalCapabilities},
       "domains": ["compliance", "financial", "governance", ...],
       "metrics": {
         "averageMaturity": {N}%,
         "activeCount": {N},
         "stalledCount": {N}
       }
     },
     "outcomes": {
       "path": "outcomes/",
       "description": "Work units organized by state. Each outcome has outcome_track.json with tasks and capability contributions.",
       "summaryFile": "status/outcome_summary.json",
       "states": {
         "queued": "outcomes/queued/",
         "ready": "outcomes/ready/",
         "in-progress": "outcomes/in-progress/",
         "blocked": "outcomes/blocked/",
         "completed": "outcomes/completed/"
       },
       "counts": {
         "queued": {N},
         "ready": {N},
         "inProgress": {N},
         "blocked": {N},
         "completed": {N},
         "total": {N}
       }
     },
     "plans": {
       "path": "plans/",
       "description": "Strategic roadmaps and execution plans guiding outcome execution.",
       "items": [
         {"name": "roadmap-2025.md", "path": "plans/roadmap-2025.md", "description": "...", "type": "roadmap"}
       ]
     },
     "research": {
       "path": "research/",
       "description": "Domain research and technology evaluation informing capability design.",
       "items": [
         {"name": "strata-legislation.md", "path": "research/strata-legislation.md", "description": "...", "domain": "compliance"}
       ]
     },
     "status": {
       "path": "status/",
       "description": "Summary indexes for quick artifact lookup.",
       "files": [
         {"name": "capability_summary.json", "path": "status/capability_summary.json", "description": "All capabilities index with maturity"},
         {"name": "outcome_summary.json", "path": "status/outcome_summary.json", "description": "All outcomes index with progress"},
         {"name": "actor_summary.json", "path": "status/actor_summary.json", "description": "Stakeholder registry"}
       ]
     }
   }
   ```

5. **Build Projects List**:
   - From workspace.json projects array
   - Include workspace itself with `isWorkspace: true`
   - Calculate relative paths from each project's perspective

6. **Sync to Each Project**:
   For each project in workspace.json (or just --project if specified):
   - Calculate relative path from project to workspace
   - Load existing `.claude/workspace.json`
   - Update `indexes` with current state
   - Update `projects` list with relative paths
   - Update `sync.lastSync` timestamp
   - Update `sync.syncedBy` to "workspace:sync"
   - Write updated file
   - Validate against schema

7. **Handle Missing Projects**:
   - If project doesn't have `.claude/workspace.json`:
     - Create it (same as `/workspace:join`)
   - If project directory doesn't exist:
     - Warn and skip

8. **Report Results**:
   - List projects synced
   - Show any errors or warnings
   - Display sync timestamp
</process>

<success_criteria>
- All project `.claude/workspace.json` files updated
- Indexes reflect current workspace state
- Projects lists updated with any new/removed projects
- sync.lastSync timestamps updated
- Schema validation passes for all files
</success_criteria>

<output_format>
## TOON Format

```toon
@type: SyncAction
actionStatus: CompletedActionStatus
@id: workspace/{workspace-id}
x-projectsSynced: {N}
x-timestamp: {ISO 8601}
result: Indexes synchronized

capabilities: {count} across {domains} domains
outcomes: {total} ({queued}q/{ready}r/{inProgress}ip/{blocked}b/{completed}c)
plans: {count}
research: {count}

projectsSynced[N]: {proj1},{proj2},{proj3}
projectsSkipped[N]: {reason}
filesUpdated[N]: {list}
```
</output_format>

<output>
## Sync Complete

**Timestamp**: {ISO 8601}

### Indexes Synced

| Index | Count | Details |
|-------|-------|---------|
| Capabilities | {N} | {M} domains, {X}% avg maturity |
| Outcomes | {N} | {q} queued, {ip} in-progress, {c} completed |
| Plans | {N} | {types} |
| Research | {N} | {domains} |

### Projects Updated

| Project | Status | Path |
|---------|--------|------|
| {name} | ✓ Synced | {path} |
| {name} | ⚠ Created | {path} (new .claude/workspace.json) |
| {name} | ✗ Skipped | {reason} |

### Summary
- {N} projects synced successfully
- {N} projects skipped
- {N} workspace.json files created
</output>

<verification>
Before completing, verify:
- [ ] Running from workspace root
- [ ] Workspace.json loaded successfully
- [ ] Status files read (capability_summary, outcome_summary)
- [ ] Plans and research directories scanned
- [ ] Each project's workspace.json updated
- [ ] sync.lastSync timestamps set
- [ ] All files validate against schemas
</verification>
