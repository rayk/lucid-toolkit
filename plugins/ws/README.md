# ws Plugin

Capability-based software development workspace management.

## Overview

The `ws` plugin provides unified workspace management for capability-driven development. It consolidates functionality across five key areas into a single, cohesive plugin:

| Area | Prefix | Purpose |
|------|--------|---------|
| Capabilities | `cap:` | Strategic goals with maturity tracking |
| Outcomes | `out:` | Tactical work units that build capabilities |
| Designs | `des:` | Technical specifications (planned) |
| Plans | `plan:` | Implementation planning |
| Execution | `exe:` | Plan execution and tracking |

## Installation

```bash
/plugin install ws@lucid-toolkit
```

Requires the shared CLI library for hooks:
```bash
cd shared/cli-commons && pip install -e .
```

## Commands

### Workspace Management

| Command | Description |
|---------|-------------|
| `/ws:version` | Display plugin version and recent changelog |
| `/ws:enviro` | Idempotent environment setup, repair, migration, and status reporting |
| `/ws:report-bug` | Report misbehavior for later debugging |

### Capabilities (`cap:`)

Capabilities represent strategic goals with measurable maturity percentages.

| Command | Description |
|---------|-------------|
| `/cap:create` | Create a capability statement following workspace standards |
| `/cap:list` | List all capabilities with status and maturity overview |
| `/cap:check` | Validate a capability against workspace standards |
| `/cap:edit` | Edit an existing capability statement |
| `/cap:delete` | Delete a capability with dependency checking |
| `/cap:merge` | Merge multiple capabilities into one |
| `/cap:split` | Split a capability into smaller capabilities |

### Outcomes (`out:`)

Outcomes are tactical work units that contribute to capability maturity.

| Command | Description |
|---------|-------------|
| `/out:create` | Create an outcome with capability linkage |
| `/out:check` | Validate an outcome against workspace standards |

### Plans (`plan:`)

| Command | Description |
|---------|-------------|
| `/plan:create` | Create an implementation plan |

### Execution (`exe:`)

| Command | Description |
|---------|-------------|
| `/exe:list` | List execution plans |
| `/exe:stage` | Stage an execution plan |

## Skills

Skills provide reusable workflows that can be invoked by commands or directly.

| Skill | Description |
|-------|-------------|
| `git-commits` | Generates well-structured commits with architectural scope and purpose documentation |
| `capability-index-sync` | Synchronizes capability indexes after modifications |
| `outcome-index-sync` | Synchronizes outcome indexes after modifications |

## Subagents

Specialized agents handle complex validation and file production tasks.

| Agent | Description |
|-------|-------------|
| `capability-checker` | Validates capability statements for schema compliance, content quality, spelling, grammar, and markdown lint |
| `outcome-checker` | Validates outcome definitions for adequacy, decomposition quality, and capability alignment |
| `toon-specialist` | Produces, validates, and parses TOON files using schema.org vocabulary |

## Hooks

Lifecycle hooks provide automation and safety nets.

| Hook | Trigger | Purpose |
|------|---------|---------|
| `session_start.py` | SessionStart | Initialize workspace context |
| `focus_tracker.py` | PostToolUse | Track focus and activity |
| `capability_sync.py` | PostToolUse | Mark indexes stale when capability files are modified outside commands |

## Data Files

The plugin manages structured data files in `.claude/`:

| File | Purpose |
|------|---------|
| `workspace-info.toon` | Main workspace snapshot |
| `capabilities-info.toon` | Capabilities index |
| `outcomes-info.toon` | Outcomes index |
| `execution-info.toon` | Execution tracking |

All `.toon` files use schema.org vocabulary and are produced exclusively by the `toon-specialist` agent.

## Schemas

TOON schemas are located in `shared/schemas/` for reuse across plugins:

| Schema | Purpose |
|--------|---------|
| `workspace-info-schema.toon` | Main workspace snapshot structure |
| `capabilities-info-schema.toon` | Capabilities index structure |
| `outcomes-info-schema.toon` | Outcomes index structure |
| `execution-info-schema.toon` | Execution tracking structure |
| `core-values-schema.toon` | 34-value framework reference data |
| `actor-registry-schema.toon` | Actor definitions reference data |

## Key Concepts

### Capability-Driven Development

- **Capabilities** define strategic goals with maturity percentages (0-100%)
- **Outcomes** are tactical work units that contribute to capability maturity
- When an outcome completes, its contribution flows up to increase capability maturity

### Outcome Hierarchy

Outcomes can be organized hierarchically:

```
outcomes/
├── 005-parent-outcome/
│   ├── outcome_track.json
│   ├── outcome-statement.md
│   ├── 005.1-child-outcome/
│   │   ├── outcome_track.json
│   │   └── outcome-statement.md
│   └── 005.2-another-child/
│       ├── outcome_track.json
│       └── outcome-statement.md
```

- Parent outcomes aggregate children via `parentContribution` percentages
- Child contributions must sum to 100%
- Only parent outcomes define `capabilityContributions`

### TOON Format

TOON (Tabular Object-Oriented Notation) is a compact format using schema.org vocabulary:

```toon
@type: Capability
@id: cap/auth-system
name: Authentication System
maturity: 45
status: active
```

## Naming Conventions

| Entity | Pattern | Example |
|--------|---------|---------|
| Capability ID | `^[a-z0-9]+(-[a-z0-9]+)*$` | `auth-system` |
| Outcome Directory | `^[0-9]+-[a-z0-9-]+$` | `005-ontology` |
| Child Outcome | `^[0-9]+\.[0-9]+-[a-z0-9-]+$` | `005.1-testing` |

## Version

Current version: **0.8.0**

See [CHANGELOG.md](CHANGELOG.md) for release history.
