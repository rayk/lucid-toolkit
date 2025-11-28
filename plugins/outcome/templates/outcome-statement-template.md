# Outcome Statement Template

Use this template when defining new outcomes to ensure completeness, clarity, and alignment with workspace schema requirements.

---

## Metadata

**Outcome ID**: `[sequence]-[descriptor]`
_Pattern: `^[0-9]+-[a-z0-9]+(-[a-z0-9]+){0,4}$` (e.g., `001-jwt-authentication`)_

**Name**: [Human-Readable Outcome Name]
_Derived from descriptor, title-cased (e.g., "JWT Authentication")_

**Type**: [ ] Atomic (single execution context) | [ ] Parent (aggregates child outcomes)

**State**: [ ] Queued | [ ] Ready | [ ] In-Progress | [ ] Blocked | [ ] Completed
_Default: Queued for new outcomes. Ready = all dependencies complete. Blocked requires blocker details below._

**Token Budget**: [Estimated tokens]
_Atomic outcomes must fit within ~200K tokens_

---

## Achievement

[1-2 sentences describing WHAT this outcome accomplishes - achievement-focused, not process-focused]

**Template**: "Achieve [specific result] so that [business/user benefit]."

**Example**: "Achieve secure JWT-based authentication with session persistence so that users can log in and maintain sessions across requests."

### Anti-patterns to Avoid
❌ Process prescriptions: "Use TDD to implement...", "Follow agile methodology..."
❌ Implementation artifacts: "Create auth.ts file...", "Write unit tests..."
❌ Tool requirements: "Implement using library X...", "Must use framework Y..."

### Patterns to Follow
✅ Observable end states: "Users can authenticate..."
✅ Behavioral requirements: "Unauthorized access is prevented..."
✅ Performance criteria: "API responds within 200ms..."

---

## Purpose

Why is this outcome needed? What problem does it solve?

[2-3 sentences explaining the rationale]

**Example**: "Users currently cannot securely access protected resources. This outcome establishes the authentication foundation required for all user-facing features, enabling secure identity verification and session management."

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

**Example**:
- **Included**: JWT token generation, session persistence, credential validation
- **Excluded**: OAuth integration, MFA, biometric authentication

---

## Observable Effects

Define concrete, testable behavioral changes that prove this outcome is complete. Express each effect as a **Given-When-Then** acceptance criterion. These are NOT implementation artifacts.

_Minimum 2 observable effects required. Cover both success cases AND error handling._

### Effect 1: [Short title]
**Actor**: [Which actor experiences/verifies this]

```gherkin
Given [precondition/context]
When [action/trigger]
Then [observable outcome]
```

**Verification**: [How to prove this effect exists]

---

### Effect 2: [Short title]
**Actor**: [Which actor experiences/verifies this]

```gherkin
Given [precondition/context]
When [action/trigger]
Then [observable outcome]
```

**Verification**: [How to prove this effect exists]

---

### Effect 3: [Short title]
**Actor**: [Which actor experiences/verifies this]

```gherkin
Given [precondition/context]
When [action/trigger]
Then [observable outcome]
```

**Verification**: [How to prove this effect exists]

---

**Example**:

### Effect 1: Successful Authentication
**Actor**: Lot Owner

```gherkin
Given a registered user with valid credentials
When they submit their email and password
Then they receive a valid session token and can access protected resources
```

**Verification**: Manual testing + automated integration tests

---

### Effect 2: Invalid Credentials Rejected
**Actor**: Lot Owner

```gherkin
Given a user with invalid credentials
When they attempt to authenticate
Then they receive a 401 status with a clear error message
And no session token is issued
```

**Verification**: Automated API tests

---

### Effect 3: Session Persistence
**Actor**: Lot Owner

```gherkin
Given an authenticated user with a valid session
When they make subsequent requests within 24 hours
Then their session remains valid without re-authentication
```

**Verification**: Session duration monitoring

---

### Effect 4: Security Compliance
**Actor**: Security Team

```gherkin
Given the authentication system is deployed
When a security scan is performed
Then zero critical authentication vulnerabilities are detected
```

**Verification**: OWASP ZAP scan results

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

**Example**:
- **Primary**: `authentication-system` +5% - Establishes JWT foundation for user authentication
- **Secondary**: `security-framework` +2% - Implements secure token handling patterns

_Large contributions (>20%) should be justified or the outcome should be split._

---

## Actor Involvement

Who is involved in or impacted by this outcome?

| Actor | Relationship | Impact |
|-------|--------------|--------|
| [Actor ID] | [ ] Beneficiary [ ] Stakeholder [ ] Contributor [ ] Approver [ ] Informed | [How they're affected] |

**Relationship Types**:
- **Beneficiary**: Primary users who benefit from this outcome
- **Stakeholder**: Parties with interest in outcome success
- **Contributor**: Teams/individuals who implement the outcome
- **Approver**: Must approve outcome before completion
- **Informed**: Should be notified of outcome progress

**Example**:
| Actor | Relationship | Impact |
|-------|--------------|--------|
| lot-owner | Beneficiary | Primary users who will authenticate to access owner portal |
| strata-manager | Stakeholder | Needs authentication for management portal access |
| security-team | Approver | Must approve security audit before completion |
| development-team | Contributor | Implements the authentication system |

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

**Example**:
- **Depends On**: None (foundational outcome)
- **Enables**: `002-oauth-integration` (requires auth foundation), `005-multi-factor-auth` (extends base auth)

---

## Hierarchy (for Parent/Child relationships)

### For Atomic Outcomes
**Parent Outcome**: `[parent-outcome-id]` or "None (root-level outcome)"

### For Parent Outcomes
**Child Outcomes**:
| Child ID | Contribution | Status |
|----------|--------------|--------|
| `[child-id]` | +[X]% | [ ] Pending [ ] In-Progress [ ] Completed |

**Integration Validation**: [What must be true when ALL children complete]

**Example** (Parent):
- Children: `010.1-sql-injection` (+2%), `010.2-xss-prevention` (+3%), `010.3-auth-bypass` (+2%)
- Integration Validation: "All vulnerabilities patched AND security scan passes"

---

## Rationale & Alternatives

### Problem Statement
[What problem does this outcome solve?]

### Alternatives Considered
| Alternative | Why Rejected |
|-------------|--------------|
| [Approach 1] | [Reason] |
| [Approach 2] | [Reason] |

### Constraints
- [Technical constraint]
- [Resource constraint]
- [External constraint]

### Known Side Effects
- [Consequence 1]
- [Consequence 2]

### Risks
| Risk | Type | Mitigation |
|------|------|------------|
| [Risk description] | [ ] Technical [ ] Dependency [ ] Resource | [How to mitigate] |

**Example**:
- **Problem**: Users cannot securely access the system
- **Alternatives**: Session cookies only (rejected - no API/mobile support), OAuth-first (rejected - adds complexity)
- **Constraints**: Must support mobile clients, 24-hour session max per security policy
- **Side Effects**: Existing basic auth will be deprecated
- **Risks**: Token refresh edge cases (technical) - mitigated by comprehensive test coverage

---

## Effort Estimate

**Effort Level**: [ ] Very Low (<25K tokens) | [ ] Low (25-75K) | [ ] Average (75-150K) | [ ] High (150-200K) | [ ] Very High (>200K - MUST SPLIT)

**Complexity Indicators**:
| Indicator | Value |
|-----------|-------|
| Files Affected | [count] |
| Systems Integrated | [count] |
| Integration Points | [count] |
| Novelty/Uncertainty | [ ] Low [ ] Medium [ ] High |

_If Very High effort, this outcome MUST be split into child outcomes._

---

## Blocker Details (if state = Blocked)

_Complete this section only if outcome is in Blocked state._

**Blocker Type**: [ ] Dependency | [ ] External | [ ] Technical | [ ] Resource | [ ] Approval

**Description**: [What is blocking progress]

**Blocked Since**: [Date/time when blocked]

**Resolution Path**: [How to resolve this blocker]

---

## Quality Checklist

Before finalizing this outcome statement, verify:

- [ ] **Valid ID**: Follows `^[0-9]+(\\.[0-9]+)?-[a-z0-9]+(-[a-z0-9]+){0,4}$` pattern (supports hierarchical IDs like 010.1-name)
- [ ] **Achievement-Focused**: Describes WHAT to accomplish, not HOW
- [ ] **No Process Prescriptions**: No methodology, tool, or workflow requirements
- [ ] **Observable Effects**: Minimum 2 effects in Given-When-Then format with actor perspectives
- [ ] **Effects NOT Artifacts**: All effects describe behavioral changes, not implementation deliverables
- [ ] **Given-When-Then Format**: Each effect follows Given [context] When [action] Then [outcome]
- [ ] **Capability Contribution**: At least one capability referenced with maturity %
- [ ] **Actor Involvement**: At least one actor identified with relationship type
- [ ] **Scope Boundaries**: Both inclusions AND exclusions defined
- [ ] **Token Budget**: Atomic outcomes fit within ~200K tokens
- [ ] **Dependencies Clear**: Only outcome dependencies (not capability dependencies)
- [ ] **Rationale Complete**: Problem statement, alternatives, constraints documented
- [ ] **No Placeholders**: No "TBD", "TODO", or empty sections

---

## Excellence Indicators

✅ **Achievement language** - "Achieve X so that Y", not "Implement X using Y"
✅ **Observable proof** - Behavioral changes that prove completion
✅ **Actor-verifiable** - Each effect specifies who can verify it
✅ **Strategic alignment** - Clear capability contribution with rationale
✅ **Realistic scope** - Fits within token budget, explicit exclusions
✅ **Dependency clarity** - Only outcome dependencies, enables chain visible
✅ **Risk awareness** - Constraints, side effects, and mitigations documented

---

## Notes for Outcome Authors

### Atomic vs. Parent Decision
- **Choose Atomic** if outcome fits within ~200K token context and is self-contained
- **Choose Parent** if outcome needs to be decomposed into multiple sub-outcomes

### Observable Effects Guidance
Express effects as Given-When-Then acceptance criteria focusing on WHAT changes, not WHAT gets created:

❌ **Artifacts (reject)**:
```
Given tests are written
When the test suite runs
Then JWT tests pass
```

✅ **Behavioral changes (accept)**:
```gherkin
Given a user with invalid credentials
When they attempt to authenticate
Then they receive a 401 status with a clear error message
```

❌ **Implementation (reject)**: "auth.ts file created"
✅ **Behavior (accept)**: "Given valid credentials, When user submits login, Then session is created"

### Contribution Calculation
Maturity contributions should reflect:
- **Impact on capability**: How much does this advance the strategic goal?
- **Effort involved**: More complex work = higher contribution
- **Risk reduction**: Security-critical outcomes may warrant higher %

### Common Pitfalls to Avoid
❌ Vague achievements ("Improve authentication")
❌ Process prescriptions ("Use TDD", "Follow clean code")
❌ Implementation artifacts as effects ("Tests pass", "File created")
❌ Missing actor perspectives on effects
❌ Capability dependencies (outcomes BUILD capabilities, don't depend on them)
❌ Scope without exclusions (leads to creep)
❌ Token budget exceeded without splitting

---

*This template aligns with `schemas/outcome_track_schema.json` requirements and workspace conventions defined in `CLAUDE.md`.*

---

## Document Information

**Version:** 2.0.0
**Created:** 2025-11-20
**Updated:** 2025-11-22
**Status:** Active

**Changelog:**
- v2.0.0: Major reconciliation - Added Ready state to state checkboxes, added Blocker Details section, updated quality checklist with hierarchical ID pattern, enhanced observable effects guidance with Given-When-Then format, added complexity indicator thresholds
- v1.0.0: Initial template aligned with outcome_track_schema.json
