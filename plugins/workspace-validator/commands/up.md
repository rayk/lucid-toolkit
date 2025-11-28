---
description: Update workspace - sync projects, reconcile sessions, validate schemas
executionMode: self-delegating
---

IMPORTANT: This command MUST delegate to preserve context. Do NOT execute scripts directly.

Delegate to subagent:

```
Task(general-purpose, haiku):
"Execute workspace health check and session reconciliation.

Run in parallel:
1. python3 scripts/workspace_health.py --fix --json
2. python3 hooks/session_summary/reconcile_cli.py --json

Then verify project sync: compare .idea/jb-workspace.xml against project_map.json.

Apply project_map_validation rules (see below) if mismatches found.

Then verify module sync:
- For each project with modules[], check paths exist
- Report any stale modules (path doesn't exist) or missing modules (discoverable but not listed)
- Use discovery rules from /project:scan command

@return compact report ONLY (no verbose output, no source dumps):
/up: [HEALTHY|ISSUES] | Fixes: N | Cap: N (M%) | Out: Q/I/C | Sess: N | Proj: N/M valid | Mod: N
[Only if issues] WARN: brief description
[Only if project sync needed] SYNC: added/removed project names
[Only if schema issues] SCHEMA: project names with missing required fields

@constraints:
- maxTokens: 2000
- format: structured-summary-only
- suppress verbose phase details and Python output"
```

Return only the compact report to user.

<project_map_validation>
## Project Map Schema Compliance

For each project in `project_map.json`, validate against `schemas/project_map_schema.json`:

### Required Fields (MUST exist)
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Project name |
| `path` | string | Path relative to workspace root |
| `description` | string | What project does and its purpose |
| `technology` | object | Tech stack (see below) |
| `keyDirectories` | object | Important directories |
| `entryPointFiles` | array | Key files to read first |

### Technology Object
```json
{
  "languages": ["Dart", "Python"],    // Array, not singular
  "frameworks": ["Flutter", "FastAPI"], // Array, not singular
  "buildTool": "Melos"
}
```

### keyDirectories Object (Required)
```json
{
  "source": "apps/lucid_home/lib",
  "tests": "apps/lucid_home/test",
  "documentation": "apps/lucid_home/architecture",
  "configuration": "apps/lucid_home",
  "build": "apps/lucid_home/build"
}
```

### entryPointFiles Array (Required)
```json
[
  {"name": "README.md", "path": "README.md", "purpose": "Project overview"},
  {"name": "pubspec.yaml", "path": "pubspec.yaml", "purpose": "Dependencies"}
]
```

### Optional Fields
| Field | Type | Values |
|-------|------|--------|
| `scope` | string | Capability/domain (e.g., "user-applications") |
| `status` | enum | `active` \| `planned` \| `archived` |

### Fix Actions
For each project missing required fields:
1. Read the project's actual structure (explore if needed)
2. Populate `keyDirectories` with actual paths
3. Populate `entryPointFiles` with key files (README, config, architecture docs)
4. Fix `technology` format: `language`→`languages[]`, `framework`→`frameworks[]`
5. Remove non-schema fields: `absolutePath`, `type`, `structure`, `packages`, `versionManager`
6. Add `scope` and `status` for completeness
</project_map_validation>

<report>
Output a **single compact report** (no tables, no verbose phase details):

```
/up: [HEALTHY|ISSUES] | Fixes: N | Cap: N (M%) | Out: Q/I/C | Sess: N | Proj: N/M valid
[Only if issues] WARN: brief description
[Only if project sync needed] SYNC: added/removed project names
[Only if schema issues] SCHEMA: project names with missing required fields
```

Example healthy: `/up: HEALTHY | Fixes: 1 | Cap: 2 (45%) | Out: 1/2/5 | Sess: 3 | Proj: 2/2 valid | Mod: 10`
Example issues: `/up: ISSUES | Fixes: 0 | Cap: 1 (0%) | Out: 0/0/0 | Sess: 1 | Proj: 0/2 valid | Mod: 8`
              `WARN: 2 broken cross-refs in capability-x`
              `SCHEMA: user_apps missing keyDirectories, entryPointFiles`
              `MOD: luon:old_module path missing, user_apps has 1 undiscovered module`
</report>

<on_error>
- Schema validation: read schema, fix JSON manually
- Broken cross-refs: check deleted capability/outcome references
- Permission: check status/ write access
- Import error: `pip3 install jsonschema`
- Preview: `--dry-run` | Single phase: `--phase N` | JSON: `--json`
- Project schema: read `schemas/project_map_schema.json`, explore project, update entry
</on_error>
