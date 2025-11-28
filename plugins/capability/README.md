# Capability Plugin

Strategic capability management with maturity tracking for capability-driven development workflows.

## Overview

Capabilities represent strategic goals measured by maturity percentage (0-100%). This plugin provides lifecycle management for defining, tracking, and visualizing capabilities and their progression.

### What is a Capability?

A **capability** is a measurable strategic goal that the system can achieve. Capabilities are:
- **Measurable**: Tracked by maturity percentage (0-100%)
- **Strategic**: Aligned to business outcomes and actor needs
- **Composable**: Built from outcomes (atomic) or sub-capabilities (composed)
- **Progressive**: Mature through defined milestones (30%, 60%, 80%, 100%)

### Key Features

- **Comprehensive Definition**: Capture purpose, scope, actors, business values, and maturity milestones
- **Actor Mapping**: Link capabilities to stakeholders with relationship types and criticality levels
- **Business Value Alignment**: Map each capability to 1-3 core business values from a 28-value framework
- **Maturity Tracking**: Define progressive milestones with concrete deliverables at each stage
- **Safe Deletion**: Remove capabilities with complete cross-reference cleanup
- **Fast Snapshots**: View capability hierarchy and health in <100ms from pre-computed cache

## Installation

First, add the Lucid Toolkit marketplace to your Claude Code workspace:

```bash
/plugin marketplace add rayk/lucid-toolkit
```

Then install the capability plugin:

```bash
/plugin install capability@lucid-toolkit
```

### Prerequisites

- Claude Code >=1.0.0
- Python >=3.11 (for hooks and scripts)
- Shared CLI library (required for hooks):

```bash
cd /path/to/lucid-toolkit/shared/cli-commons
pip install -e .
```

## Commands

### `/capability:create [capability-name or description]`

Create a comprehensive capability statement following workspace standards.

**What it does:**
- Guides you through defining a complete capability
- Captures strategic foundation (purpose, type, domain, target maturity)
- Maps actor involvement with relationship types and criticality
- Links to 1-3 core business values with measurable rationale
- Defines maturity milestones (30%, 60%, 80%, 100%) with concrete deliverables
- Establishes measurement criteria with quantified metrics
- Validates against workspace schema requirements

**Example:**
```bash
/capability:create auth-system
/capability:create "secure user authentication"
```

**Output:**
- `capabilities/[capability-id]/capability-statement.md` - Complete capability definition
- `capabilities/[capability-id]/capability_track.json` - Schema-compliant tracking file

---

### `/capability:delete <capability-id>`

Safely delete a capability and clean up all cross-references.

**What it does:**
- Removes capability from `status/capability_summary.json` (all indexes)
- Deletes capability directory from `capabilities/`
- Removes capability references from all outcome tracking files
- Updates `status/outcome_summary.json` to remove capability links
- Ensures no orphaned references remain

**Example:**
```bash
/capability:delete auth-system
```

**Safety:**
- Validates capability exists before deletion
- Updates all cross-references automatically
- Maintains referential integrity across tracking files

---

### `/capability:snapshot`

Generate a hierarchical snapshot of all capabilities showing structure, maturity, and health.

**What it does:**
- Displays pre-computed capability hierarchy from cache
- Shows maturity percentages and health indicators
- Flags blocked and at-risk capabilities
- Performance: <100ms from cache (vs ~16s for LLM generation)
- Auto-regenerates if snapshot file is missing

**Example:**
```bash
/capability:snapshot
```

**Output:**
Displays contents of `capabilities/SNAPSHOT.md` with current capability state.

## Usage Examples

### Creating Your First Capability

```bash
/capability:create authentication-system
```

You'll be guided through:
1. **Identity**: Defining the capability ID and name
2. **Foundation**: Purpose, type (atomic/composed), domain, target maturity
3. **Actors**: Selecting stakeholders and defining their relationships
4. **Business Value**: Mapping to 1-3 core values with rationale
5. **Scope**: What's included and excluded
6. **Maturity**: Defining deliverables at 30%, 60%, 80%, 100%
7. **Measurement**: Criteria, evidence, and quantified metrics
8. **Dependencies**: Prerequisites and what this capability enables
9. **Composition**: Outcomes (atomic) or sub-capabilities (composed)

### Viewing Capability Status

```bash
/capability:snapshot
```

See the current state of all capabilities with their maturity levels and health indicators.

### Removing a Capability

```bash
/capability:delete old-capability-id
```

Safely removes the capability and updates all tracking files.

## Capability Framework

### Actor Relationships

Capabilities identify stakeholder involvement with:

- **Relationship Types**:
  - `requires` - Actor needs this capability
  - `provides` - Actor delivers this capability
  - `consumes` - Actor uses this capability
  - `enables` - Actor makes this capability possible
  - `governs` - Actor regulates/oversees this capability

- **Criticality Levels**:
  - `essential` - Critical to actor's role
  - `important` - Significant but not critical
  - `optional` - Nice to have

### Business Values Framework

Each capability maps to 1-3 primary values from 28 core business values:

**Technical Quality**: Dependability, Performance, Security, Maintainability

**Business & Strategic**: Efficiency, Scalability, Time-to-Market, User Experience

**Communication & Process**: Transparency, Interoperability, Compliance

**Revenue & Market**: Revenue Enablement, Market Differentiation, Customer Acquisition

**User & Stakeholder**: Convenience, Personalization, Trust & Confidence, Empowerment, Responsiveness, Predictability, Control & Autonomy, Peace of Mind, Accessibility

**Operational**: Flexibility, Resilience, Observability, Cost Optimization, Data Quality

**Learning & Growth**: Learnability, Discovery

**Social & Environmental**: Fairness & Equity, Community & Connection, Sustainability, Privacy

### Maturity Progression

Capabilities progress through four stages:

- **30% - Experimental**: Proof of concept validated
- **60% - Tactical**: Usable in constrained production
- **80% - Production**: Reliable and well-documented
- **100% - Comprehensive**: Industry-leading implementation

## File Structure

```
capability/
├── plugin.json                          # Plugin metadata
├── commands/
│   ├── create.md                        # Create capability command
│   ├── delete.md                        # Delete capability command
│   └── snapshot.md                      # Generate snapshot command
├── hooks/
│   ├── __init__.py                      # Hook initialization
│   └── hooks/
│       ├── __init__.py                  # Submodule init
│       └── regenerate_snapshot.py       # Snapshot regeneration logic
├── schemas/
│   ├── capability_track_schema.json     # Capability tracking schema
│   └── capability_summary_schema.json   # Capability summary schema
└── templates/
    └── capability-statement-template.md # Capability definition template
```

## Integration with Outcome Workflow

Capabilities are built by outcomes:

- **Atomic Capabilities**: Built from outcome completions
  - Each outcome contributes a percentage to capability maturity
  - As outcomes complete, capability maturity increases

- **Composed Capabilities**: Built from sub-capabilities
  - Maturity is weighted average of child capabilities
  - Used for strategic groupings

### Cross-Reference Integrity

When modifying capabilities, maintain referential integrity with:

- `capabilities/*/capability_track.json` - Individual capability state
- `status/capability_summary.json` - Central capability index
- `outcomes/*/outcome_track.json` - Outcome-to-capability links
- `status/outcome_summary.json` - Central outcome index

## Schemas

The plugin includes two JSON schemas for validation:

### `capability_track_schema.json`
Defines the structure for individual capability tracking files:
- Metadata (ID, name, type, domain, status)
- Strategic context (purpose, scope, value proposition)
- Actor involvement with relationship types
- Business value mappings
- Maturity milestones and measurement criteria
- Dependencies and composition

### `capability_summary_schema.json`
Defines the central capability index structure:
- Capability array with metadata
- Indexes by domain, type, status, activity state, maturity range
- Summary statistics and aggregations
- Cross-reference to outcomes

## Dependencies

- **Shared Libraries**: `../../shared/cli-commons` (required for hooks)
- **Workspace Structure**: Expects standard workspace layout with `capabilities/`, `outcomes/`, and `status/` directories

## Related Plugins

- **outcome**: Manage tactical work units that build capabilities
- **workspace**: Multi-project workspace management
- **think**: Mental models for strategic decision-making

## Version

1.0.0
