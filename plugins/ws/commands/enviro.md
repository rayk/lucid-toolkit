---
description: Idempotent workspace environment setup, repair, migration, and status reporting
allowed-tools: [Task, Read, Bash, AskUserQuestion]
---

<objective>
Manage the workspace environment through an idempotent command that detects current state and performs the appropriate action: setup, repair, migrate, or report.

This command delegates scanning work to parallel subagents to minimize main context usage.
</objective>

<schema_reference>
## Schema / Instance Relationship

**Schemas** are managed by the toon-specialist subagent (read-only reference data).

**Instances** are ALWAYS saved to `.claude/` in the project where the plugin is installed:
```
{project}/.claude/
├── workspace-info.toon          (main workspace snapshot)
├── capabilities-info.toon       (capabilities index)
├── outcomes-info.toon           (outcomes index)
└── execution-info.toon          (execution tracking)
```

| Data File | Schema Name | Instance |
|-----------|-------------|----------|
| workspace-info | `workspace-info-schema.toon` | `.claude/workspace-info.toon` |
| capabilities-info | `capabilities-info-schema.toon` | `.claude/capabilities-info.toon` |
| outcomes-info | `outcomes-info-schema.toon` | `.claude/outcomes-info.toon` |
| execution-info | `execution-info-schema.toon` | `.claude/execution-info.toon` |

**Note:** Schema locations are known only to toon-specialist. Callers reference schemas by name only.
</schema_reference>

<execution_model>
This command uses a coordinator pattern with specialized subagents:

1. **Main context**: State detection, orchestration, user interaction, final output
2. **Explore subagents**: Scan filesystem, return structured data (READ-ONLY)
3. **toon-specialist subagent**: Produces valid .toon files from structured data

**Two-Phase Pattern for File Generation:**
```
┌─────────────────┐     structured      ┌─────────────────┐
│  Explore Agent  │ ──── data ────────► │ toon-specialist │
│  (read-only)    │     (JSON/dict)     │  (writes files) │
└─────────────────┘                     └─────────────────┘
```

IMPORTANT: Immediately notify user that scanning is starting, then delegate.
</execution_model>

<process>
## Execution Summary

| Phase | Action | Parallelism |
|-------|--------|-------------|
| 1 | State detection | Main context (1-2 reads) |
| 2 | Workspace scanning | **4 Explore agents IN PARALLEL** |
| 3 | Produce workspace-info.toon | 1 toon-specialist |
| 4 | Related data scanning | **Up to 3 Explore agents IN PARALLEL** |
| 4b | Produce related .toon files | 1 toon-specialist |

**CRITICAL**: Phases 2 and 4a MUST launch all subagents in a SINGLE message with multiple Task calls.

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

For SETUP state, launch ALL 4 subagents IN PARALLEL in a SINGLE message with 4 Task tool calls.

**CRITICAL**: Use exactly these prompts. Scanners return ONLY the specified fields - no explanations, no extra data.

### Subagent 1: Directories Scanner
```
Task(subagent_type="Explore", model="haiku", prompt="""
Count files in workspace directories. Return ONLY this TOON - no prose:

@type: ItemList
directories{name,exists,count|tab}:
capabilities	{true|false}	{count of **/capability-statement.md}
outcomes	{true|false}	{count of **/outcome_track.json}
plans	{true|false}	{count of *.md}
executions	{true|false}	{count of files}
research	{true|false}	0
status	{true|false}	0
""")
```

### Subagent 2: Projects Scanner
```
Task(subagent_type="Explore", model="haiku", prompt="""
Find projects by technology markers. Return ONLY this TOON - no prose:

@type: ItemList
hasProjectMap: {true|false}
projectMapPath: {path or null}

projects{name,path,tech|tab}:
{dirname}	{relative-path}	{typescript|python|rust|go|java|flutter|dotnet}

Detection: package.json=typescript, pyproject.toml=python, Cargo.toml=rust, go.mod=go, pom.xml/build.gradle=java, pubspec.yaml=flutter, *.csproj=dotnet
""")
```

### Subagent 3: IDE Scanner
```
Task(subagent_type="Explore", model="haiku", prompt="""
Check .idea/ directory. Return ONLY this TOON - no prose:

If .idea/ exists:
@type: SoftwareApplication
ide.name: IntelliJ IDEA
ide.sdkName: {from misc.xml or null}
ide.languageLevel: {from misc.xml or null}
ide.moduleCount: {count of *.iml files}

If no .idea/:
@type: SoftwareApplication
ide.name: none
""")
```

### Subagent 4: Git Metadata Scanner
```
Task(subagent_type="Explore", model="haiku", prompt="""
Get git metadata. Return ONLY this TOON - no prose:

@type: Project
workspace.name: {basename of cwd}
workspace.codeRepository: {git remote get-url origin, or null}
workspace.version: {git rev-parse --short HEAD, or null}
workspace.dateModified: {git log -1 --format=%cI, or null}
""")
```

**Parallel Launch Instruction**: Send ONE message containing 4 Task tool calls simultaneously.

## Phase 3: Produce workspace-info.toon (via toon-specialist)

After all Phase 2 subagents complete, pass their TOON outputs directly to toon-specialist.

### Step 1: Ensure .claude/ directory exists
```bash
mkdir -p .claude
```

### Step 2: Invoke toon-specialist with scanner outputs
Pass the raw TOON from all 4 scanners. Do NOT reformat - toon-specialist handles parsing.

```
Task(subagent_type="toon-specialist", prompt="""
@type: CreateAction
name: produce
object.schema: workspace-info-schema.toon
object.output: .claude/workspace-info.toon

# Scanner 1 output (directories):
{paste Scanner 1 TOON verbatim}

# Scanner 2 output (projects):
{paste Scanner 2 TOON verbatim}

# Scanner 3 output (IDE):
{paste Scanner 3 TOON verbatim}

# Scanner 4 output (git):
{paste Scanner 4 TOON verbatim}

# Defaults:
focus.name: null
focus.actionStatus: PotentialActionStatus
lastSession.id: null
""")
```

### Step 3: Proceed to Phase 4
After workspace-info.toon is confirmed written, check related data files.

## Phase 4: Check and Generate Related Data Files

After workspace-info.toon is established (SETUP, MIGRATE, REPAIR, or HEALTHY states):

### Step 1: Check which related files exist
```
.claude/capabilities-info.toon  → exists? valid?
.claude/outcomes-info.toon      → exists? valid?
.claude/execution-info.toon     → exists? valid?
```

### Step 2: Launch SCANNER subagents for MISSING files (Phase 4a)

Launch ALL needed scanners IN PARALLEL in a SINGLE message. Scanners return compact TOON only.

#### Scanner: Capabilities Data (if capabilities-info.toon missing)
```
Task(subagent_type="Explore", model="haiku", prompt="""
Read all capabilities/**/capability-statement.md YAML frontmatter. Return ONLY this TOON - no prose:

@type: ItemList
summary.total: {count}
summary.active: {count where status=active}
summary.avgMaturity: {average currentMaturity as int}

capabilities{id,name,type,status,maturity,target|tab}:
{identifier}	{name}	{atomic|composed}	{active|deprecated}	{maturity.current}	{maturity.target}
""")
```

#### Scanner: Outcomes Data (if outcomes-info.toon missing)
```
Task(subagent_type="Explore", model="haiku", prompt="""
Count outcome_track.json in each outcomes/{stage}/ directory. Return ONLY this TOON - no prose:

@type: ItemList
summary{stage,count|tab}:
queued	{count in outcomes/queued/}
ready	{count in outcomes/ready/}
in-progress	{count in outcomes/in-progress/}
blocked	{count in outcomes/blocked/}
completed	{count in outcomes/completed/}

focus.name: {directory name in in-progress with focus=true, or null}
focus.path: {path to focused outcome, or null}
""")
```

#### Scanner: Executions Data (if execution-info.toon missing)
```
Task(subagent_type="Explore", model="haiku", prompt="""
Check executions/ directory. Return ONLY this TOON - no prose:

@type: ItemList
summary.total: {count of execution files, or 0}
summary.active: {count where status=in-progress, or 0}
summary.completed: {count where status=completed, or 0}

activeExecution.id: {id of active execution, or null}
activeExecution.outcome: {linked outcome, or null}
""")
```

**Parallel Launch Instruction**: Send ONE message containing all needed scanner Task calls.

### Step 3: Invoke toon-specialist to produce files (Phase 4b)

After scanners return, pass raw TOON outputs to toon-specialist. Single request for all files:

```
Task(subagent_type="toon-specialist", prompt="""
@type: CreateAction
name: produce-related

# File 1: capabilities-info
capabilities.schema: capabilities-info-schema.toon
capabilities.output: .claude/capabilities-info.toon
capabilities.data:
{paste Capabilities Scanner TOON verbatim}

# File 2: outcomes-info
outcomes.schema: outcomes-info-schema.toon
outcomes.output: .claude/outcomes-info.toon
outcomes.data:
{paste Outcomes Scanner TOON verbatim}

# File 3: execution-info
executions.schema: execution-info-schema.toon
executions.output: .claude/execution-info.toon
executions.data:
{paste Executions Scanner TOON verbatim}
""")
```

### Step 4: Update workspace-info.toon related paths

After toon-specialist confirms files are written, update workspace-info.toon:
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

## Phase 6: Verify Output Files

Confirm all .toon files were produced by toon-specialist:
- `.claude/workspace-info.toon` - must exist
- `.claude/capabilities-info.toon` - exists if capabilities/ directory found
- `.claude/outcomes-info.toon` - exists if outcomes/ directory found
- `.claude/execution-info.toon` - exists if executions/ directory found

All files were produced by toon-specialist using its schema registry.

If any expected file is missing, report the error from toon-specialist.
</process>

<schema_reference>
**toon-specialist** produces all .toon files using its schema registry.

| File | Schema Name |
|------|-------------|
| workspace-info.toon | `workspace-info-schema.toon` |
| capabilities-info.toon | `capabilities-info-schema.toon` |
| outcomes-info.toon | `outcomes-info-schema.toon` |
| execution-info.toon | `execution-info-schema.toon` |

The toon-specialist knows schema locations and applies them to produce valid output.
No manual formatting required - all schema.org/TOON production is delegated.
</schema_reference>

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
If any related files are missing, use the two-phase pattern from Phase 4:
1. Launch Explore scanners to gather data (Phase 4a pattern)
2. Invoke toon-specialist to produce files (Phase 4b pattern)

This ensures REPORT mode also repairs missing related data with valid TOON format.

### Step 4: Display formatted summary

Output format:
```
## Workspace Status

{workspace-name} @ {commit-short}
Last updated: {relative-time}

### Schema Reference
- Schema: workspace-info-schema.toon (via toon-specialist)
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

### Step 1: Read existing workspace-info.toon
Read current file to extract existing data for preservation.

### Step 2: Launch toon-specialist for migration
```
Task(subagent_type="toon-specialist", model="sonnet", prompt="""
@type: UpdateAction
name: migrate

object.source: .claude/workspace-info.toon
object.schema: workspace-info-schema.toon
object.targetVersion: 0.8.0

migrations:
- Add relatedData section if missing
- Add lastSession tracking fields if missing
- Ensure all 5 outcome stages present in outcomes.summary
- Preserve all existing valid data
- Update softwareVersion to 0.8.0
- Update dateModified to current timestamp

Return migration report in TOON format showing changes made.
""")
```

### Step 3: Check and generate missing related files
After migration completes, check which related data files exist in `.claude/`:
- .claude/capabilities-info.toon
- .claude/outcomes-info.toon
- .claude/execution-info.toon

For missing files, use the two-phase pattern from Phase 4:
1. Launch Explore scanners to gather data (Phase 4a pattern)
2. Invoke toon-specialist to produce files (Phase 4b pattern)
</migrate_mode>

<repair_mode>
For REPAIR state:

### Step 1: Analyze corrupted workspace-info.toon
```
Task(subagent_type="Explore", model="haiku", prompt="""
Analyze .claude/workspace-info.toon for corruption.

1. Read the file and identify:
   - Which sections parse correctly
   - Which sections are corrupted/incomplete
   - What data can be preserved
2. Scan filesystem to gather fresh data for corrupted sections

Return JSON format:
{
  "preservedSections": ["workspace", "projects", ...],
  "corruptedSections": ["capabilities", "outcomes", ...],
  "freshData": {
    "workspace": {...},
    "directories": {...},
    ...
  }
}
""")
```

### Step 2: Launch toon-specialist for repair
```
Task(subagent_type="toon-specialist", model="sonnet", prompt="""
@type: UpdateAction
name: repair

object.path: .claude/workspace-info.toon
object.schema: workspace-info-schema.toon
object.preservedData: {preserved sections from analyzer}
object.freshData: {fresh data from analyzer}

Repair the workspace-info.toon file:
1. Keep all valid preserved sections
2. Replace corrupted sections with fresh data
3. Ensure relatedData section exists
4. Update softwareVersion to 0.8.0
5. Update dateModified to current timestamp
6. Validate complete file before writing

Return repair report in TOON format.
""")
```

### Step 3: Regenerate ALL related files
After repair completes, regenerate ALL related data files (they may be stale):
- .claude/capabilities-info.toon
- .claude/outcomes-info.toon
- .claude/execution-info.toon

Use the two-phase pattern from Phase 4:
1. Launch Explore scanners to gather fresh data (Phase 4a pattern)
2. Invoke toon-specialist to produce files (Phase 4b pattern)

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
Plugin: ws v0.8.0

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
**Parallelism:**
- Phase 2: ALL 4 scanners launched in ONE message (4 parallel Task calls)
- Phase 4a: ALL needed scanners launched in ONE message (up to 3 parallel Task calls)
- Never sequential scanner launches

**Data Flow:**
- Scanners return ONLY compact TOON - no prose, no explanations
- Scanner output passed verbatim to toon-specialist - no reformatting in main context
- Main context only handles: state detection, orchestration, final output

**File Production:**
- Main context NEVER writes .toon files directly
- toon-specialist produces ALL .toon files (workspace-info, capabilities-info, outcomes-info, execution-info)
- All instance files written to .claude/ directory

**Context Conservation:**
- Minimal main context token usage
- No verbose scanner responses polluting context
- toon-specialist handles all schema reading and validation
</success_criteria>
