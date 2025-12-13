---
name: create-adr
description: |
  Create Architecture Decision Records (ADRs) following LCA conventions.

  INVOKE THIS SKILL when user:
  - Asks to "document a decision" or "record a decision"
  - Mentions "ADR", "decision record", or "architectural decision"
  - Wants to capture trade-offs or options considered
  - Needs to supersede or update an existing decision
  - Asks about decision history or rationale

  Trigger keywords: ADR, decision record, architectural decision, trade-offs, options, rationale
allowed-tools:
  - Read
  - Write
  - Glob
  - AskUserQuestion
---

<objective>
Guide creation of Architecture Decision Records that capture the "why" behind architectural choices. ADRs are append-only documents that preserve decision history, enabling future maintainers to understand context and trade-offs.
</objective>

<quick_start>
<workflow>
1. **Identify decision scope**: What architectural choice needs documentation?
2. **Gather context**: Why is this decision being made now? What drivers exist?
3. **Document options**: What alternatives were considered?
4. **Analyze trade-offs**: Explicit positive, negative, neutral consequences
5. **Record decision**: Write ADR with proper numbering and status
6. **Link to architecture docs**: Reference from relevant ARCHITECTURE.md
</workflow>

<naming_convention>
```
adr-NNN-{slug}.md

Examples:
adr-001-use-protocol-buffers.md
adr-002-adopt-event-sourcing.md
adr-003-schema-org-boundaries.md
```

Numbers are sequential and never reused. Superseded ADRs keep their number.
</naming_convention>

<template>
```markdown
# ADR-NNN: {Title}

**Status**: Proposed | Accepted | Deprecated | Superseded by ADR-XXX
**Date**: YYYY-MM-DD
**Deciders**: [list of people involved]
**Technical Story**: [ticket/issue reference if applicable]

## Context and Problem Statement

[Describe the context and problem. What forces are at play? Why is this decision needed now?]

## Decision Drivers

* [Driver 1: e.g., Performance requirements]
* [Driver 2: e.g., Team expertise]
* [Driver 3: e.g., Maintenance burden]

## Considered Options

1. [Option 1]
2. [Option 2]
3. [Option 3]

## Decision Outcome

**Chosen option**: "[Option N]" because [justification].

### Consequences

**Positive:**
* [Benefit 1]
* [Benefit 2]

**Negative:**
* [Drawback 1]
* [Drawback 2]

**Neutral:**
* [Side effect that is neither good nor bad]

## Pros and Cons of Options

### Option 1: [Name]

* Good, because [argument]
* Good, because [argument]
* Bad, because [argument]

### Option 2: [Name]

* Good, because [argument]
* Bad, because [argument]
* Bad, because [argument]

### Option 3: [Name]

[etc.]

## Links

* [Link to related ADRs]
* [Link to architecture documentation]
* [Link to external references]
```
</template>
</quick_start>

<adr_lifecycle>
<statuses>
| Status | Meaning | Action |
|--------|---------|--------|
| Proposed | Under discussion | Gather feedback, refine options |
| Accepted | Decision made | Implement, update architecture docs |
| Deprecated | No longer relevant | Document why, keep for history |
| Superseded | Replaced by newer ADR | Link to superseding ADR |
</statuses>

<append_only_rule>
ADRs are **never deleted or modified** after acceptance. They are historical records.

**To change a decision**:
1. Create new ADR with next number
2. Reference original: "Supersedes ADR-NNN"
3. Update original status: "Superseded by ADR-XXX"

This preserves the decision trail and reasoning evolution.
</append_only_rule>

<numbering>
- Start at 001
- Always 3 digits with leading zeros
- Sequential, never skip numbers
- Superseded ADRs keep their original number
</numbering>
</adr_lifecycle>

<decision_drivers>
<common_drivers>
When gathering context, consider these common architectural drivers:

**Technical**:
- Performance requirements (latency, throughput)
- Scalability needs (horizontal, vertical)
- Reliability requirements (uptime, fault tolerance)
- Security constraints (compliance, data protection)

**Organizational**:
- Team expertise and capacity
- Time-to-market pressure
- Budget constraints
- Existing technology investments

**Operational**:
- Maintenance burden
- Monitoring and observability
- Deployment complexity
- Rollback capabilities

**Strategic**:
- Vendor lock-in considerations
- Future flexibility needs
- Integration requirements
- Standards compliance
</common_drivers>

<elicitation>
Ask these questions to surface drivers:

1. "What problem is this decision solving?"
2. "What happens if we don't make this decision?"
3. "What constraints are non-negotiable?"
4. "Who will be affected by this decision?"
5. "How long do we expect this decision to remain valid?"
</elicitation>
</decision_drivers>

<trade_off_analysis>
<explicit_consequences>
LCA mandates explicit trade-offs—never assume decisions are purely positive.

**Positive consequences**: What improves? What becomes easier?
**Negative consequences**: What gets harder? What new problems emerge?
**Neutral consequences**: What changes without clear good/bad valence?
</explicit_consequences>

<analysis_framework>
For each option, evaluate against:

| Criterion | Weight | Option 1 | Option 2 | Option 3 |
|-----------|--------|----------|----------|----------|
| Performance | High | ++ | + | - |
| Maintainability | Medium | + | ++ | + |
| Team familiarity | Low | - | + | ++ |
| Migration effort | Medium | -- | + | + |

Use: `++` (strong positive), `+` (positive), `0` (neutral), `-` (negative), `--` (strong negative)
</analysis_framework>

<hidden_costs>
Surface hidden costs explicitly:

- **Learning curve**: Time for team to become proficient
- **Migration path**: Effort to move from current state
- **Operational overhead**: Ongoing maintenance burden
- **Technical debt**: Future refactoring this creates
- **Lock-in**: Difficulty switching away later
</hidden_costs>
</trade_off_analysis>

<lca_specific_adrs>
<common_decisions>
Architecture decisions frequently needed in LCA systems:

**Boundary Decisions**:
- "Where should the Conduit boundary be?"
- "What Protocol Buffer version to use?"
- "How to version the API?"

**Composition Decisions**:
- "How to decompose this into Atoms?"
- "What should the Composite orchestrate?"
- "Where does this logic belong?"

**Data Strategy Decisions**:
- "What Schema.org types at boundaries?"
- "How to model this internally?"
- "Where is the mapping layer?"

**Performance Tunnel Decisions**:
- "Is this bottleneck proven by profiling?"
- "What optimization approach?"
- "How to encapsulate complexity?"
</common_decisions>

<example_adr>
```markdown
# ADR-005: Use Schema.org/Product at API Boundary

**Status**: Accepted
**Date**: 2025-01-15
**Deciders**: Architecture team

## Context and Problem Statement

Our product catalog API needs to be consumable by AI agents and third-party
integrations. We need a data format that is self-describing and follows
industry standards.

## Decision Drivers

* AI agents need to understand our data semantically
* Third-party integrations should work without custom documentation
* Internal models need to remain optimized for computation

## Considered Options

1. Custom JSON schema with documentation
2. Schema.org/Product with JSON-LD serialization
3. GraphQL with custom types

## Decision Outcome

**Chosen option**: "Schema.org/Product with JSON-LD serialization" because
it provides semantic interoperability for AI consumers while following
established web standards.

### Consequences

**Positive:**
* AI agents can parse and understand our data without training
* Follows LCA principle of Schema.org at boundaries
* SEO benefits from structured data

**Negative:**
* Schema.org types are verbose compared to internal models
* Mapping layer adds complexity
* Some product attributes don't map cleanly

**Neutral:**
* Team needs to learn JSON-LD serialization

## Links

* Relates to ARCHITECTURE.md#data-strategy
* Schema.org Product: https://schema.org/Product
```
</example_adr>
</lca_specific_adrs>

<directory_structure>
<placement>
ADRs live in a dedicated directory at the architecture level they affect:

```
project/
├── ARCHITECTURE.md
├── adr/
│   ├── adr-001-initial-architecture.md
│   ├── adr-002-use-protocol-buffers.md
│   └── adr-003-schema-org-boundaries.md
└── services/
    └── order-service/
        ├── architecture.md
        └── adr/
            └── adr-001-caching-strategy.md
```
</placement>

<index>
Maintain an index file for discoverability:

```markdown
# Architecture Decision Records

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [001](adr-001-initial-architecture.md) | Initial Architecture | Accepted | 2025-01-01 |
| [002](adr-002-use-protocol-buffers.md) | Use Protocol Buffers | Accepted | 2025-01-05 |
| [003](adr-003-schema-org-boundaries.md) | Schema.org at Boundaries | Accepted | 2025-01-15 |
```
</index>
</directory_structure>

<validation>
<checklist>
Before marking ADR Accepted:

- [ ] Clear problem statement (why now?)
- [ ] Decision drivers listed with rationale
- [ ] At least 2 options considered
- [ ] Chosen option clearly stated with justification
- [ ] Positive consequences documented
- [ ] Negative consequences documented (mandatory—no free lunches)
- [ ] Neutral consequences considered
- [ ] Links to related architecture docs
- [ ] Proper numbering (adr-NNN format)
- [ ] Date and deciders recorded
</checklist>
</validation>

<success_criteria>
An ADR is complete when:

- A future reader can understand WHY the decision was made
- Trade-offs are explicit, not hidden
- Alternative options are documented for historical context
- Links connect to relevant architecture documentation
- Status accurately reflects decision state
</success_criteria>
