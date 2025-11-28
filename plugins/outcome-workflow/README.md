# Outcome Workflow Plugin

A Claude Code plugin for managing capability-driven development through outcome-based work units.

## Overview

The Outcome Workflow plugin implements a complete lifecycle for tracking tactical work units (outcomes) that build strategic capabilities. Each outcome represents a discrete piece of work with observable behavioral effects and contributions to capability maturity.

## Core Concepts

### What is an Outcome?

An outcome is a unit of tactical work that:
- Describes **WHAT** to achieve (not HOW to implement)
- Specifies observable effects (behavioral changes proving completion)
- Links to capabilities with maturity contribution percentages
- Links to at least one project from project_map.json
- Moves through a defined lifecycle from queued → ready → in-progress → completed

### Outcome Lifecycle States

Outcomes progress through five states, each with its own directory:

| State | Directory | Entry Gate | Description |
|-------|-----------|------------|-------------|
| **queued** | `0-queued/` | Created with definition | Valid outcome statement exists |
| **ready** | `1-ready/` | Design complete + deps satisfied | Has design docs, all dependencies in completed state |
| **in-progress** | `2-in-progress/` | User runs /outcome:focus | Active work is happening |
| **blocked** | `3-blocked/` | Blocker identified | External blocker preventing progress |
| **completed** | `4-completed/` | All effects verified | Done, all observable effects achieved |

### Parent-Child Outcomes

Outcomes can be hierarchical:

- **Parent outcomes** aggregate multiple related child outcomes
- **Child outcomes** are physically nested under parent directory: `outcomes/2-in-progress/005-parent/005.1-child/`
- Parent and children share ONE classification directory (move as unit)
- Parent blocked → all children blocked (cascade effect)
- Parent can't complete until all children state=success

**Contribution Model:**
- Parent outcomes OWN `capabilityContributions` (e.g., +15% to capability)
- Child outcomes have `capabilityContributions: []` (empty)
- Children declare `parentContribution` as % of parent's work (must sum to 100%)
- Capability maturity updates ONLY when parent completes (all children done)
- Capability's `builtByOutcomes` only references parent, not children

## Directory Structure

```
outcomes/
├── 0-queued/
│   └── 001-jwt-authentication/
│       ├── outcome_track.json          # Machine-readable tracking
│       ├── outcome-statement.md        # Human-readable definition
│       ├── reports/                    # Execution reports
│       └── evidence/                   # Verification evidence
├── 1-ready/
├── 2-in-progress/
│   └── 010-security-vulnerabilities/   # Parent outcome
│       ├── outcome_track.json
│       ├── outcome-statement.md
│       ├── design/
│       │   ├── solution_design.md
│       │   └── implementation_design.md
│       ├── 010.1-sql-injection/        # Child outcome (nested)
│       │   ├── outcome_track.json
│       │   └── outcome-statement.md
│       └── 010.2-xss-prevention/       # Child outcome (nested)
│           ├── outcome_track.json
│           └── outcome-statement.md
├── 3-blocked/
└── 4-completed/
```

## Naming Patterns

| Entity | Pattern | Example |
|--------|---------|---------|
| Capability ID | `^[a-z0-9]+(-[a-z0-9]+)*$` | `auth-system` |
| Outcome Dir (parent) | `^[0-9]+-[a-z0-9-]+$` | `005-ontology-workflow` |
| Outcome Dir (child) | `^[0-9]+\.[0-9]+-[a-z0-9-]+$` | `005.1-ontology-testing` |
| Task File | `^[0-9]{2}-[A-Z*]-[a-z0-9-]+\.md$` | `01-A-implement-jwt.md` |

## Slash Commands

### /outcome:create [outcome-name or description]

Create a new outcome with proper structure, schema validation, capability linkage, and project association.

**Required Information:**
- Achievement description (WHAT to accomplish)
- Purpose (why this outcome is needed)
- At least 2 observable effects in Given-When-Then format
- Primary capability contribution (capabilityId, maturityContribution %, rationale)
- At least one project (projectName, involvement type, affected areas)
- At least one actor involvement (beneficiary, stakeholder, contributor, etc.)

**Output:**
- `outcomes/0-queued/{NNN}-{name}/outcome_track.json`
- `outcomes/0-queued/{NNN}-{name}/outcome-statement.md`
- `outcomes/0-queued/{NNN}-{name}/reports/` directory
- `outcomes/0-queued/{NNN}-{name}/evidence/` directory

### /outcome:design <outcome-directory-label> [description]

Create or update design documents (solution + implementation) for an outcome.

**Generates:**
- `design/solution_design.md` - What we're building and why
- `design/implementation_design.md` - How we'll build it
- Task breakdown in `outcome_track.json`

### /outcome:focus <outcome-id or directory-label>

Focus on a queued/ready outcome to commence work. Transitions outcome to in-progress state, loads context, and prepares work environment.

**Invokes Skill:** `focus` (handles transition workflow)

### /outcome:defocus

Remove focus from current outcome(s) without changing their state - they remain in-progress.

### /outcome:move <outcome-ids...> [--to <target-state>]

Move one or more outcomes between states (queued, ready, in-progress, blocked, completed) with full cross-reference updates.

**Updates:**
- outcome_track.json (state field)
- Physical directory location
- capability_track.json (outcome paths)
- status/outcome_summary.json
- status/capability_summary.json (if completing)

### /outcome:complete <outcome-id or directory-label>

Complete an in-progress outcome - moves to completed state, updates capability maturity.

**Validation:**
- All observable effects must be verified
- All tasks must be in success state
- For parent outcomes: all children must be in success state

### /outcome:edit <outcome-id> [field-to-edit]

Edit an existing outcome's properties, observable effects, capability contributions, or project associations.

### /outcome:delete <outcome-directory-label>

Delete an outcome and clean up all cross-references in capabilities and summaries.

**Cleanup:**
- Removes outcome directory
- Updates capability's builtByOutcomes array
- Updates outcome_summary.json
- Updates dependent outcomes' outcomeDependencies

### /outcome:decompose <outcome-directory-label>

Decompose an outcome into child outcomes while preserving capability contributions.

**Process:**
- Creates child outcome directories nested under parent
- Sets up parent-child contribution model
- Children get `capabilityContributions: []` and `parentContribution: N%`
- Parent retains capability contributions

## Skills

### focus

Handles the outcome focus transition workflow:
1. Move outcome to in-progress state
2. Update all tracking files
3. Load context (design docs, linked modules, etc.)
4. Present ready message

Invoked by `/outcome:focus` command after outcome selection.

## Templates

### outcome-statement-template.md

Human-readable definition template with:
- Achievement description (outcome-focused)
- Purpose statement
- Scope (included/excluded)
- Observable effects (Given-When-Then format)
- Capability contributions
- Project linkages
- Actor involvements

### solution_design.md

Solution architecture template covering:
- Problem statement
- Proposed solution
- Alternative approaches considered
- Technical architecture
- Integration points
- Success criteria

### implementation_design.md

Implementation details template:
- Component breakdown
- Data models
- API contracts
- File structure
- Dependencies
- Testing strategy

### auto_execution_plan.md

Autonomous execution plan for fully automated work:
- Task breakdown with token estimates
- Dependencies and sequencing
- Context requirements
- Target directories

### collab_execution_plan.md

Collaborative execution plan for human-in-the-loop work:
- Milestone-based planning
- Handoff points
- Review gates
- Approval workflows

## Schemas

### outcome_track_schema.json

Machine-readable tracking schema defining:
- Outcome metadata (id, name, directoryLabel, state, etc.)
- Capability contributions with maturity percentages
- Project linkages with involvement types
- Observable effects with verification methods
- Parent-child relationships
- Tasks with execution tracking
- Actors with relationship types
- Execution log with artifact tracking

**Schema Version:** 2.1.0

### outcome_summary_schema.json

Summary index schema for quick lookups:
- All outcomes with current state
- Directory locations
- Capability mappings
- Project associations

## Project Involvement Types

| Type | Description |
|------|-------------|
| **primary** | Main project where the outcome's work is implemented |
| **secondary** | Project affected but not the main focus |
| **integration** | Project involved for integration/compatibility purposes |

## Observable Effects

Observable effects are behavioral changes that prove outcome completion. They must:

- Be written in Given-When-Then format
- Describe behavioral changes (NOT implementation artifacts)
- Specify actor perspective (who can verify)
- Define verification method (how to prove)
- Not include process prescriptions ("tests pass", "code reviewed")

**Good Examples:**
- "Given a registered user with valid credentials, When they submit login, Then they receive a session token and can access protected resources"
- "Given the system is deployed, When a security scan is performed, Then zero critical vulnerabilities are detected"

**Bad Examples:**
- "Tests pass" (implementation artifact)
- "Code is reviewed" (process prescription)
- "System is improved" (vague, not verifiable)

## Anti-Patterns to Avoid

Reject outcomes that contain:

- **Process prescriptions:** "Use TDD", "Follow agile", "Implement with X library"
- **Implementation artifacts as effects:** "Tests pass", "File created", "Code reviewed"
- **Vague achievements:** "Improve", "Enhance", "Optimize" (without quantification)
- **Capability dependencies:** Outcomes BUILD capabilities, don't depend on them

## Validation Checklist

Before creating an outcome, verify:

- [ ] Outcome name matches pattern `^[a-z0-9]+(-[a-z0-9]+){0,4}$`
- [ ] Directory label matches pattern `^[0-9]+-[a-z0-9]+(-[a-z0-9]+){0,4}$`
- [ ] At least 2 observable effects defined
- [ ] At least 1 capability contribution with valid path
- [ ] At least 1 project with valid projectName from project_map.json
- [ ] At least 1 actor involvement specified
- [ ] Achievement description is outcome-focused (no process prescriptions)
- [ ] Token budget within acceptable range (recommend split if >200K)

## Integration with Capabilities

Outcomes are the primary mechanism for building capability maturity:

1. Outcome defines `capabilityContributions` with maturity percentages
2. Capability's `builtByOutcomes` array tracks contributing outcomes
3. When outcome completes, capability maturity increases by contribution amount
4. Capability maturity is sum of all completed outcome contributions
5. For parent outcomes, maturity updates only when all children complete

**Example:**
```json
{
  "capabilityContributions": [
    {
      "capabilityId": "authentication-system",
      "capabilityPath": "capabilities/authentication-system/capability_track.json",
      "maturityContribution": 15,
      "rationale": "Establishes JWT foundation for user authentication",
      "isPrimary": true
    }
  ]
}
```

## Token Budget Estimates

| Level | Token Range | Description |
|-------|-------------|-------------|
| very-low | <25K | Simple, isolated changes |
| low | 25-75K | Single component work |
| average | 75-150K | Multi-component integration |
| high | 150-200K | System-wide changes |
| very-high | >200K | Consider decomposing into parent+children |

## Cross-Reference Integrity

The outcome workflow maintains referential integrity across:

- **Capability tracks:** `builtByOutcomes` arrays point to outcome paths
- **Outcome summary:** Central index of all outcomes
- **Capability summary:** Aggregated capability maturity view
- **Outcome dependencies:** `outcomeDependencies` and `enables` arrays

When outcomes move between states or are deleted, all cross-references must update atomically.

## Usage Example

```bash
# Create a new outcome
/outcome:create "JWT authentication for lucid-auth-service"

# Design the solution
/outcome:design 001-jwt-authentication

# Focus on the work
/outcome:focus 001-jwt-authentication

# Work happens here...

# Complete the outcome
/outcome:complete 001-jwt-authentication
```

## Dependencies

This plugin integrates with:

- **capability-workflow plugin** - For capability tracking and maturity updates
- **project_map.json** - For project and module references
- **workspace schemas** - For validation and integrity checks

## License

Part of the Lucid Toolkit workspace configuration.
