# Outcome Statement Template

Use this template when creating new outcomes to ensure completeness, clarity, and alignment with workspace schema requirements.

---

## YAML Frontmatter

```yaml
---
identifier: 005-outcome-name        # Pattern: ^[0-9]+-[a-z0-9]+(-[a-z0-9]+){0,4}$
name: Human-Readable Outcome Name   # Display name, title-cased
stage: queued                       # queued | ready | in-progress | blocked | completed
priority: P2                        # P1 (critical) | P2 (important) | P3 (nice-to-have)

achievement: |
  Achieve [specific result] so that [business/user benefit].

purpose: |
  Why this outcome is needed. What problem does it solve?

tokenBudget: average               # very-low (<25K) | low (25-75K) | average (75-150K) | high (150-200K)

capabilityContributions:
  - capabilityId: capability-id
    contribution: 15               # percentage (typically 5-20%, max 25%)
    rationale: How this outcome advances the capability

actors:
  - id: actor-id                   # kebab-case from actor registry
    relationship: beneficiary      # beneficiary | stakeholder | contributor | approver | informed

scope:
  included:
    - Specific responsibility 1
    - Specific responsibility 2
    - Specific responsibility 3
  excluded:
    - Explicit non-goal 1
    - Explicit non-goal 2
    - Explicit non-goal 3

dependencies:
  dependsOn: []                    # Outcome IDs that must complete first
  enables: []                      # Outcome IDs unlocked when this completes

# For child outcomes only (nested under parent):
# parentOutcome: 005-parent-name
# parentContribution: 40           # What % of parent's work this represents
# Note: Children have capabilityContributions: [] (contribute to parent, not directly to capability)

validation:
  lastChecked: null
  status: UNCHECKED
---
```

---

## Achievement

[1-2 sentences describing WHAT this outcome accomplishes - achievement-focused, not process-focused]

**Template**: "Achieve [specific result] so that [business/user benefit]."

### Patterns to Follow
- Observable end states: "Users can authenticate..."
- Behavioral requirements: "Unauthorized access is prevented..."
- Performance criteria: "API responds within 200ms..."

### Anti-patterns to Avoid
- Process prescriptions: "Use TDD to implement...", "Follow agile methodology..."
- Implementation artifacts: "Create auth.ts file...", "Write unit tests..."
- Tool requirements: "Implement using library X...", "Must use framework Y..."

---

## Purpose

Why is this outcome needed? What problem does it solve?

[2-3 sentences explaining the rationale]

---

## Scope

### Included
- [Specific deliverable 1]
- [Specific deliverable 2]
- [Specific deliverable 3]

_What IS this outcome responsible for achieving?_

### Excluded
- [Explicit non-goal 1]
- [Explicit non-goal 2]
- [Explicit non-goal 3]

_What is NOT this outcome's responsibility? (Prevents scope creep)_

---

## Observable Effects

Define concrete, testable behavioral changes that prove this outcome is complete. Express each effect as a **Given-When-Then** acceptance criterion with actor perspective.

_Minimum 2 observable effects required. Cover both success cases AND error handling._

### Effect 1: [Short Title]
**Actor**: [actor-id from registry]

```gherkin
Given [precondition/context]
When [action/trigger]
Then [observable outcome]
```

**Verification**: [How to prove this effect exists]

---

### Effect 2: [Short Title]
**Actor**: [actor-id from registry]

```gherkin
Given [precondition/context]
When [action/trigger]
Then [observable outcome]
```

**Verification**: [How to prove this effect exists]

---

### Effect 3: [Short Title] (optional)
**Actor**: [actor-id from registry]

```gherkin
Given [precondition/context]
When [action/trigger]
Then [observable outcome]
```

**Verification**: [How to prove this effect exists]

---

## Capability Contributions

This outcome builds the following capabilities:

### Primary Capability
**Capability ID**: `[capability-id]`
**Maturity Contribution**: +[X]%
**Rationale**: [How this outcome advances the capability]

### Secondary Capabilities (optional)
| Capability ID | Contribution | Rationale |
|---------------|--------------|-----------|
| `[cap-id]` | +[X]% | [Why this outcome impacts this capability] |

_Large contributions (>20%) should be justified or the outcome should be split._

---

## Actor Involvement

Who is involved in or impacted by this outcome?

| Actor | Relationship | Impact |
|-------|--------------|--------|
| [actor-id] | beneficiary/stakeholder/contributor/approver/informed | [How affected] |

**Relationship Types**:
- **Beneficiary**: Primary users who benefit from this outcome
- **Stakeholder**: Parties with interest in outcome success
- **Contributor**: Teams/individuals who implement the outcome
- **Approver**: Must approve outcome before completion
- **Informed**: Should be notified of outcome progress

---

## Dependencies

### Depends On (outcomes that must complete first)
| Outcome ID | Rationale |
|------------|-----------|
| `[outcome-id]` | [Why this dependency exists] |

_Leave empty if no dependencies. Outcomes depend on OTHER OUTCOMES only, not capabilities._

### Enables (outcomes unlocked when this completes)
| Outcome ID | How This Enables It |
|------------|---------------------|
| `[outcome-id]` | [What becomes possible] |

---

## Hierarchy (for Parent/Child outcomes)

### For Atomic/Standalone Outcomes
**Parent Outcome**: None (root-level outcome)

### For Child Outcomes
**Parent Outcome**: `[parent-outcome-id]`
**Parent Contribution**: [X]% (what portion of parent's work this represents)

_Note: Child outcomes have empty capabilityContributions - they contribute to their parent, which contributes to capabilities._

### For Parent Outcomes
**Child Outcomes**:
| Child ID | Contribution | Status |
|----------|--------------|--------|
| `[child-id]` | +[X]% | queued/ready/in-progress/completed |

**Integration Validation**: [What must be true when ALL children complete]

_All children's parentContribution values must sum to 100%._

---

## Effort Estimate

**Token Budget**: [very-low | low | average | high]

| Budget Level | Token Range | Guidance |
|--------------|-------------|----------|
| very-low | <25K | Simple, focused task |
| low | 25-75K | Standard outcome |
| average | 75-150K | Complex outcome |
| high | 150-200K | Large outcome (consider splitting) |

_If >200K tokens estimated, MUST split into parent with child outcomes._

---

## Blocker Details (if stage = blocked)

_Complete this section only if outcome is in blocked stage._

**Blocker Type**: dependency | external | technical | resource | approval

**Description**: [What is blocking progress]

**Blocked Since**: [Date/time when blocked]

**Resolution Path**: [How to resolve this blocker]

---

## Quality Checklist

Before finalizing this outcome statement, verify:

- [ ] **Valid ID**: Follows `^[0-9]+(\\.[0-9]+)?-[a-z0-9]+(-[a-z0-9]+){0,4}$` pattern
- [ ] **Achievement-Focused**: Describes WHAT to accomplish, not HOW
- [ ] **No Process Prescriptions**: No methodology, tool, or workflow requirements
- [ ] **Observable Effects**: Minimum 2 effects in Given-When-Then format
- [ ] **Effects NOT Artifacts**: All effects describe behavioral changes
- [ ] **Actor Perspectives**: Each effect tied to an actor
- [ ] **Capability Contribution**: At least one capability with maturity %
- [ ] **Actor Involvement**: At least one actor with relationship type
- [ ] **Scope Boundaries**: Both inclusions AND exclusions defined
- [ ] **Token Budget**: Within acceptable range (<200K or split)
- [ ] **Dependencies Clear**: Only outcome dependencies (not capability)
- [ ] **No Placeholders**: No "TBD", "TODO", or empty sections

---

## Document Information

**Version:** 1.0.0
**Created:** 2025-12-03
**Status:** Active

_This template aligns with outcomes-info-schema.toon requirements and workspace conventions._
