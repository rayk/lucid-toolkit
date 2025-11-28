# Workspace Validator Plugin

Validates and maintains health of multi-project Claude Code workspaces.

## Overview

This plugin provides tools for validating workspace structure, checking cross-references, and maintaining project mappings across multi-repository setups.

## Components

### Commands

| Command | Description |
|---------|-------------|
| `/up` | Update workspace - sync projects, reconcile sessions, validate schemas |
| `/project:resolve` | Resolve module references across project boundaries |
| `/tools:analyze` | Deep analysis of workspace claude prompts, configurations, and scripts |

### Scripts

| Script | Purpose |
|--------|---------|
| `workspace_health.py` | Validates workspace health, checks for broken references, validates schemas |
| `validate_refs.py` | Validates cross-references between capabilities, outcomes, and tracking files |

### Schemas

| Schema | Validates |
|--------|-----------|
| `project_map_schema.json` | Project map structure and module definitions |
| `actor_summary_schema.json` | Actor/session tracking data |

## Use Cases

- Multi-project workspace coordination
- Cross-reference integrity validation
- Project mapping and module resolution
- Workspace health monitoring
- Schema validation for tracking files

## Dependencies

- Python 3.8+
- JSONSchema validation library
- Git (for project sync operations)

## Installation

Install as a Claude Code plugin by placing in `lucid-toolkit/plugins/workspace-validator/`

## Usage

```bash
# Update entire workspace
/up

# Resolve a module reference
/project:resolve luon:neo4j_service

# Analyze workspace configuration
/tools:analyze
```

## Related Plugins

- **outcome-workflow**: Uses workspace validation for outcome tracking
- **capability-workflow**: Requires workspace validation for capability cross-refs
- **session-manager**: Integrates with workspace health checks
