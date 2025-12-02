---
description: Idempotent workspace environment setup, repair, migration, and status reporting
allowed-tools: [Task, Read, Write, AskUserQuestion]
---

<objective>
Manage the workspace environment through an idempotent command that detects current state and performs the appropriate action: setup, repair, migrate, or report.

This command delegates scanning work to parallel subagents to minimize main context usage.
</objective>

<schema_reference>
## Schema / Instance Relationship

**Schemas** are stored in the plugin directory (read-only reference):
```
plugins/ws/templates/data/
├── workspace-info-schema.toon
├── capabilities-info-schema.toon
├── outcomes-info-schema.toon
├── execution-info-schema.toon
├── core-values-schema.toon      (reference data, no instance)
└── actor-registry-schema.toon   (reference data, no instance)
```

**Instances** are ALWAYS saved to `.claude/` in the project where the plugin is installed:
```
{project}/.claude/
├── workspace-info.toon          (main workspace snapshot)
├── capabilities-info.toon       (capabilities index)
├── outcomes-info.toon           (outcomes index)
└── execution-info.toon          (execution tracking)
```

| Data File | Schema (read-only) | Instance (generated) |
|-----------|-------------------|---------------------|
| workspace-info | `plugins/ws/templates/data/workspace-info-schema.toon` | `.claude/workspace-info.toon` |
| capabilities-info | `plugins/ws/templates/data/capabilities-info-schema.toon` | `.claude/capabilities-info.toon` |
| outcomes-info | `plugins/ws/templates/data/outcomes-info-schema.toon` | `.claude/outcomes-info.toon` |
| execution-info | `plugins/ws/templates/data/execution-info-schema.toon` | `.claude/execution-info.toon` |
</schema_reference>

<execution_model>
This command uses a coordinator pattern:
1. **Main context**: State detection, orchestration, user interaction, final output
2. **Subagents**: All scanning and data gathering (runs in parallel, isolated context)

IMPORTANT: Immediately notify user that scanning is starting, then delegate.
</execution_model>

<process>
## Phase 1: Quick State Detection (Main Context)

Notify user immediately:
```
Starting workspace environment scan...
```

Check state with minimal reads:
1. Check if `.claude/workspace-info.toon` exists
2. If exists: read first 10 lines to get version
3. Determine action: setup | repair | migrate | report

| State | Condition | Action |
|-------|-----------|--------|
| **virgin** | File doesn't exist | Run SETUP via subagents |
| **healthy** | File exists, valid, version matches | Run REPORT then CHECK RELATED |
| **outdated** | File exists, version mismatch | Run MIGRATE via subagent |
| **corrupted** | File exists, invalid/incomplete | Run REPAIR via subagent |

## Phase 2: Delegate Workspace Scanning (Parallel Subagents)

For SETUP state, launch these subagents IN PARALLEL using a single message with multiple Task tool calls:

### Subagent 1: Standard Directories Scanner
```
Task(subagent_type="Explore", model="haiku", prompt="""
Scan workspace for standard capability-driven development directories.

Check for these directories at workspace root and report findings:
- capabilities/ → count **/capability_track.json files
- outcomes/ → count **/outcome_track.json files, note stage subdirs
- plans/ → count *.md files
- executions/ → count session logs
- research/ → check if exists
- status/ → check for capability_summary.json, outcome_summary.json

Return TOON format:
```
@type: ItemList
directories{name,exists,itemCount,path|tab}:
capabilities	true	5	./capabilities
outcomes	true	12	./outcomes
...
```
""")
```

### Subagent 2: Project & Technology Scanner
```
Task(subagent_type="Explore", model="haiku", prompt="""
Scan workspace for projects and technology indicators.

1. Check for project-map.json at root or .claude/
2. Scan for technology indicators:
   - package.json → Node.js/TypeScript
   - pyproject.toml, setup.py → Python
   - Cargo.toml → Rust
   - go.mod → Go
   - pom.xml, build.gradle → Java/Kotlin
   - pubspec.yaml → Flutter/Dart
   - *.csproj → .NET

3. Identify .git directories to find project boundaries

Return TOON format:
```
@type: ItemList
hasProjectMap: true|false
projectMapPath: {path}

projects{name,path,technology,gitRoot|tab}:
{name}	{path}	{tech}	{git-root}
...
```
""")
```

### Subagent 3: IDE Configuration Scanner
```
Task(subagent_type="Explore", model="haiku", prompt="""
Scan for IntelliJ IDEA configuration in .idea/ directory.

If .idea/ exists, extract:
1. From modules.xml: module names and paths
2. From misc.xml: SDK name, language level
3. From vcs.xml: VCS mappings
4. List *.iml files found

Return TOON format:
```
@type: SoftwareApplication
ide.name: IntelliJ IDEA
ide.configPath: .idea/
ide.sdkName: {sdk}
ide.languageLevel: {level}

ide.modules{name,path,type|tab}:
{module}	{path}	{type}
...

ide.vcsRoots{directory,vcs|tab}:
{dir}	Git
...
```

If no .idea/ directory, return:
```
@type: SoftwareApplication
ide.name: none
```
""")
```

### Subagent 4: Git & Workspace Metadata
```
Task(subagent_type="Explore", model="haiku", prompt="""
Gather git and workspace metadata.

Execute and report:
1. git rev-parse --short HEAD
2. git remote get-url origin
3. git log -1 --format=%cI (commit timestamp)
4. basename of workspace directory

Return TOON format:
```
@type: Project
workspace.name: {directory-name}
workspace.codeRepository: {remote-url}
workspace.version: {commit-hash}
workspace.dateModified: {commit-timestamp}
```
""")
```

## Phase 3: Merge Results (Main Context)

After all subagents complete:
1. Collect TOON outputs from each subagent
2. Merge into unified workspace-info.toon structure following the schema
3. Write .claude/workspace-info.toon
4. Proceed to Phase 4 to check related data files

## Phase 4: Check and Generate Related Data Files

After workspace-info.toon is established (SETUP, MIGRATE, REPAIR, or HEALTHY states):

### Step 1: Check which related files exist
```
.claude/capabilities-info.toon  → exists? valid?
.claude/outcomes-info.toon      → exists? valid?
.claude/execution-info.toon     → exists? valid?
```

### Step 2: Launch parallel subagents for MISSING files

For each missing file, launch a subagent IN PARALLEL. Use a single message with multiple Task tool calls:

#### Subagent: Capabilities Scanner (if capabilities-info.toon missing)
```
Task(subagent_type="Explore", model="haiku", prompt="""
Scan workspace for capabilities and generate capabilities-info.toon.

Schema: plugins/ws/templates/data/capabilities-info-schema.toon
Output: .claude/capabilities-info.toon

1. Find all capability_track.json files in capabilities/
2. For each capability, extract:
   - identifier, name, description
   - currentMaturity, targetMaturity
   - status (active/deprecated/planned)
   - capabilityType (atomic/composed)
3. Compute summary statistics:
   - totalCapabilities, activeCapabilities, deprecatedCapabilities
   - atomicCapabilities, composedCapabilities
   - averageMaturity
4. Compute maturity distribution (0-29%, 30-59%, 60-79%, 80-100%)
5. Group by domain
6. Identify alerts (stale checks, blocked capabilities)

Write .claude/capabilities-info.toon following the schema.
Return summary: {totalCapabilities, averageMaturity, alertCount}
""")
```

#### Subagent: Outcomes Scanner (if outcomes-info.toon missing)
```
Task(subagent_type="Explore", model="haiku", prompt="""
Scan workspace for outcomes and generate outcomes-info.toon.

Schema: plugins/ws/templates/data/outcomes-info-schema.toon
Output: .claude/outcomes-info.toon

1. Scan each stage directory:
   - outcomes/queued/
   - outcomes/ready/
   - outcomes/in-progress/
   - outcomes/blocked/
   - outcomes/completed/
2. For each outcome, find outcome_track.json and extract:
   - directory, name, stage, priority
   - capabilityContributions
   - parentOutcome (for child outcomes like 005.1-*)
3. Compute capability contributions aggregate
4. Build hierarchy (parent-child relationships)
5. Identify current focus (from in-progress outcomes)
6. List recent activity (modified in last 7 days)

Write .claude/outcomes-info.toon following the schema.
Return summary: {totalOutcomes, stageDistribution, focusOutcome}
""")
```

#### Subagent: Executions Scanner (if execution-info.toon missing)
```
Task(subagent_type="Explore", model="haiku", prompt="""
Scan workspace for executions and generate execution-info.toon.

Schema: plugins/ws/templates/data/execution-info-schema.toon
Output: .claude/execution-info.toon

1. Scan executions/ directory for execution logs
2. For each execution, extract:
   - id, name, linked outcome
   - status (pending/in-progress/completed/failed)
   - progress percentage
   - phase information
3. Identify active execution (if any)
4. Compute cost tracking if available
5. List recent completions
6. List failures requiring attention

Write .claude/execution-info.toon following the schema.
If no executions/ directory or empty, create minimal file with zero counts.
Return summary: {totalExecutions, activeExecutions, failedExecutions}
""")
```

### Step 3: Ensure .claude/ directory exists

Before subagents write files, ensure `.claude/` directory exists:
```bash
mkdir -p .claude
```

### Step 4: Update workspace-info.toon related paths

After related files are generated, update workspace-info.toon to reflect actual paths:
- If file generated: set path (e.g., `.claude/capabilities-info.toon`)
- If file empty/not applicable: set to `null`

## Phase 5: User Confirmation (SETUP only)

Present merged findings:
```
## Workspace Scan Complete

Workspace: {name} @ {commit}
Repository: {remote-url}

### Projects ({count})
{project-list}

### Standard Directories
{directory-summary}

### IDE Integration
{ide-summary}

### Related Data Files
- capabilities-info.toon: {generated|existing|skipped}
- outcomes-info.toon: {generated|existing|skipped}
- execution-info.toon: {generated|existing|skipped}

Proceed with workspace initialization? [Y/n]
```

## Phase 6: Generate Output Files

Write all files to `.claude/` directory following their respective schemas:
- `.claude/workspace-info.toon` → workspace-info-schema.toon
- `.claude/capabilities-info.toon` → capabilities-info-schema.toon (if generated)
- `.claude/outcomes-info.toon` → outcomes-info-schema.toon (if generated)
- `.claude/execution-info.toon` → execution-info-schema.toon (if generated)

All schemas are located in: `plugins/ws/templates/data/`
</process>

<workspace_info_template>
Generate output following workspace-info-schema.toon structure:

```toon
# Workspace Environment Snapshot
# Schema: plugins/ws/templates/data/workspace-info-schema.toon
# Instance: .claude/workspace-info.toon
# Generated by /ws:enviro - DO NOT EDIT MANUALLY

@context: https://schema.org
@type: SoftwareSourceCode
@id: workspace/{workspace-name}
dateCreated: {timestamp}
dateModified: {timestamp}
softwareVersion: 0.2.2

# ─── Workspace ───────────────────────────────────────────
workspace@type: Project
workspace.name: {workspace-name}
workspace.codeRepository: {github-url}
workspace.version: {commit-hash}
workspace.dateModified: {commit-timestamp}

# ─── Related Data Files ─────────────────────────────────
# Paths to detailed TOON instances (null if not yet generated)
# All instances stored in .claude/ directory
relatedData@type: ItemList
relatedData.capabilitiesInfo: .claude/capabilities-info.toon
relatedData.outcomesInfo: .claude/outcomes-info.toon
relatedData.executionInfo: .claude/execution-info.toon

# ─── Projects ────────────────────────────────────────────
projects@type: ItemList
projects.numberOfItems: {count}

project{name,codeRepository,version,dateModified,path,@type,technologies|tab}:
{merged-from-subagent-2}

# ─── Capabilities ────────────────────────────────────────
# Summary - full details in relatedData.capabilitiesInfo
capabilities@type: ItemList
capabilities.path: {path}
capabilities.numberOfItems: {count}

capability{identifier,name,path,maturityLevel|tab}:
{capability-rows}

# ─── Outcomes ────────────────────────────────────────────
# Summary - full details in relatedData.outcomesInfo
outcomes@type: ItemList
outcomes.path: {path}

outcomes.summary{stage,count,path|tab}:
queued	{n}	outcomes/queued/
ready	{n}	outcomes/ready/
in-progress	{n}	outcomes/in-progress/
blocked	{n}	outcomes/blocked/
completed	{n}	outcomes/completed/

# ─── Plans ───────────────────────────────────────────────
plans@type: ItemList
plans.path: plans/
plans.numberOfItems: {count}

# ─── Executions ──────────────────────────────────────────
# Summary - full details in relatedData.executionInfo
executions@type: ItemList
executions.path: executions/
executions.numberOfItems: {count}

# ─── Research ────────────────────────────────────────────
research@type: ItemList
research.path: research/
research.numberOfItems: {count}

# ─── IDE Integration ─────────────────────────────────────
{merged-from-subagent-3}

# ─── Current Focus ───────────────────────────────────────
focus@type: Action
focus.name: null
focus.target: null
focus.actionStatus: PotentialActionStatus

# ─── Session Tracking ────────────────────────────────────
lastSession.id: null
lastSession.timestamp: null
lastSession.event: null
```
</workspace_info_template>

<report_mode>
For REPORT state (healthy workspace-info.toon exists):

### Step 1: Read workspace-info.toon directly (no subagents needed)

### Step 2: Check related data files exist
```
Check if these files exist in .claude/ directory:
- .claude/capabilities-info.toon
- .claude/outcomes-info.toon
- .claude/execution-info.toon
```

### Step 3: Generate missing related files (if any)
If any related files are missing, launch parallel subagents to generate them
(same as Phase 4 subagents - capabilities, outcomes, executions scanners).

This ensures REPORT mode also repairs missing related data.

### Step 4: Display formatted summary

Output format:
```
## Workspace Status

{workspace-name} @ {commit-short}
Last updated: {relative-time}

### Schema Reference
- Schema: plugins/ws/templates/data/workspace-info-schema.toon
- Instance: .claude/workspace-info.toon

### Related Data Status
| File | Status | Items |
|------|--------|-------|
| capabilities-info.toon | {✓/⚡ generated} | {n} |
| outcomes-info.toon | {✓/⚡ generated} | {n} |
| execution-info.toon | {✓/⚡ generated} | {n} |

### Projects ({count})
{project-table}

### Capabilities ({count})
{capability-summary}

### Outcomes
- Queued: {n}
- In Progress: {n}
- Completed: {n}

### Current Focus
{focus-name} ({focus-path})
```
</report_mode>

<migrate_mode>
For MIGRATE state:

### Step 1: Launch migration subagent
```
Task(subagent_type="general-purpose", model="haiku", prompt="""
Migrate workspace-info.toon from old version to current.

Reference schema: plugins/ws/templates/data/workspace-info-schema.toon

1. Read existing .claude/workspace-info.toon
2. Identify version from softwareVersion field
3. Apply migrations for each version step:
   - Add relatedData section if missing
   - Add lastSession tracking fields if missing
   - Ensure all 5 outcome stages present
4. Preserve all existing data
5. Update softwareVersion to 0.2.2
6. Write updated file

Return summary of changes made.
""")
```

### Step 2: Check and generate missing related files
After migration completes, check which related data files exist in `.claude/`:
- .claude/capabilities-info.toon
- .claude/outcomes-info.toon
- .claude/execution-info.toon

Launch parallel subagents to generate any missing files (same as Phase 4).
</migrate_mode>

<repair_mode>
For REPAIR state:

### Step 1: Launch repair subagent for workspace-info
```
Task(subagent_type="general-purpose", model="haiku", prompt="""
Repair corrupted workspace-info.toon.

Reference schema: plugins/ws/templates/data/workspace-info-schema.toon

1. Read existing .claude/workspace-info.toon
2. Identify which sections are valid vs corrupted
3. For corrupted sections, rescan filesystem to regenerate
4. Preserve all valid data
5. Ensure relatedData section exists
6. Write repaired file following schema

Return summary of repairs made.
""")
```

### Step 2: Check and regenerate related files
After repair completes, check ALL related data files in `.claude/` (regenerate even if they exist but may be stale):
- .claude/capabilities-info.toon
- .claude/outcomes-info.toon
- .claude/execution-info.toon

Launch parallel subagents to regenerate all files (same as Phase 4).
This ensures related data is consistent with repaired workspace-info.
</repair_mode>

<output_format>
**Progress Notification** (immediate):
```
Starting workspace environment scan...
Launching parallel scanners for directories, projects, IDE config...
```

**Related Data Scan** (after workspace-info established):
```
Checking related data files in .claude/...
  ✓ .claude/capabilities-info.toon (exists)
  ⚡ .claude/outcomes-info.toon (generating...)
  ⚡ .claude/execution-info.toon (generating...)
```

**SETUP Complete**:
```
## Workspace Environment Initialized

Workspace: {name}
Repository: {url}
Plugin: ws v0.2.2

### Core Files
- .claude/workspace-info.toon ✓

### Related Data (in .claude/)
- capabilities-info.toon: {count} capabilities
- outcomes-info.toon: {count} outcomes
- execution-info.toon: {count} executions

### Summary
Projects: {count} discovered
Capabilities: {count} tracked ({avg}% avg maturity)
Outcomes: {queued} queued, {in-progress} active, {completed} done
```

**REPORT Complete** (with related check):
```
## Workspace Status

{name} @ {commit}
Last updated: {relative-time}

### Related Data Status
| File | Status | Count |
|------|--------|-------|
| capabilities-info.toon | ✓ | {n} |
| outcomes-info.toon | ✓ | {n} |
| execution-info.toon | ⚠ missing | - |

{if any missing}
Run `/ws:enviro --repair` to regenerate missing files.
{/if}

### Projects ({count})
{project-table}

### Capabilities ({count})
{capability-summary}

### Outcomes
- Queued: {n}
- In Progress: {n}
- Completed: {n}
```

**MIGRATE Complete**:
```
## Workspace Migrated

From: ws v{old} → v{new}
Changes: {summary}

### Related Data
Checked and regenerated missing files:
- {file}: {status}
```

**REPAIR Complete**:
```
## Workspace Repaired

### Core File
Fixed: {list}
Preserved: {count} sections

### Related Data
- capabilities-info.toon: {regenerated|preserved}
- outcomes-info.toon: {regenerated|preserved}
- execution-info.toon: {regenerated|preserved}
```
</output_format>

<success_criteria>
- User notified immediately that scan is starting
- Scanning delegated to parallel subagents (not main context)
- Main context only handles: state detection, orchestration, user prompts, final output
- Results merged efficiently from subagent TOON outputs
- Output follows workspace-info-schema.toon structure (from plugins/ws/templates/data/)
- relatedData section included pointing to related instance files in .claude/
- workspace-info.toon valid after execution
- Related data files checked after workspace-info established
- Missing related files generated in parallel via subagents
- All generated files follow their respective schemas from plugins/ws/templates/data/
- All instance files written to .claude/ directory
- Minimal main context token usage
</success_criteria>
