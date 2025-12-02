---
description: Idempotent workspace environment setup, repair, migration, and status reporting
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion]
---

<objective>
Manage the workspace environment through an idempotent command that detects current state and performs the appropriate action: setup, repair, migrate, or report.

This command maintains `workspace-info.toon` in the `.claude` directory, using schema.org vocabulary to describe the workspace structure and status snapshot.
</objective>

<context>
Workspace info: @.claude/workspace-info.toon
Plugin version: @plugins/ws/plugin.json
Git status: !`git rev-parse --short HEAD 2>/dev/null || echo "no-git"`
Git remote: !`git remote get-url origin 2>/dev/null || echo "no-remote"`
Timestamp: !`date -u +%Y-%m-%dT%H:%M:%SZ`
</context>

<state_detection>
Detect workspace state by checking for `.claude/workspace-info.toon`:

| State | Condition | Action |
|-------|-----------|--------|
| **virgin** | File doesn't exist | Run SETUP |
| **healthy** | File exists, valid, version matches | Run REPORT |
| **outdated** | File exists, version mismatch | Run MIGRATE |
| **corrupted** | File exists, invalid/incomplete | Run REPAIR |
</state_detection>

<setup_scanning>
When workspace-info.toon does not exist, perform comprehensive directory and file scanning:

## 1. Standard Workspace Directories

Scan for these directories at workspace root:

| Directory | Purpose | Scan For |
|-----------|---------|----------|
| `capabilities/` | Capability tracking | `**/capability_track.json`, subdirs |
| `outcomes/` | Outcome management | `**/outcome_track.json`, stage subdirs |
| `plans/` | Plan documents | `*.md`, design docs |
| `executions/` | Execution logs | Session logs, reports |
| `research/` | Research artifacts | Notes, references, findings |
| `status/` | Summary files | `capability_summary.json`, `outcome_summary.json` |

For each found directory, record:
- Path (relative to workspace root)
- Item count
- Last modified timestamp

## 2. Project Map Detection

Check for `project-map.json` at workspace root or in `.claude/`:

```bash
# Scan locations
ls -la project-map.json .claude/project-map.json 2>/dev/null
```

If found, extract:
- Project names and paths
- Project types and technologies
- Cross-project dependencies

## 3. IntelliJ IDEA Configuration

Scan for `.idea/` directory at workspace root:

```bash
# Check for IntelliJ project
ls -la .idea/ 2>/dev/null
```

### Key IntelliJ Files to Read

| File | Contains | Extract |
|------|----------|---------|
| `.idea/modules.xml` | Module definitions | Project modules and their paths |
| `.idea/misc.xml` | Project SDK, language level | Java/Kotlin version, SDK name |
| `.idea/vcs.xml` | VCS mappings | Git roots, VCS type |
| `.idea/*.iml` | Module configs | Source roots, dependencies |
| `.idea/runConfigurations/` | Run configs | Application entry points |
| `.idea/codeStyles/` | Code style settings | Formatting preferences |

### IntelliJ Parsing Logic

```
1. If .idea/modules.xml exists:
   - Parse <module> elements for fileurl paths
   - Each module = potential project/subproject

2. If .idea/misc.xml exists:
   - Extract <component name="ProjectRootManager">
   - Get project-jdk-name, languageLevel

3. If .idea/vcs.xml exists:
   - Parse <mapping directory="..." vcs="Git"/>
   - Identify git-tracked subdirectories

4. For each *.iml file found:
   - Extract <sourceFolder> elements
   - Identify src/main, src/test, resources
   - Note module dependencies
```

### IntelliJ Directory Locations (Reference)

**Project-level** (in workspace):
- `.idea/` - Project settings directory
- `*.iml` - Module files (may be in root or subdirs)

**User-level** (global, do not scan):
- macOS: `~/Library/Application Support/JetBrains/IntelliJIdea{version}/`
- Windows: `%APPDATA%\JetBrains\IntelliJIdea{version}\`
- Linux: `~/.config/JetBrains/IntelliJIdea{version}/`

## 4. Additional Project Indicators

Also scan for:

| File | Indicates | Technology |
|------|-----------|------------|
| `package.json` | Node.js project | JavaScript/TypeScript |
| `pyproject.toml` | Python project | Python (modern) |
| `setup.py` | Python project | Python (legacy) |
| `Cargo.toml` | Rust project | Rust |
| `go.mod` | Go project | Go |
| `pom.xml` | Maven project | Java |
| `build.gradle` | Gradle project | Java/Kotlin |
| `*.csproj` | .NET project | C# |
| `pubspec.yaml` | Flutter/Dart | Dart |
| `Gemfile` | Ruby project | Ruby |

## 5. Scan Execution Order

```
1. Check for project-map.json → use as primary source if found
2. Scan for .idea/ → extract IntelliJ project structure
3. Scan for standard directories (capabilities, outcomes, etc.)
4. Scan for technology indicators (package.json, etc.)
5. Scan for .git directories → identify project boundaries
6. Merge and deduplicate findings
7. Present discovered structure for confirmation
```

## 6. Scan Output

After scanning, present findings before generating workspace-info.toon:

```
## Workspace Scan Results

### Detected from IntelliJ (.idea/)
- Modules: {list}
- SDK: {java-version}
- VCS roots: {list}

### Detected from project-map.json
- Projects: {list with paths}

### Standard Directories Found
- capabilities/: {count} capabilities
- outcomes/: {count} outcomes
- plans/: {count} plans
- executions/: {count} executions
- research/: {found|not found}

### Technology Stack
- {tech}: {project-path}
- ...

Proceed with workspace initialization? [Y/n]
```
</setup_scanning>

<process>
1. **Detect State**:
   - Check if `.claude/workspace-info.toon` exists
   - If exists: validate structure and version
   - Determine action: setup | repair | migrate | report

2. **Execute Action**:

   **SETUP** (virgin state):
   - Create `.claude/` directory if needed
   - Run comprehensive workspace scan (see `<setup_scanning>`)
   - Gather remaining information interactively
   - Generate initial `workspace-info.toon`
   - Display setup summary

   **REPAIR** (corrupted state):
   - Identify missing/invalid sections
   - Preserve valid data
   - Regenerate corrupted sections from filesystem
   - Update snapshot timestamp
   - Display repair summary

   **MIGRATE** (outdated state):
   - Read existing file
   - Transform to new schema version
   - Preserve all compatible data
   - Add new required fields with defaults
   - Update version and timestamp
   - Display migration summary

   **REPORT** (healthy state):
   - Read and display current workspace status
   - Show workspace overview
   - List projects with sync status
   - Summarize capabilities and maturity
   - Summarize outcomes by stage
   - Show current focus

3. **Update Snapshot**:
   - Always update `dateModified` timestamp
   - Update git commit references
   - Write changes to file
</process>

<workspace_info_schema>
The `workspace-info.toon` file uses TOON format with schema.org vocabulary:

```toon
# Workspace Environment Snapshot
# Generated by ws plugin

@context: https://schema.org
@type: SoftwareSourceCode
@id: workspace/{workspace-name}
dateCreated: {initial-creation-timestamp}
dateModified: {last-snapshot-timestamp}
softwareVersion: {ws-plugin-version}

# ─── Workspace ───────────────────────────────────────────
workspace@type: Project
workspace.name: {workspace-name}
workspace.codeRepository: {github-url}
workspace.version: {last-commit-id}
workspace.dateModified: {commit-timestamp}

# ─── Projects ────────────────────────────────────────────
projects@type: ItemList
projects.numberOfItems: {count}

project{name,codeRepository,version,dateModified,path,@type,technologies|tab}:
{name}	{repo}	{commit}	{timestamp}	{relative-path}	{project-type}	{tech-stack}
...

# Project Artifacts (per project)
artifacts.{project-name}{name,@type,path,description,usedBy|tab}:
{artifact-name}	{artifact-type}	{relative-path}	{contains-description}	{used-by}
...

# ─── Capabilities ────────────────────────────────────────
capabilities@type: ItemList
capabilities.path: {capabilities-root-path}
capabilities.numberOfItems: {count}

capability{identifier,name,path,maturityLevel|tab}:
{id}	{capability-name}	{relative-path}	{maturity-percentage}
...

# ─── Outcomes ────────────────────────────────────────────
outcomes@type: ItemList
outcomes.path: {outcomes-root-path}

outcomes.summary{stage,count,path|tab}:
queued	{n}	{path-to-queued}
ready	{n}	{path-to-ready}
in-progress	{n}	{path-to-in-progress}
blocked	{n}	{path-to-blocked}
completed	{n}	{path-to-completed}

# ─── Plans ───────────────────────────────────────────────
plans@type: ItemList
plans.path: {plans-root-path}
plans.numberOfItems: {count}

# ─── Executions ──────────────────────────────────────────
executions@type: ItemList
executions.path: {executions-root-path}
executions.numberOfItems: {count}

# ─── Research ────────────────────────────────────────────
research@type: ItemList
research.path: {research-root-path}
research.numberOfItems: {count}

# ─── IDE Integration ─────────────────────────────────────
ide@type: SoftwareApplication
ide.name: {ide-name}
ide.softwareVersion: {ide-version}
ide.configPath: {.idea-path}

ide.modules{name,path,type|tab}:
{module-name}	{module-path}	{module-type}
...

ide.sdkName: {sdk-name}
ide.languageLevel: {language-level}

# ─── Current Focus ───────────────────────────────────────
focus@type: Action
focus.name: {current-outcome-name}
focus.target: {current-outcome-path}
focus.actionStatus: ActiveActionStatus
```
</workspace_info_schema>

<setup_questions>
After scanning completes, only ask for information that couldn't be auto-detected:

1. **Workspace name**:
   - Auto-detect from: git remote name, .idea project name, directory name
   - Ask only if: multiple candidates or none found

2. **Confirm detected structure**:
   - Present scan results (see `<setup_scanning>` output)
   - Ask user to confirm or modify detected paths

3. **Missing directories** (if not found):
   - Ask whether to create standard directories (capabilities/, outcomes/, etc.)
   - Or specify custom paths

4. **Current focus**:
   - If outcomes exist, ask which outcome is currently in progress
   - Otherwise, leave focus empty

For each project discovered:
- Auto-detect type from build files (package.json → library/app, pom.xml → service, etc.)
- Auto-detect technology stack from manifest files
- Auto-scan for key artifacts (entry points, configs, schemas)
- Only ask for clarification if detection is ambiguous
</setup_questions>

<output_format>
**SETUP Output**:
```
## Workspace Environment Initialized

Workspace: {name}
Repository: {github-url}
Plugin: ws v{version}

Projects: {count} discovered
Capabilities: {count} tracked
Outcomes: {count} total ({in-progress} active)

Created: .claude/workspace-info.toon
```

**REPORT Output**:
```
## Workspace Status

{workspace-name} @ {commit-short}
Last updated: {relative-time}

### Projects ({count})
{project-table}

### Capabilities ({count})
{capability-summary-with-maturity}

### Outcomes
- Queued: {n}
- Ready: {n}
- In Progress: {n}
- Blocked: {n}
- Completed: {n}

### Current Focus
{outcome-name} ({outcome-path})
```

**REPAIR Output**:
```
## Workspace Repaired

Fixed sections:
- {section}: {issue} → {resolution}

Preserved: {count} sections unchanged
Updated: .claude/workspace-info.toon
```

**MIGRATE Output**:
```
## Workspace Migrated

From: ws v{old-version}
To: ws v{new-version}

Changes:
- {migration-change-description}

Updated: .claude/workspace-info.toon
```
</output_format>

<success_criteria>
- State correctly detected (virgin/healthy/outdated/corrupted)
- Appropriate action executed (setup/report/migrate/repair)
- workspace-info.toon is valid after execution
- All sections populated with accurate data
- Git references current and accurate
- Timestamps in ISO 8601 UTC format
- schema.org vocabulary used correctly
- Command is truly idempotent (safe to run repeatedly)
</success_criteria>

<verification>
After any write operation:
1. Read back workspace-info.toon
2. Validate all required sections present
3. Verify git commit matches current HEAD
4. Confirm timestamp is recent
5. Check version matches ws plugin version
</verification>
