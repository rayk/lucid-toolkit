# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Lucid Toolkit is a Claude Code plugin marketplace implementing capability-driven development workflows. Plugins are modular and installable independently via the Claude Code plugin system.

## Installation Commands

```bash
# Add marketplace
/plugin marketplace add rayk/lucid-toolkit

# Install specific plugin
/plugin install capability-workflow@lucid-toolkit

# Install shared CLI library (required for hooks/scripts)
cd shared/cli-commons && pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"
```

## Testing Commands

```bash
# Run tests for CLI commons
cd shared/cli-commons && pytest

# With coverage
pytest --cov=lucid_cli_commons
```

## Architecture

### Plugin Structure

Each plugin under `plugins/` follows this structure:
```
plugins/{name}/
├── plugin.json          # Plugin metadata and command/skill declarations
├── commands/            # Slash commands (*.md with YAML frontmatter)
├── skills/              # Skills (SKILL.md files with XML structure)
├── hooks/               # Python lifecycle scripts
├── agents/              # Subagent configurations (*.md)
├── templates/           # File templates
└── schemas/             # JSON schemas for validation
```

### Available Plugins (8)

**Core Workflow:**
- `capability-workflow` - Strategic capability management with maturity tracking (capabilities → outcomes)
- `outcome-workflow` - Outcome lifecycle (queued → ready → in-progress → blocked → completed)
- `session-manager` - Session lifecycle tracking

**Analysis & Development:**
- `thinking-tools` - Mental models (consider, assess, reflect commands)
- `maker-toolkit` - Build skills, commands, and agents with quality auditing
- `workspace-validator` - Schema validation and health checks
- `planner` - TDD execution prompt generator with model delegation

**Best Practices:**
- `delegation-protocol` - Context-saving patterns (delegate 3+ ops to subagents)

### Shared Library

`shared/cli-commons/` provides Python utilities for plugin hooks:
- `lucid_cli_commons.schema` - JSON Schema validation
- `lucid_cli_commons.git` - Git operations
- `lucid_cli_commons.fs` - Atomic file writes, path utilities
- `lucid_cli_commons.crossref` - Cross-reference management

### Key Patterns

**Capability-Driven Development:**
- Capabilities = strategic goals measured by maturity percentage
- Outcomes = tactical work units that build capabilities
- Outcomes define `capabilityContributions` with maturity percentages
- When outcome completes, capability maturity increases

**Outcome Hierarchy:**
- Parent outcomes aggregate children (nested directories: `005-parent/005.1-child/`)
- Children have `parentContribution` %, parent owns `capabilityContributions`
- Parent moves → all children move together

**Delegation Protocol:**
- Count operations before classifying requests
- 3+ tool calls → delegate to subagent
- Specific user input ≠ simple solution (the "specificity trap")

**Skills vs Commands:**
- Skills (SKILL.md): Interactive guidance with progressive disclosure, XML structure
- Commands (*.md): Executable workflows with YAML frontmatter, arguments

### Token Budget Guidelines (from delegation-protocol)

| Operation Type | Budget | Model |
|----------------|--------|-------|
| File search, pattern matching | 1500 | haiku |
| Yes/no validation | 800 | haiku |
| Code analysis, flow tracing | 2000 | sonnet |
| Multi-file fix + commit | 2500 | sonnet |
| Synthesis, complex reasoning | 3000 | opus |

## Naming Conventions

| Entity | Pattern | Example |
|--------|---------|---------|
| Capability ID | `^[a-z0-9]+(-[a-z0-9]+)*$` | `auth-system` |
| Outcome Dir | `^[0-9]+-[a-z0-9-]+$` | `005-ontology-workflow` |
| Child Outcome | `^[0-9]+\.[0-9]+-[a-z0-9-]+$` | `005.1-ontology-testing` |

## Cross-Reference Integrity

When modifying tracking files, maintain referential integrity across:
- `capabilities/*/capability_track.json` - Individual capability state
- `outcomes/*/outcome_track.json` - Outcome state and capability links
- `status/capability_summary.json` - Central capability index
- `status/outcome_summary.json` - Central outcome index