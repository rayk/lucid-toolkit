# Capability Statement Template

Use this template when defining new capabilities to ensure completeness, clarity, and alignment with workspace schema requirements.

---

## Metadata

**Capability ID**: `[domain]-[name]`
_Pattern: `^[a-z0-9]+(-[a-z0-9]+)*$` (kebab-case, e.g., `authentication-system`)_

**Name**: [Human-Readable Capability Name]
_Concise, action-oriented (e.g., "Secure Authentication System")_

**Type**: [ ] Atomic (built from outcomes) | [ ] Composed (built from sub-capabilities)

**Domain**: [Strategic Category]
_E.g., "Data Security & Privacy", "Product Lifecycle", "Developer Experience"_

**Status**: [ ] Active | [ ] Deprecated | [ ] Merged
_Default: Active for new capabilities_

**Target Maturity**: [0-100]%
_Strategic goal - what maturity level makes this capability "good enough" for business needs?_

---

## Purpose

[1-2 sentences explaining what this capability enables the system to DO]

**Template**: "Enable the system to [primary action] by [key mechanism], allowing [business outcome]."

**Example**: "Enable the system to authenticate users securely by implementing JWT-based session management, allowing the platform to verify user identity and enforce access controls."

---

## Value Proposition

Why does this capability matter? Categorize benefits:

### Risk Mitigation
- [Quantified security/compliance/reliability improvement]
- _Example: "Reduces unauthorized access risk by 95% through multi-factor authentication"_

### User Experience
- [Measurable UX improvement]
- _Example: "Reduces login friction to <2 seconds for 99% of users"_

### Development Velocity
- [Time/effort savings for developers]
- _Example: "Reduces authentication implementation time by 50% through reusable components"_

### Compliance
- [Standards/regulations met]
- _Example: "Achieves GDPR Article 32 compliance for user data protection"_

---

## Scope

### Included
- [Specific boundary 1]
- [Specific boundary 2]
- [Specific boundary 3]

_What IS this capability responsible for?_

### Excluded
- [Explicit non-goal 1]
- [Explicit non-goal 2]
- [Explicit non-goal 3]

_What is NOT this capability's responsibility? (Avoid scope creep)_

---

## Actor Involvement

_Which actors from the actor registry does this capability involve or impact?_

| Actor | Relationship | Criticality | Description |
|-------|--------------|-------------|-------------|
| **[Actor Name]** | [requires\|provides\|consumes\|enables\|governs] | [essential\|important\|optional] | [How this actor relates to the capability] |

**Relationship Types**:
- `requires`: Actor needs this capability to fulfill their role
- `provides`: Actor delivers or implements this capability
- `consumes`: Actor uses this capability's outputs
- `enables`: Actor makes this capability possible
- `governs`: Actor regulates or oversees this capability

**Criticality Levels**:
- `essential`: Critical to actor's role - capability failure significantly impacts actor
- `important`: Significant but not critical - degraded experience without it
- `optional`: Nice to have - actor can function without it

**Impact Assessment**:
- [Describe how actors interact with this capability]
- [Note which actors are direct users vs indirect beneficiaries]
- [Identify risks to actors if capability fails or is immature]

_Reference: Load actors from `status/actor_summary.json` for valid actor IDs_

---

## Maturity Milestones

Define concrete deliverables at each maturity threshold. Follow progressive complexity: experimental → tactical → production → comprehensive.

### 30% - Experimental
**Status**: Proof of concept validated
**Deliverables**:
- [Key proof-of-concept outcome]
- [Initial implementation/prototype]
- [Basic validation test]

**Example**: "JWT token generation working in development environment, basic login flow functional"

---

### 60% - Tactical
**Status**: Usable in constrained production scenarios
**Deliverables**:
- [Production-ready core functionality]
- [Essential error handling]
- [Documentation for basic use cases]

**Example**: "Production JWT implementation with refresh tokens, rate limiting, basic audit logging"

---

### 80% - Production
**Status**: Reliable and well-documented for general use
**Deliverables**:
- [Comprehensive error handling]
- [Performance optimization]
- [Complete documentation + runbooks]
- [Monitoring/observability]

**Example**: "Multi-factor authentication, session management, comprehensive security logging, incident response procedures"

---

### 100% - Comprehensive
**Status**: Industry-leading implementation
**Deliverables**:
- [Advanced features]
- [Edge case handling]
- [Automation/self-healing]
- [Continuous improvement mechanisms]

**Example**: "Adaptive authentication, biometric support, automated threat detection, zero-downtime credential rotation"

---

## Measurement

### Criteria
How do we assess current maturity?

- [Assessment method 1]
- [Assessment method 2]
- [Assessment method 3]

**Example**:
- Test coverage ≥95% for authentication flows
- Security audit passing score ≥90%
- Mean time to authenticate <1.5 seconds

### Evidence
What demonstrates progress toward maturity milestones?

- [Observable artifact 1]
- [Observable artifact 2]
- [Observable artifact 3]

**Example**:
- Passing penetration test reports
- Authentication flow test suite results
- Session management audit logs

### Metrics
Quantified thresholds for success:

| Metric | Target | Current | Gap |
|--------|--------|---------|-----|
| [Metric 1] | [Target value] | [Current value] | [Difference] |
| [Metric 2] | [Target value] | [Current value] | [Difference] |
| [Metric 3] | [Target value] | [Current value] | [Difference] |

**Example**:
| Metric | Target | Current | Gap |
|--------|--------|---------|-----|
| Test Coverage | 95% | 78% | -17% |
| Auth Success Rate | 99.9% | 98.2% | -1.7% |
| P95 Latency | <1.5s | 2.1s | +0.6s |

---

## Dependencies

### Prerequisites
Capabilities that MUST exist before this capability can progress:

| Capability ID | Minimum Maturity Required | Rationale |
|---------------|---------------------------|-----------|
| `[capability-id]` | [0-100]% | [Why this is needed] |

**Example**:
| Capability ID | Minimum Maturity Required | Rationale |
|---------------|---------------------------|-----------|
| `database-infrastructure` | 60% | Need persistent storage for session tokens |
| `api-gateway` | 30% | Need request routing for auth endpoints |

### Enables
Capabilities that are UNLOCKED by this capability:

| Capability ID | How This Enables It |
|---------------|---------------------|
| `[capability-id]` | [What becomes possible] |

**Example**:
| Capability ID | How This Enables It |
|---------------|---------------------|
| `user-profile-management` | Cannot manage profiles without authenticated user identity |
| `authorization-system` | Authentication is prerequisite for authorization decisions |

---

## Composition

### For Atomic Capabilities
**Built By Outcomes**: This capability is constructed from individual outcome completions.

**Required Outcomes** (list outcomes that contribute to this capability):
- `[outcome-id]`: [% contribution to maturity]
- `[outcome-id]`: [% contribution to maturity]

**Example**:
- `001-jwt-implementation`: 25% maturity contribution
- `002-session-management`: 20% maturity contribution
- `003-mfa-implementation`: 30% maturity contribution
- `004-audit-logging`: 25% maturity contribution

---

### For Composed Capabilities
**Built By Sub-Capabilities**: This capability is the weighted average of child capabilities.

**Sub-Capabilities** (list child capabilities with their weights):

| Sub-Capability ID | Weight | Rationale |
|-------------------|--------|-----------|
| `[sub-cap-id]` | [%] | [Why this weight?] |

**Total Weight MUST = 100%**

**Example**:
| Sub-Capability ID | Weight | Rationale |
|-------------------|--------|-----------|
| `password-authentication` | 40% | Primary auth mechanism for most users |
| `oauth-integration` | 30% | Third-party login support |
| `session-lifecycle` | 20% | Session creation, refresh, invalidation |
| `security-monitoring` | 10% | Threat detection and response |

---

## Quality Checklist

Before finalizing this capability statement, verify:

- [ ] **Clear ID**: Follows `^[a-z0-9]+(-[a-z0-9]+)*$` pattern
- [ ] **Actionable Purpose**: Uses action verbs ("Enable the system to...")
- [ ] **Quantified Value**: At least 2 value propositions with measurable impact
- [ ] **Explicit Boundaries**: Both inclusions AND exclusions defined
- [ ] **Actor Involvement**: 1+ actors identified with relationship type, criticality, and description
- [ ] **Complete Maturity Narrative**: All 4 milestones (30/60/80/100%) have concrete deliverables
- [ ] **Testable Measurement**: Specific metrics with target values
- [ ] **Dependency Clarity**: Prerequisites and enablements explicitly documented
- [ ] **Composition Transparency**:
    - Atomic: Outcomes listed with maturity contributions
    - Composed: Sub-capabilities listed with weights totaling 100%
- [ ] **No Placeholders**: No "TBD", "TODO", or empty sections in completed areas
- [ ] **Business Outcome Linkage**: Clear connection between capability and strategic value

---

## Excellence Indicators

✅ **Action-oriented language** - "Enable the system to..." not "The system should..."
✅ **Quantified success criteria** - Numbers, percentages, thresholds
✅ **Progressive maturity story** - Clear narrative from 30% → 100%
✅ **Strategic alignment** - Links to business outcomes/risk reduction
✅ **Measurable evidence** - Observable artifacts that prove maturity
✅ **Realistic scope** - Achievable boundaries with explicit exclusions
✅ **Dependency traceability** - Clear prerequisite chain and enablement graph
✅ **Actor traceability** - Clear stakeholder identification with relationship types

---

## Notes for Capability Authors

### Atomic vs. Composed Decision
- **Choose Atomic** if this capability is built through sequential completion of outcomes (work items)
- **Choose Composed** if this capability represents a strategic grouping of other capabilities

### Target Maturity Guidance
- **30-60%**: Experimental/early-stage capabilities, high uncertainty
- **60-80%**: Production capabilities requiring reliability
- **80-100%**: Mission-critical capabilities, compliance-driven, or competitive differentiators

### Maturity Contribution Calculation
For atomic capabilities, outcome maturity contributions should reflect:
- **Effort required** (more complex outcomes = higher %)
- **Strategic importance** (higher value outcomes = higher %)
- **Risk reduction** (security-critical outcomes = higher %)

Total contributions should align with target maturity (e.g., if target is 80%, outcomes totaling 80% maturity gets you there).

### Common Pitfalls to Avoid
❌ Vague purpose statements ("Improve authentication")
❌ Unmeasurable value propositions ("Better security")
❌ Missing scope exclusions (leads to scope creep)
❌ Milestone deliverables without concrete artifacts
❌ Dependencies without maturity thresholds
❌ Composition weights that don't total 100%

---

*This template aligns with `schemas/capability_track_schema.json` requirements and workspace conventions defined in `CLAUDE.md`.*
