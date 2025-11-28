# Shared Workspaces

Central registry and home directories for multi-project workspaces that can be accessed by any project with the workspace plugin installed.

## Purpose

When the workspace plugin is installed in multiple projects, this shared directory enables:

1. **Workspace Discovery** - Projects can discover and subscribe to existing workspaces
2. **Cross-Project Coordination** - Multiple projects share workspace configuration
3. **Shared Artifacts** - Capabilities and outcomes stored in workspace home directories
4. **Subscriber Tracking** - Know which plugin instances are using each workspace

## Directory Structure

```
shared/workspaces/
├── workspaces.json               # Central registry of all workspaces
├── workspaces_schema.json        # Validation schema
├── README.md                     # This documentation
│
├── {workspace-id}/               # Workspace home directory (created per workspace)
│   ├── capabilities/             # Capability artifacts (used by capability-workflow)
│   │   ├── {capability-id}/
│   │   │   ├── capability_track.json
│   │   │   └── capability-statement.md
│   │   └── ...
│   ├── outcomes/                 # Outcome artifacts (used by outcome-workflow)
│   │   ├── queued/
│   │   ├── in-progress/
│   │   └── completed/
│   └── status/                   # Summary files
│       ├── capability_summary.json
│       ├── outcome_summary.json
│       └── capability_snapshot.md
│
└── {another-workspace-id}/       # Another workspace home
    ├── capabilities/
    ├── outcomes/
    └── status/
```

## How It Works

### 1. Creating a Workspace

When `/workspace:init my-workspace` is run:

1. Creates workspace entry in `workspaces.json`
2. Creates workspace home directory: `shared/workspaces/my-workspace/`
3. Creates subdirectories: `capabilities/`, `outcomes/`, `status/`
4. Subscribes current project as admin

```json
{
  "id": "my-workspace",
  "name": "My Workspace",
  "homePath": "shared/workspaces/my-workspace/",
  "directories": {
    "capabilities": "capabilities/",
    "outcomes": "outcomes/",
    "status": "status/"
  },
  "projects": [...],
  "subscribers": [...]
}
```

### 2. Subscribing to a Workspace

When a project runs `/workspace:subscribe my-workspace`:

1. Adds subscriber entry to workspace in registry
2. Gains access to workspace home directory
3. Can use capability-workflow and outcome-workflow within that workspace

### 3. Plugin Integration

**capability-workflow plugin** uses:
- `{workspace-home}/capabilities/` - Stores capability definitions
- `{workspace-home}/status/capability_summary.json` - Capability index

**outcome-workflow plugin** uses:
- `{workspace-home}/outcomes/` - Stores outcome artifacts by state
- `{workspace-home}/status/outcome_summary.json` - Outcome index

## Workspace Home Directory

Each workspace has its own home directory named after the workspace ID:

| Directory | Purpose | Plugin |
|-----------|---------|--------|
| `capabilities/` | Capability definitions and tracking | capability-workflow |
| `outcomes/` | Outcome artifacts organized by state | outcome-workflow |
| `status/` | Summary files and snapshots | Both |

### Capabilities Directory

```
capabilities/
├── authentication-system/
│   ├── capability_track.json
│   └── capability-statement.md
├── billing-integration/
│   ├── capability_track.json
│   └── capability-statement.md
└── ...
```

### Outcomes Directory

```
outcomes/
├── queued/
│   └── 001-basic-auth/
│       ├── outcome_track.json
│       └── outcome-statement.md
├── in-progress/
│   └── 002-session-mgmt/
│       └── ...
└── completed/
    └── 003-password-policy/
        └── ...
```

### Status Directory

```
status/
├── capability_summary.json    # Index of all capabilities
├── outcome_summary.json       # Index of all outcomes
└── capability_snapshot.md     # Pre-rendered capability overview
```

## Registry Files

| File | Purpose |
|------|---------|
| `workspaces.json` | Registry of all shared workspaces |
| `workspaces_schema.json` | JSON Schema for validation |

## Subscriber Model

Each plugin instance that subscribes to a workspace is tracked:

| Field | Description |
|-------|-------------|
| `instanceId` | Unique ID for the plugin instance |
| `projectPath` | Where the plugin is installed |
| `subscribedAt` | When subscription occurred |
| `lastAccess` | Most recent workspace access |
| `accessLevel` | Permission level (read/write/admin) |

## Access Levels

| Level | Capabilities |
|-------|--------------|
| `read` | View workspace, list projects, read artifacts |
| `write` | Add/remove projects, create/modify capabilities and outcomes |
| `admin` | Delete workspace, manage subscribers |

## Cross-Plugin Coordination

When capability-workflow and outcome-workflow operate on a workspace:

1. **Workspace Resolution**: Plugins resolve workspace from current project subscription
2. **Path Resolution**: Use `homePath` + `directories.capabilities` or `directories.outcomes`
3. **Cross-References**: Outcomes reference capabilities by path within workspace home
4. **Summary Updates**: Both plugins update status files in `{workspace-home}/status/`

### Example: Creating a Capability

```
/capability:create authentication-system
```

1. Plugin checks current project's workspace subscription
2. Resolves path: `shared/workspaces/my-workspace/capabilities/authentication-system/`
3. Creates `capability_track.json` and `capability-statement.md`
4. Updates `shared/workspaces/my-workspace/status/capability_summary.json`

### Example: Creating an Outcome

```
/outcome:create basic-authentication
```

1. Plugin checks current project's workspace subscription
2. Resolves path: `shared/workspaces/my-workspace/outcomes/queued/001-basic-authentication/`
3. Creates `outcome_track.json` with capability contribution references
4. Updates `shared/workspaces/my-workspace/status/outcome_summary.json`
