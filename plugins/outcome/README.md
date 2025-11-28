# Outcome Plugin

Lifecycle management for tactical work units (outcomes) that build strategic capabilities.

## Overview

The Outcome plugin implements a complete workflow for creating, tracking, and completing work units in capability-driven development. Outcomes represent discrete pieces of work with observable behavioral effects and measurable contributions to capability maturity.

## Installation

Add the Lucid Toolkit marketplace:

```bash
/plugin marketplace add rayk/lucid-toolkit
```

Install the outcome plugin:

```bash
/plugin install outcome@lucid-toolkit
```

## Prerequisites

- Python 3.11+
- Claude Code 1.0.0+
- Shared CLI library installed:

```bash
cd shared/cli-commons && pip install -e .
```

## Core Concepts

### What is an Outcome?

An outcome is a unit of tactical work that:
- Describes WHAT to achieve (not HOW to implement)
- Specifies observable effects in Given-When-Then format
- Links to capabilities with maturity contribution percentages
- Links to at least one project from project_map.json
- Progresses through a defined lifecycle: queued → ready → in-progress → completed

### Lifecycle States

| State | Directory | Description |
|-------|-----------|-------------|
| queued | `0-queued/` | Valid outcome statement exists |
| ready | `1-ready/` | Has design docs, dependencies satisfied |
| in-progress | `2-in-progress/` | Active work is happening |
| blocked | `3-blocked/` | External blocker preventing progress |
| completed | `4-completed/` | All observable effects verified |

### Parent-Child Outcomes

Outcomes can be hierarchical:
- Parent outcomes aggregate related child outcomes
- Children are nested under parent directory: `outcomes/2-in-progress/005-parent/005.1-child/`
- Parent owns `capabilityContributions`, children have `parentContribution` percentages
- Parent can't complete until all children reach success state
- Capability maturity updates only when parent completes

## Commands

### /outcome:create [outcome-name or description]

Create a new outcome with proper structure and schema validation.

**Requires:**
- Achievement description (WHAT to accomplish)
- At least 2 observable effects (Given-When-Then format)
- Primary capability contribution with maturity percentage
- At least one project linkage
- At least one actor involvement

**Creates:**
- `outcomes/0-queued/{NNN}-{name}/outcome_track.json`
- `outcomes/0-queued/{NNN}-{name}/outcome-statement.md`
- `reports/` and `evidence/` subdirectories

### /outcome:design <outcome-directory-label> [description]

Create or update design documents for an outcome. Idempotent - safe to run multiple times.

**Generates:**
- `design/solution_design.md` - What we're building and why
- `design/implementation_design.md` - How we'll build it
- Task breakdown in outcome_track.json

### /outcome:focus <outcome-id or directory-label>

Focus on a queued/ready outcome to begin work. Transitions outcome to in-progress state and loads context.

**Process:**
- Moves outcome from queued/ready to in-progress
- Updates all cross-references
- Loads outcome context into session
- Registers outcome in session tracking

### /outcome:defocus

Remove focus from current outcome(s) without changing state. Outcomes remain in-progress.

### /outcome:move <outcome-ids...> [--to <target-state>]

Move outcomes between states with full cross-reference updates.

**Updates:**
- outcome_track.json (state field)
- Physical directory location
- All capability_track.json references
- outcome_summary.json and capability_summary.json

### /outcome:complete <outcome-id or directory-label>

Complete an in-progress outcome, moving it to completed state and updating capability maturity.

**Validates:**
- All observable effects verified
- All tasks in success state
- For parent outcomes: all children in success state

### /outcome:edit <outcome-id> [field-to-edit]

Edit outcome properties while maintaining schema compliance.

**Editable:**
- Core properties (description, purpose, scope)
- Observable effects (add, edit, remove, verify)
- Capability contributions
- Project associations
- Dependencies
- Actor involvements

### /outcome:decompose <outcome-directory-label>

Decompose an outcome into child outcomes while preserving capability contributions.

**Process:**
- Creates child directories nested under parent
- Parent retains capability contributions
- Children get `parentContribution` percentages (must sum to 100%)
- Parent becomes type "parent", children remain type "atomic"

### /outcome:delete <outcome-directory-label>

Delete an outcome and clean up all cross-references.

**Cleanup:**
- Removes outcome directory
- Updates capability builtByOutcomes arrays
- Updates outcome_summary.json
- Updates dependent outcomes

## Skills

### focus

Handles the outcome focus transition workflow. Invoked by `/outcome:focus` command.

**Responsibilities:**
1. Move outcome to in-progress state
2. Update all tracking files
3. Load context (design docs, linked modules)
4. Present ready message

## Directory Structure

```
outcomes/
├── 0-queued/
│   └── 001-jwt-authentication/
│       ├── outcome_track.json
│       ├── outcome-statement.md
│       ├── reports/
│       └── evidence/
├── 1-ready/
├── 2-in-progress/
│   └── 010-security-vulnerabilities/   # Parent outcome
│       ├── outcome_track.json
│       ├── outcome-statement.md
│       ├── design/
│       │   ├── solution_design.md
│       │   └── implementation_design.md
│       ├── 010.1-sql-injection/        # Child (nested)
│       │   ├── outcome_track.json
│       │   └── outcome-statement.md
│       └── 010.2-xss-prevention/       # Child (nested)
│           ├── outcome_track.json
│           └── outcome-statement.md
├── 3-blocked/
└── 4-completed/
```

## Schemas

### outcome_track_schema.json (v2.1.0)

Defines machine-readable tracking structure:
- Outcome metadata (id, name, directoryLabel, state)
- Capability contributions with maturity percentages
- Project linkages with involvement types
- Observable effects with verification methods
- Parent-child relationships
- Tasks with execution tracking
- Actor involvements
- Execution log with artifact tracking

### outcome_summary_schema.json (v1.0.0)

Summary index for quick lookups:
- All outcomes with current state
- Directory locations
- Capability mappings
- Project associations

## Templates

- **outcome-statement-template.md** - Human-readable outcome definition
- **solution_design.md** - Solution architecture and approach
- **implementation_design.md** - Technical implementation details
- **auto_execution_plan.md** - Autonomous execution plan
- **collab_execution_plan.md** - Collaborative execution plan with handoff points

## Observable Effects

Observable effects prove outcome completion. They must:
- Be written in Given-When-Then format
- Describe behavioral changes (NOT implementation artifacts)
- Specify actor perspective
- Define verification method

**Good Examples:**
- "Given a registered user with valid credentials, When they submit login, Then they receive a session token"
- "Given the system is deployed, When a security scan runs, Then zero critical vulnerabilities are detected"

**Bad Examples:**
- "Tests pass" (implementation artifact)
- "Code is reviewed" (process prescription)
- "System is improved" (vague, not verifiable)

## Naming Conventions

| Entity | Pattern | Example |
|--------|---------|---------|
| Outcome Dir (parent) | `^[0-9]+-[a-z0-9-]+$` | `005-ontology-workflow` |
| Outcome Dir (child) | `^[0-9]+\.[0-9]+-[a-z0-9-]+$` | `005.1-ontology-testing` |
| Capability ID | `^[a-z0-9]+(-[a-z0-9]+)*$` | `auth-system` |

## Usage Example

```bash
# Create a new outcome
/outcome:create "JWT authentication for auth-service"

# Design the solution
/outcome:design 001-jwt-authentication

# Move to ready state
/outcome:move 001-jwt-authentication --to ready

# Focus on the work
/outcome:focus 001-jwt-authentication

# Work happens here...

# Complete the outcome
/outcome:complete 001-jwt-authentication
```

## Integration

This plugin integrates with:
- **capability plugin** - For capability tracking and maturity updates
- **project_map.json** - For project and module references
- **workspace schemas** - For validation and integrity checks

## Cross-Reference Integrity

The outcome workflow maintains referential integrity across:
- **Capability tracks**: `builtByOutcomes` arrays point to outcome paths
- **Outcome summary**: Central index of all outcomes
- **Capability summary**: Aggregated capability maturity view
- **Outcome dependencies**: `outcomeDependencies` and `enables` arrays

When outcomes move between states or are deleted, all cross-references update atomically.

## License

Part of the Lucid Toolkit.
