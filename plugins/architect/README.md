# Architect Plugin

Architecture design and documentation following Lucid Composite Architecture (LCA) principles.

## Purpose

The architect plugin provides tools for designing, documenting, and reviewing software architecture based on LCA principles:

- **Composition over Inheritance** - Behavior composed, never inherited
- **Radical Containment** - Failures contained within boundaries
- **Functional Immutability** - Data immutable by default
- **Simplicity Default** - 80% generic, 20% performance-optimized
- **Data Strategy** - Schema.org at boundaries, focused types internally

## Installation

```bash
/plugin install architect@lucid-toolkit
```

## Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `/architect:init` | Initialize architecture documentation | `/architect:init [platform\|repository\|service\|component]` |
| `/architect:adr` | Create Architecture Decision Record | `/architect:adr <decision-title>` |
| `/architect:review` | Review architecture compliance | `/architect:review [full\|documentation\|code\|consistency]` |

## Skills

### manage-architecture

Create and maintain architecture documentation following LCA principles. Use when:
- Creating ARCHITECTURE.md files
- Documenting component hierarchies (Atoms, Composites, Conduits)
- Defining data strategies with Schema.org boundaries
- Setting up documentation hierarchy navigation

### create-adr

Create Architecture Decision Records that capture context, options, and trade-offs. Use when:
- Making architectural decisions
- Documenting why choices were made
- Superseding previous decisions

## Agents

### component-analyzer

Analyzes codebase to identify LCA structural components:
- **Atoms** - Pure functions, immutable objects, leaf nodes
- **Composites** - Containers that orchestrate Atoms
- **Conduits** - Boundaries between deployable units (Protocol Buffers, versioned APIs)
- **Deployable Units** - Self-contained services

Also identifies violations of LCA principles.

### architecture-reviewer

Reviews architecture against LCA principles across five dimensions:
- Composition (no behavior inheritance)
- Containment (failure isolation, scope boundaries)
- Immutability (pure functions, immutable data)
- Simplicity (profiling-driven optimization)
- Data Strategy (boundary semantics)

### adr-writer

Drafts ADRs following LCA conventions with:
- Context and problem statement
- Decision drivers (prioritized)
- Considered options (minimum 2)
- Explicit trade-offs (positive AND negative)

### consistency-checker

Validates architecture hierarchy for conflicts:
- Detects when lower levels override higher levels (VIOLATION)
- Detects when constraints are relaxed (VIOLATION)
- Validates against LCA immutable principles
- Distinguishes valid extensions from prohibited overrides

## Schemas

### component-info-schema.toon

Tracks LCA component inventory:
- Atoms, Composites, Conduits, Deployable Units
- Violation tracking with status
- Analysis history

### adr-index-schema.toon

ADR index and lifecycle tracking:
- Status management (proposed → accepted → superseded)
- Supersession chains
- Decision type categorization

## Hierarchy Resolution Model

Architecture flows DOWN through levels. Lower levels inherit from above and may EXTEND or ELABORATE but NEVER OVERRIDE.

```
LCA Core Principles (this plugin - IMMUTABLE)
    ↓ Cannot be overridden
Platform ARCHITECTURE.md
    ↓ Cannot be overridden by lower levels
Repository architecture.md
    ↓ Cannot be overridden by lower levels
Service/Component architecture.md
    ↓ Applies to local code
```

**Closer to code = applies to code, but cannot contradict higher levels.**

### Allowed Actions (Lower Levels)

| Action | Example |
|--------|---------|
| **Extend** | Platform: "Use Protocol Buffers" → Service: "Use proto3 with buf validation" |
| **Elaborate** | Platform: "Idempotent services" → Service: "Via request-id deduplication" |
| **Specialize** | Platform: "Schema.org at boundaries" → Service: "Schema.org/Order for orders" |

### Prohibited Actions (Lower Levels)

| Action | Example |
|--------|---------|
| **Override** | ❌ Platform: "No inheritance" → Service: "Use inheritance for code reuse" |
| **Relax** | ❌ Platform: "All APIs versioned" → Service: "Internal APIs skip versioning" |
| **Ignore** | ❌ Platform requires Data Strategy → Service omits section |

### LCA Immutable Principles

These cannot be overridden by any project architecture:

1. Composition over Inheritance
2. Radical Containment
3. Functional Immutability
4. Protocol Buffers for Conduits
5. Schema.org at Boundaries
6. Single Subject Types Internally
7. Versioned Conduits
8. Uni-directional Dependencies

## LCA Structural Hierarchy

```
Deployable Unit (Service)
├── Conduit (API Boundary - versioned, Protocol Buffers)
├── Composite (Orchestrator)
│   ├── Atom (Pure Function)
│   ├── Atom (Value Object)
│   └── Atom (Validator)
└── Composite (Coordinator)
    ├── Atom (Calculator)
    └── Atom (Formatter)
```

## Documentation Hierarchy

| Level | Scope | File |
|-------|-------|------|
| Platform | Cross-cutting concerns | `ARCHITECTURE.md` (uppercase, root) |
| Repository | Single codebase | `architecture.md` (lowercase) |
| Service | Focused microservice | `{service}/architecture.md` |
| Component | Implementation detail | `{component}/architecture.md` |

Navigation headers link documents: `↑ Parent | ← Siblings | ↓ Children`

## Maturity Status

| Status | Trust | Description |
|--------|-------|-------------|
| Draft | Hypothesis | Ideas tentative, not reviewed |
| InProgress | Direction Set | Core direction established, evolving |
| Stable | Reliable | Reviewed, safe to build against |
| Locked | Production | Change requires ADR |

## Quick Start

1. **Initialize architecture documentation:**
   ```
   /architect:init
   ```

2. **Review current architecture:**
   ```
   /architect:review
   ```

3. **Document a decision:**
   ```
   /architect:adr Use Protocol Buffers for service communication
   ```

## Related

- [arc-dec.md](../../arc-dec.md) - Full LCA specification
- [luc plugin](../luc/) - Project setup and workspace management
- [analyst plugin](../analyst/) - Mental models for decision analysis
