---
description: Detect workspace/project type and generate .claude/workspace-info.toon or .claude/project-info.toon
allowed-tools: [Read, Task, Write, AskUserQuestion]
---

<objective>
Detect whether the current directory is a workspace (multi-project) or a single project, then generate the appropriate info file:
- **Workspace**: Creates `.claude/workspace-info.toon` for multi-project environments with capabilities, outcomes, and plans
- **Project**: Creates `.claude/project-info.toon` for single-project environments

This command is idempotent - it detects existing state and performs setup, repair, or report as needed.
</objective>

<context>
Existing info files: !`ls .claude/*.toon 2>/dev/null || echo "none"`
Git remote: !`git remote get-url origin 2>/dev/null || echo "not a git repo"`
</context>

<process>
## Execution Model

This command uses a coordinator pattern with specialized subagents:
- **Main context**: State detection, orchestration, user interaction, final output
- **Explore subagents**: Scan filesystem, return structured data (READ-ONLY)

IMPORTANT: Immediately notify user that scanning is starting, then delegate.

## Detection Criteria

A directory is classified as a **workspace** if ANY of these are true:
- Contains `capabilities/` directory
- Contains `outcomes/` directory
- Contains multiple project markers (2+ of: package.json, pyproject.toml, Cargo.toml, go.mod, pubspec.yaml)
- Contains a `projects/` or `apps/` or `libs/` directory structure

Otherwise, it's classified as a **project**.

| Signal | Workspace | Project |
|--------|-----------|---------|
| `capabilities/` exists | ✓ | |
| `outcomes/` exists | ✓ | |
| Multiple project markers | ✓ | |
| Single project marker | | ✓ |
| No special directories | | ✓ |

## Phase 1: Quick State Detection (Main Context)

Notify user immediately:
```
Starting environment detection...
```

Check state with minimal reads:
1. Check if `.claude/workspace-info.toon` exists → workspace mode
2. Check if `.claude/project-info.toon` exists → project mode
3. If neither exists, detect environment type

| State | Condition | Action |
|-------|-----------|--------|
| **virgin** | No info file exists | Detect type, run SETUP |
| **workspace-exists** | workspace-info.toon exists | REPORT workspace status |
| **project-exists** | project-info.toon exists | REPORT project status |

## Phase 2: Environment Type Detection (if virgin)

Launch detection scanner:
```
Task(subagent_type="Explore", model="haiku", prompt="""
Detect environment type. Return ONLY this TOON - no prose:

@type: DetectionResult
environment.type: {workspace|project}
environment.signals: {comma-separated list of detected signals}

Detection rules:
- workspace if: capabilities/ exists OR outcomes/ exists OR 2+ project markers
- project otherwise

Check for:
- capabilities/ directory
- outcomes/ directory
- plans/ directory
- package.json, pyproject.toml, Cargo.toml, go.mod, pubspec.yaml, pom.xml, *.csproj
- projects/, apps/, libs/ directories
""")
```

## Phase 3a: Workspace Setup (if type=workspace)

Launch 4 scanners IN PARALLEL in a SINGLE message:

### Scanner 1: Directories
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

### Scanner 2: Projects
```
Task(subagent_type="Explore", model="haiku", prompt="""
Find projects by technology markers. Return ONLY this TOON - no prose:

@type: ItemList
projects{name,path,tech|tab}:
{dirname}	{relative-path}	{typescript|python|rust|go|java|flutter|dotnet}

Detection: package.json=typescript, pyproject.toml=python, Cargo.toml=rust, go.mod=go, pom.xml/build.gradle=java, pubspec.yaml=flutter, *.csproj=dotnet
""")
```

### Scanner 3: IDE
```
Task(subagent_type="Explore", model="haiku", prompt="""
Check .idea/ directory. Return ONLY this TOON - no prose:

If .idea/ exists:
@type: SoftwareApplication
ide.name: IntelliJ IDEA
ide.sdkName: {from misc.xml or null}
ide.languageLevel: {from misc.xml or null}

If no .idea/:
@type: SoftwareApplication
ide.name: none
""")
```

### Scanner 4: Git Metadata
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

After scanners complete, create `.claude/` directory and write `workspace-info.toon`.

## Phase 3b: Project Setup (if type=project)

Launch 2 scanners IN PARALLEL:

### Scanner 1: Project Info
```
Task(subagent_type="Explore", model="haiku", prompt="""
Get project metadata. Return ONLY this TOON - no prose:

@type: SoftwareSourceCode
project.name: {from package.json name, pyproject.toml name, or directory name}
project.version: {from package.json version, pyproject.toml version, or null}
project.description: {from package.json description, or null}
project.technology: {typescript|python|rust|go|java|flutter|dotnet|unknown}
project.entryPoint: {main/index file path, or null}
""")
```

### Scanner 2: Git Metadata
```
Task(subagent_type="Explore", model="haiku", prompt="""
Get git metadata. Return ONLY this TOON - no prose:

@type: Project
project.codeRepository: {git remote get-url origin, or null}
project.gitVersion: {git rev-parse --short HEAD, or null}
project.dateModified: {git log -1 --format=%cI, or null}
project.branch: {git branch --show-current, or null}
""")
```

After scanners complete, create `.claude/` directory and write `project-info.toon`.

## Phase 4: Generate Info File

Write the appropriate file based on environment type (Write tool auto-creates `.claude/` directory):
- Workspace: `.claude/workspace-info.toon`
- Project: `.claude/project-info.toon`

## Phase 5: User Confirmation

Present findings:
```
## Environment Setup Complete

Type: {Workspace|Project}
Name: {name}
Repository: {url}

### {Summary appropriate to type}

Files created:
- .claude/{workspace|project}-info.toon
```
</process>

<output>
**Workspace mode creates:**
- `.claude/workspace-info.toon` - Full workspace snapshot (schema: `shared/schemas/workspace-info-schema.toon`)

**Project mode creates:**
- `.claude/project-info.toon` - Single project snapshot (schema: `shared/schemas/project-info-schema.toon`)

**project-info.toon structure:**
```toon
@context: https://schema.org
@type: SoftwareSourceCode
@id: project/{name}
dateCreated: {timestamp}
dateModified: {timestamp}

project.name: {name}
project.description: {description}
project.version: {version}
project.technology: {tech}
project.entryPoint: {path}
project.codeRepository: {url}
project.gitVersion: {commit}
project.branch: {branch}

dependencies.count: {n}
devDependencies.count: {n}

lastSession.id: null
lastSession.timestamp: null
```
</output>

<verification>
Before completing, verify:
- `.claude/` directory exists
- Appropriate info file created (workspace-info.toon or project-info.toon)
- File contains valid TOON syntax (@context, @type, @id present)
- All scanner data integrated into output file
- No placeholder values remain (all {placeholders} replaced with actual data)
</verification>

<success_criteria>
**Detection:**
- Environment type correctly identified (workspace vs project)
- All relevant signals detected and logged

**File Generation:**
- Appropriate info file created in `.claude/` directory
- File follows TOON format with schema.org types
- All detected metadata captured

**Idempotency:**
- Existing files trigger REPORT mode, not overwrite
- No data loss on re-run

**Context Conservation:**
- Scanners return ONLY compact TOON
- Main context handles orchestration only
- Parallel scanner launches where possible
</success_criteria>
