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

## Phase 3: Produce workspace-info.toon (via toon-specialist)

After all Phase 2 subagents complete:

### Step 1: Ensure .claude/ directory exists
```bash
mkdir -p .claude
```

### Step 2: Collect scanner results
Gather structured data from all Phase 2 scanners:
- Directories data (from Scanner 1)
- Projects & technology data (from Scanner 2)
- IDE configuration data (from Scanner 3)
- Git & workspace metadata (from Scanner 4)

### Step 3: Invoke toon-specialist to produce workspace-info.toon
```
Task(subagent_type="toon-specialist", model="sonnet", prompt="""
@type: CreateAction
name: produce-workspace-info

object.schema: workspace-info-schema.toon
object.output: .claude/workspace-info.toon
object.data:
  workspace: {from Scanner 4 - name, repository, version, dateModified}
  projects: {from Scanner 2 - project list with technologies}
  directories: {from Scanner 1 - capabilities, outcomes, plans counts}
  ide: {from Scanner 3 - IDE configuration}
  focus: null
  lastSession: null

Produce .claude/workspace-info.toon following the schema.
Return production report in TOON format.
""")
```

### Step 4: Proceed to Phase 4
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

For each missing file, launch an Explore subagent IN PARALLEL to gather data.
These are READ-ONLY scanners that return structured JSON data.

#### Scanner: Capabilities Data (if capabilities-info.toon missing)
```
Task(subagent_type="Explore", model="haiku", prompt="""
Scan workspace for capabilities data. Return structured JSON (not TOON).

1. Find all capability_track.json files in capabilities/
2. For each capability, extract:
   - identifier, name, description
   - currentMaturity, targetMaturity
   - status (active/deprecated/planned)
   - capabilityType (atomic/composed)
   - domain (from parent directory name)
3. Compute summary statistics

Return JSON format:
{
  "summary": {
    "totalCapabilities": N,
    "activeCapabilities": N,
    "deprecatedCapabilities": N,
    "atomicCapabilities": N,
    "composedCapabilities": N,
    "averageMaturity": N
  },
  "maturityDistribution": [
    {"range": "0-29%", "count": N},
    {"range": "30-59%", "count": N},
    {"range": "60-79%", "count": N},
    {"range": "80-100%", "count": N}
  ],
  "capabilities": [
    {"identifier": "...", "name": "...", "type": "...", "status": "...", "currentMaturity": N, "targetMaturity": N, "domain": "..."},
    ...
  ],
  "domains": [
    {"domain": "...", "count": N, "avgMaturity": N, "capabilities": ["id1", "id2"]},
    ...
  ]
}
""")
```

#### Scanner: Outcomes Data (if outcomes-info.toon missing)
```
Task(subagent_type="Explore", model="haiku", prompt="""
Scan workspace for outcomes data. Return structured JSON (not TOON).

1. Scan each stage directory: outcomes/queued/, ready/, in-progress/, blocked/, completed/
2. For each outcome, find outcome_track.json and extract:
   - directory, name, stage, priority
   - capabilityContributions
   - parentOutcome (for child outcomes like 005.1-*)
3. Build hierarchy (parent-child relationships)

Return JSON format:
{
  "summary": {
    "totalOutcomes": N,
    "byStage": {"queued": N, "ready": N, "in-progress": N, "blocked": N, "completed": N}
  },
  "outcomes": [
    {"directory": "...", "name": "...", "stage": "...", "priority": N, "type": "parent|atomic", "capabilityContributions": [...], "children": [...]},
    ...
  ],
  "focus": {"name": "...", "path": "..."} or null
}
""")
```

#### Scanner: Executions Data (if execution-info.toon missing)
```
Task(subagent_type="Explore", model="haiku", prompt="""
Scan workspace for executions data. Return structured JSON (not TOON).

1. Check if executions/ directory exists
2. If exists, scan for execution logs and extract:
   - id, name, linked outcome
   - status (pending/in-progress/completed/failed)
   - progress percentage
3. If no executions/ directory, return empty structure

Return JSON format:
{
  "summary": {
    "totalExecutions": N,
    "activeExecutions": N,
    "completedExecutions": N,
    "failedExecutions": N
  },
  "executions": [
    {"id": "...", "name": "...", "outcome": "...", "status": "...", "progress": N},
    ...
  ],
  "activeExecution": {...} or null
}
""")
```

### Step 3: Invoke toon-specialist to produce files (Phase 4b)

After scanners return data, invoke toon-specialist to produce valid TOON files.
Send ALL data in a single request for efficiency:

```
Task(subagent_type="toon-specialist", model="sonnet", prompt="""
@type: CreateAction
name: produce-related-files

# Capabilities data (from scanner)
capabilities.schema: capabilities-info-schema.toon
capabilities.output: .claude/capabilities-info.toon
capabilities.data: {JSON from capabilities scanner}

# Outcomes data (from scanner)
outcomes.schema: outcomes-info-schema.toon
outcomes.output: .claude/outcomes-info.toon
outcomes.data: {JSON from outcomes scanner}

# Executions data (from scanner)
executions.schema: execution-info-schema.toon
executions.output: .claude/execution-info.toon
executions.data: {JSON from executions scanner}

Produce all three .toon files following their respective schemas.
Validate each file before writing.
Return production report in TOON format.
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

All files were produced by toon-specialist following schemas in: `plugins/ws/templates/data/`

If any expected file is missing, report the error from toon-specialist.
</process>

<schema_reference>
**toon-specialist** produces all .toon files using these schemas:

| File | Schema |
|------|--------|
| workspace-info.toon | `plugins/ws/templates/data/workspace-info-schema.toon` |
| capabilities-info.toon | `plugins/ws/templates/data/capabilities-info-schema.toon` |
| outcomes-info.toon | `plugins/ws/templates/data/outcomes-info-schema.toon` |
| execution-info.toon | `plugins/ws/templates/data/execution-info-schema.toon` |

The toon-specialist reads schemas directly and applies them to produce valid output.
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

### Step 1: Read existing workspace-info.toon
Read current file to extract existing data for preservation.

### Step 2: Launch toon-specialist for migration
```
Task(subagent_type="toon-specialist", model="sonnet", prompt="""
@type: UpdateAction
name: migrate

object.source: .claude/workspace-info.toon
object.schema: workspace-info-schema.toon
object.targetVersion: 0.3.0

migrations:
- Add relatedData section if missing
- Add lastSession tracking fields if missing
- Ensure all 5 outcome stages present in outcomes.summary
- Preserve all existing valid data
- Update softwareVersion to 0.3.0
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
4. Update softwareVersion to 0.3.0
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
Plugin: ws v0.3.0

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
- Scanning delegated to parallel Explore subagents (READ-ONLY)
- Main context only handles: state detection, orchestration, user prompts, final output
- **Main context NEVER writes .toon files directly** - all production via toon-specialist
- **Two-phase pattern for ALL file generation:**
  - Phase A: Explore agents return structured data (JSON)
  - Phase B: toon-specialist produces valid .toon files
- **toon-specialist produces ALL .toon files:**
  - workspace-info.toon (Phase 3)
  - capabilities-info.toon, outcomes-info.toon, execution-info.toon (Phase 4)
- toon-specialist validates all files before writing
- All files follow their respective schemas from plugins/ws/templates/data/
- All instance files written to .claude/ directory
- Minimal main context token usage
- **No TOON format errors** (toon-specialist ensures consistency)
</success_criteria>
