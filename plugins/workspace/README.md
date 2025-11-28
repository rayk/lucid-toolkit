# Workspace Plugin

Multi-project management with shared registry, health validation, and cross-reference integrity for Claude Code.

## Overview

The Workspace plugin enables management of multiple related projects or repositories as a single unified workspace. It provides:

- **Shared Registry**: Central workspace registry with multi-project coordination
- **Subscriber Model**: Multiple projects can subscribe to the same workspace
- **Health Validation**: 8-phase systematic health checks with auto-repair
- **Cross-Reference Integrity**: Validation of capability-outcome relationships
- **Module Resolution**: Quick navigation via `project:module` references

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
- Shared CLI library (required for hooks/scripts):
  ```bash
  cd shared/cli-commons && pip install -e .
  ```

## Architecture

### Shared Workspace Registry

Workspaces are stored in a shared registry at `shared/workspaces/workspaces.json`. Each workspace has its own home directory containing capabilities, outcomes, and status artifacts.

```
shared/workspaces/
├── workspaces.json              # Central registry of all workspaces
├── workspaces_schema.json       # Validation schema
└── {workspace-id}/              # Workspace home directory
    ├── capabilities/            # Capability artifacts
    ├── outcomes/                # Outcome artifacts (queued/in-progress/completed)
    └── status/                  # Summary files and snapshots
```

### Subscriber Model

Multiple projects can subscribe to the same workspace with different access levels:

- **read**: View workspace, list projects
- **write**: Add/remove projects, create artifacts
- **admin**: Delete workspace, manage subscribers

## Commands

### Project Management

#### `/workspace:init [workspace-name]`
Initialize a new multi-project workspace.

Creates workspace entry in shared registry, workspace home directory with subdirectories (capabilities/, outcomes/, status/), and subscribes current project as admin.

#### `/workspace:subscribe [workspace-id]`
Subscribe current project to an existing shared workspace.

Registers this plugin instance as a subscriber, enabling access to all workspace projects and settings.

#### `/workspace:unsubscribe [workspace-id]`
Remove current project's subscription from a workspace.

Preserves workspace and its projects (only removes subscription).

#### `/workspace:add [project-path or git-url]`
Add an existing project or repository to the current workspace.

Supports local paths or git URLs (will clone if URL provided).

#### `/workspace:remove [project-name]`
Remove a project from workspace configuration.

Preserves project files on disk (configuration only).

#### `/workspace:list [--verbose | --json]`
Display all projects in subscribed workspaces.

Options:
- `--verbose`: Detailed project information
- `--json`: JSON output

#### `/workspace:switch [project-name]`
Switch working context to a specific project.

Changes directory, loads project-specific configurations, and displays project overview.

### Validation & Health

#### `/workspace:health [--fix | --verbose | --phase N]`
Execute comprehensive 8-phase workspace health check.

**Phases:**
1. Capability Directory-Summary Sync
2. Outcome Directory-Summary Sync
3. Cross-Reference Integrity
4. Index Validation & Rebuild
5. Temporal Health Checks
6. Temp File Cleanup
7. Git Health Check
8. Comprehensive Report

**Options:**
- `--fix`: Auto-repair issues
- `--verbose`: Detailed output
- `--phase N`: Run specific phase (1-8)
- `--dry-run`: Preview changes
- `--json`: JSON output

**Output Format:**
```
/workspace:health: [HEALTHY|ISSUES] | Fixes: N | Cap: N (M%) | Out: Q/I/C | Proj: N

Issues Found: 2 (0 critical, 1 high, 1 medium)
- HIGH: Broken reference in outcome 005-auth
- MEDIUM: Stale index entry for deprecated capability
```

#### `/workspace:validate [--schemas | --refs | --all]`
Deep validation of workspace configurations.

Validates:
- JSON schemas for all tracking files
- @ file references in instruction files
- Project map compliance
- Naming pattern compliance

**Options:**
- `--schemas`: Validate JSON schemas only
- `--refs`: Validate @ references only
- `--all`: Full validation (default)

#### `/workspace:resolve <project:module[/subpath][#entry]>`
Resolve module references to absolute paths.

**Reference Patterns:**

| Pattern | Example | Description |
|---------|---------|-------------|
| project:module | luon:neo4j_service | Module in specific project |
| module_id | neo4j_service | Search all projects (if unique) |
| project:module/subpath | luon:neo4j_service/cypher | Subpath within module |
| project:module#entry | luon:neo4j_service#CypherLoader | Entry point file |

## Usage Examples

### Initialize and Subscribe

```bash
# Create a new workspace
/workspace:init platform-services

# Subscribe another project to the workspace
cd /path/to/another/project
/workspace:subscribe platform-services
```

### Health Checks

```bash
# Run health check
/workspace:health --verbose

# Auto-fix issues
/workspace:health --fix

# Run specific phase
/workspace:health --phase 3
```

### Navigation

```bash
# List all projects
/workspace:list

# Switch to a project
/workspace:switch api-gateway

# Resolve module path
/workspace:resolve luon:neo4j_service#CypherLoader
```

### Validation

```bash
# Full validation before commit
/workspace:validate --all

# Check schemas only
/workspace:validate --schemas

# Check references only
/workspace:validate --refs
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

## Naming Conventions

| Entity | Pattern | Example |
|--------|---------|---------|
| Capability ID | `^[a-z0-9]+(-[a-z0-9]+)*$` | `auth-system` |
| Outcome Dir | `^[0-9]+-[a-z0-9-]+$` | `001-setup-auth` |
| Child Outcome | `^[0-9]+\.[0-9]+-[a-z0-9-]+$` | `001.1-oauth` |
| Module ID | `^[a-z][a-z0-9_]*$` | `neo4j_service` |

## Integration with Lucid Toolkit

| Plugin | Uses Workspace For |
|--------|-------------------|
| **capability** | `{workspace-home}/capabilities/` |
| **outcome** | `{workspace-home}/outcomes/` |
| **context** | Session tracking, workspace context |

## Schemas

- `workspaces_schema.json` - Shared registry validation
- `workspace_schema.json` - Local workspace configuration
- `project_map_schema.json` - Project navigation and module lookup

## File Structure

```
plugins/workspace/
├── plugin.json              # Plugin metadata
├── README.md               # This file
├── commands/               # Slash commands
│   ├── init.md            # Initialize workspace
│   ├── subscribe.md       # Subscribe to workspace
│   ├── unsubscribe.md     # Leave workspace
│   ├── add.md             # Add project
│   ├── remove.md          # Remove project
│   ├── list.md            # List projects
│   ├── switch.md          # Switch context
│   ├── health.md          # 8-phase health check
│   ├── validate.md        # Schema/ref validation
│   └── resolve.md         # Module resolution
└── schemas/
    ├── workspace_schema.json      # Workspace configuration schema
    └── project_map_schema.json    # Project map schema
```
