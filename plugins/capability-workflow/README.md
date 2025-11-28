# Capability Workflow Plugin

Comprehensive workflow for managing capabilities in the lucid_stack workspace. This plugin enables creation, deletion, and snapshot generation of capabilities following workspace standards.

## Overview

Capabilities are strategic goals measured by maturity percentage. This plugin provides complete lifecycle management:
- **Create**: Define new capabilities with strategic context, actor involvement, and business value mapping
- **Delete**: Safely remove capabilities with full cross-reference cleanup
- **Snapshot**: Generate hierarchical views of capability structure and maturity metrics

## Assets

### Commands (3 files)
Located in `commands/`:

1. **create.md** - Create a complete capability statement
   - Guides through capability identity capture
   - Maps strategic foundation (purpose, type, domain, target maturity)
   - Identifies actor involvement and criticality
   - Maps core business values (1-3 values from 28-value framework)
   - Validates against workspace schema and template requirements

2. **delete.md** - Delete a capability and clean up all references
   - Safely removes capability from workspace
   - Cleans up capability_summary.json
   - Removes all outcome cross-references
   - Updates outcome_summary.json
   - Ensures no orphaned references

3. **snapshot.md** - Generate capability snapshot
   - Displays pre-computed hierarchical structure
   - Shows capability maturity levels and health indicators
   - Performance: <100ms from cache (vs ~16s for LLM generation)
   - Regenerates if snapshot file missing

### Hooks (4 files)
Located in `hooks/`:

- **__init__.py** - Hook initialization
- **hooks/regenerate_snapshot.py** - Capability snapshot regeneration logic
- **hooks/__init__.py** - Hook submodule initialization
- **lib/snapshot_generator.py** - Snapshot generation utility library

### Templates (1 file)
Located in `templates/`:

- **capability-statement-template.md** - Standard template for capability definitions
  - Follows workspace conventions
  - Includes sections for purpose, type, domain, actors, values, and maturity milestones

### Schemas (2 files)
Located in `schemas/`:

1. **capability_track_schema.json** (29.7 KB)
   - Defines capability tracking file structure
   - Validates capability metadata, actors, business values, and maturity tracking

2. **capability_summary_schema.json** (28.9 KB)
   - Defines capability summary structure
   - Used for quick lookups and hierarchical capability views

## Usage

### Create a Capability
```bash
/capability:create [capability-name or description]
```

Example:
```bash
/capability:create auth-system
```

### Delete a Capability
```bash
/capability:delete <capability-id>
```

Example:
```bash
/capability:delete auth-system
```

### Generate Snapshot
```bash
/capability:snapshot
```

## Integration Points

### Schema Validation
Before modifying capability tracking files, validate against:
- `schemas/capability_track_schema.json` - Individual capability definitions
- `schemas/capability_summary_schema.json` - Summary index

### Cross-References
Capabilities link to:
- **Outcomes**: Track which outcomes build each capability
- **Actors**: Define actor relationships (requires/provides/consumes/enables/governs)
- **Business Values**: Map to 1-3 core values from strategic framework

When updating capabilities, ensure cross-references are maintained in:
- `status/capability_summary.json` - Central index
- `outcomes/*/outcome_track.json` - Outcome-to-capability links
- `status/outcome_summary.json` - Outcome summary index

## Actor Framework

Capabilities identify actor involvement organized by domain:
- Ownership & Governance
- External Service & Professional
- User Interaction
- System & Infrastructure
- Data & Analytics
- Application Services

Each actor relationship specifies:
- **Type**: requires | provides | consumes | enables | governs
- **Criticality**: essential | important | optional
- **Description**: How the actor relates to this capability

## Business Values Framework

Capabilities map to 1-3 core values from the 28-value strategic framework, including:
- Strategic alignment
- User value delivery
- Technical excellence
- Operational efficiency
- And 24 additional values...

## File Structure
```
capability-workflow/
├── README.md                              (this file)
├── commands/
│   ├── create.md                          (create command)
│   ├── delete.md                          (delete command)
│   └── snapshot.md                        (snapshot command)
├── hooks/
│   ├── __init__.py                        (hook initialization)
│   ├── hooks/
│   │   ├── __init__.py                    (submodule init)
│   │   └── regenerate_snapshot.py         (regeneration logic)
│   └── lib/
│       ├── __init__.py                    (library init)
│       └── snapshot_generator.py          (generator utility)
├── schemas/
│   ├── capability_track_schema.json       (capability tracking schema)
│   └── capability_summary_schema.json     (capability summary schema)
└── templates/
    └── capability-statement-template.md   (statement template)
```

## Related Documentation

See lucid_stack CLAUDE.md for workspace conventions:
- Capability classification and lifecycle
- Cross-reference integrity requirements
- Schema validation protocols
- Workspace operations and naming patterns

## Version

Extracted from lucid_stack on 2025-11-28.
Source: `/Users/rayk/Projects/lucid_stack/.claude/`
