# Workspace Plugin

IntelliJ workspace project management with index synchronization to member projects.

## Overview

The Workspace plugin implements the IntelliJ workspace model where the **workspace itself IS a project** containing capabilities, outcomes, plans, research, and status directories. Member projects are added to the workspace and receive synchronized indexes of workspace artifacts.

Key features:
- **Workspace IS a Project**: The workspace is an IntelliJ project that contains all planning artifacts
- **Index Synchronization**: Workspace indexes are automatically synced to member projects
- **Comprehensive Source Mapping**: `project-map.json` maps all project sources, modules, and entry points
- **10-Phase Health Validation**: Systematic health checks with auto-repair
- **Module Resolution**: Quick navigation via `project:module[/subpath][#entry]` references

## Installation

```bash
# Add the lucid-toolkit marketplace
/plugin marketplace add rayk/lucid-toolkit

# Install the workspace plugin
/plugin install workspace@lucid-toolkit
```

### Prerequisites

- Claude Code >= 1.0.0
- Python >= 3.11
- Shared CLI library (required for hooks):
  ```bash
  cd shared/cli-commons && pip install -e .
  ```

## Architecture

### Workspace Structure

The workspace project contains all planning and tracking artifacts:

```
lucid-workspace/                    # Workspace IS the project
├── workspace.json                  # Workspace definition + project list
├── project-map.json                # Source maps for all projects
├── capabilities/                   # Strategic capabilities by domain
├── outcomes/                       # Work units by state
│   ├── queued/
│   ├── ready/
│   ├── in-progress/
│   ├── blocked/
│   └── completed/
├── plans/                          # Roadmaps and execution plans
├── research/                       # Domain research and analysis
├── status/                         # Summary indexes
│   ├── capability_summary.json
│   ├── outcome_summary.json
│   └── actor_summary.json
├── schemas/                        # JSON validation schemas
└── .idea/jb-workspace.xml         # IntelliJ workspace flag
```

### Project Integration

Each member project receives a `.claude/workspace.json` with:
- **Indexes**: Paths with descriptions to capabilities, outcomes, plans, research, status
- **Projects List**: All workspace projects with relative paths for navigation
- **Sync Metadata**: Last sync timestamp and auto-sync settings

```
member-project/.claude/
└── workspace.json                  # Receives indexes + project list
    ├── indexes.capabilities        # Path + description + count + domains
    ├── indexes.outcomes            # Path + description + state counts
    ├── indexes.plans               # Path + description + items
    ├── indexes.research            # Path + description + items
    └── projects[]                  # All workspace projects
```

## Commands

### Workspace Management

#### `/workspace:init [workspace-name]`
Initialize the current directory as an IntelliJ workspace project.

Creates `workspace.json`, `project-map.json`, and all standard directories.

#### `/workspace:add [project-path or git-url]`
Add a project to the workspace.

Updates `workspace.json` and `project-map.json`, creates project's `.claude/workspace.json` with indexes.

#### `/workspace:remove [project-name]`
Remove a project from workspace configuration.

Preserves project files on disk (configuration only).

### Project Connection

#### `/workspace:join [workspace-path]`
Connect current project to an existing workspace (run from project directory).

Creates `.claude/workspace.json` with indexes to workspace artifacts.

#### `/workspace:leave [--keep-in-workspace]`
Disconnect current project from its workspace.

Removes `.claude/workspace.json`. By default, also removes project from workspace.

### Synchronization

#### `/workspace:sync [--project <id>] [--dry-run]`
Synchronize workspace indexes to all member projects.

Reads current state from workspace status files and updates each project's `.claude/workspace.json`.

**Auto-sync**: When `capability_summary.json` or `outcome_summary.json` changes, the sync hook automatically updates all projects.

### Navigation

#### `/workspace:list [--verbose | --json]`
Display all projects in the workspace with sync status.

Shows project types, roles, languages, sync status, and module counts.

#### `/workspace:switch [project-name]`
Switch working context to a specific project.

#### `/workspace:resolve <project:module[/subpath][#entry]>`
Resolve module references to absolute paths.

**Reference Patterns:**

| Pattern | Example | Description |
|---------|---------|-------------|
| `project:module` | `lucid-knowledge:neo4j_service` | Module in specific project |
| `module_id` | `neo4j_service` | Search all projects (if unique) |
| `project:module/subpath` | `lucid-knowledge:evolution/wrangler` | Subpath within module |
| `project:module#entry` | `lucid-knowledge:neo4j_service#CypherLoader` | Entry point file |

### Validation & Health

#### `/workspace:health [--fix | --verbose | --phase N]`
Execute comprehensive 10-phase workspace health check.

**Phases:**
0. Workspace Structure Validation
1. Capability Directory-Summary Sync
2. Outcome Directory-Summary Sync
3. Cross-Reference Integrity
4. Index Validation & Rebuild
5. Project Sync Validation
6. Temporal Health Checks
7. Temp File Cleanup
8. Git Health Check
9. Comprehensive Report

**Options:**
- `--fix`: Auto-repair issues
- `--verbose`: Detailed output
- `--phase N`: Run specific phase (0-9)
- `--dry-run`: Preview changes
- `--json`: JSON output

#### `/workspace:validate [--schemas | --refs | --all]`
Deep validation of workspace configurations.

## Usage Examples

### Initialize Workspace and Add Projects

```bash
# In the workspace project directory
/workspace:init "My Workspace"

# Add projects
/workspace:add ../my-library
/workspace:add ../my-service
```

### Connect a Project to Workspace

```bash
# In the project directory
/workspace:join ../my-workspace
```

### Sync and Health Checks

```bash
# Manually sync indexes to all projects
/workspace:sync

# Run health check
/workspace:health --verbose

# Auto-fix issues
/workspace:health --fix
```

### Navigation

```bash
# List all projects with sync status
/workspace:list

# Resolve module path
/workspace:resolve lucid-knowledge:neo4j_service#CypherLoader
```

## Workspace Types

| Type | Description | Example |
|------|-------------|---------|
| `monorepo` | Single repo, multiple packages | Lerna, Turborepo |
| `multi-repo` | Separate repositories | Microservices |
| `hybrid` | Mix of both | Platform + plugins |

## Project Types

| Type | Description |
|------|-------------|
| `library` | Reusable code package |
| `service` | Backend service/API |
| `application` | User-facing application |
| `tool` | Development/build tool |
| `docs` | Documentation project |
| `config` | Shared configuration |
| `planning` | Planning/workspace project |

## Schemas

| Schema | Purpose |
|--------|---------|
| `workspace_schema.json` | Workspace project configuration |
| `project_workspace_schema.json` | Project's `.claude/workspace.json` |
| `project_map_schema.json` | Source mapping for all projects |
| `actor_summary_schema.json` | Stakeholder registry |

## File Structure

```
plugins/workspace/
├── plugin.json              # Plugin metadata
├── README.md               # This file
├── settings.json           # Hook configuration
├── commands/
│   ├── init.md            # Initialize workspace
│   ├── add.md             # Add project
│   ├── remove.md          # Remove project
│   ├── join.md            # Join workspace (from project)
│   ├── leave.md           # Leave workspace
│   ├── sync.md            # Sync indexes
│   ├── list.md            # List projects
│   ├── switch.md          # Switch context
│   ├── health.md          # 10-phase health check
│   ├── validate.md        # Schema/ref validation
│   └── resolve.md         # Module resolution
├── hooks/
│   ├── pre-commit-validation.py    # Validate before commit
│   └── sync-on-summary-change.py   # Auto-sync on changes
└── schemas/
    ├── workspace_schema.json        # Workspace config (v2.0.0)
    ├── project_workspace_schema.json # Project index receiver
    ├── project_map_schema.json      # Source mapping (v2.0.0)
    └── actor_summary_schema.json    # Stakeholder registry
```

## Version History

### v2.0.0
- **Breaking**: Workspace IS the project (IntelliJ model)
- Added `plans/` and `research/` directories
- New index synchronization model with `project_workspace_schema.json`
- New commands: `join`, `leave`, `sync`
- Removed: `subscribe`, `unsubscribe` (replaced by join/leave)
- Auto-sync hook for summary changes
- 10-phase health check (added Phase 0 and Phase 5)
