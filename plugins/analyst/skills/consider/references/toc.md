# Theory of Constraints: Logical Thinking Process

Systematic root cause analysis and solution design using causal graphs, conflict resolution, and simulation. Based on Goldratt's Thinking Processes.

## When to Use

- Complex operational problems with multiple symptoms
- Situations where "obvious" fixes keep failing
- Hidden conflicts blocking progress (damned-if-you-do, damned-if-you-don't)
- Need to verify a solution won't create new problems
- Tracing symptoms back to actionable root causes

## The Three Phases

| Phase | Question | Tool | Goal |
|-------|----------|------|------|
| **Current Reality Tree** | What to change? | CRT | Find root cause |
| **Evaporating Cloud** | What to change to? | EC | Resolve conflict |
| **Future Reality Tree** | How to cause change? | FRT | Verify solution |

## Categories of Legitimate Reservation (CLR)

Use these to validate EVERY causal link:

| Reservation | Test Question |
|-------------|---------------|
| **Clarity** | Do I understand the statement? |
| **Entity Existence** | Does this cause actually exist in reality? |
| **Causality Existence** | Does the cause actually lead to the effect? |
| **Cause Sufficiency** | Is this cause enough alone, or are dependent causes missing? |
| **Additional Cause** | Is there another independent cause? |
| **Cause-Effect Reversal** | Is the arrow pointing the wrong direction? |
| **Predicted Effect Existence** | If the cause exists, would we see other effects? |
| **Tautology** | Is this circular reasoning? |

## Execution Template

```markdown
**Problem Statement:** [The undesirable effects the user is experiencing]

---

## Phase 1: Current Reality Tree (What to Change?)

### Step 1.1: List Undesirable Effects (UDEs)
*Symptoms the user is complaining about - observable, not interpretations*

| # | Undesirable Effect | Evidence |
|---|-------------------|----------|
| 1 | [symptom] | [how we know] |
| 2 | [symptom] | [how we know] |
| 3 | [symptom] | [how we know] |

### Step 1.2: Build Causal Chain (Backward)
*For each UDE, ask "Why?" and connect to causes*

```
[UDE 1] ← caused by ← [Cause A] ← caused by ← [Deeper Cause]
                   ↖
[UDE 2] ← caused by ← [Cause B] ← caused by ← [ROOT CAUSE]
                   ↗
[UDE 3] ← caused by ← [Cause C] ← caused by ← [Deeper Cause]
```

### Step 1.3: Validate Each Link (CLR Check)

| Link | Reservation Check | Pass/Fail | Revision |
|------|-------------------|-----------|----------|
| [A → B] | Cause Sufficiency | ⚠️ Fail | Add: [missing cause] |
| [B → C] | Causality Existence | ✓ Pass | - |
| [C → D] | Entity Existence | ⚠️ Fail | [cause doesn't exist] |

### Step 1.4: Identify Root Cause
**Root Cause:** [The deepest cause that, if removed, would eliminate multiple UDEs]

**Validation:** This root cause connects to [X] of [Y] UDEs through validated causal chains.

---

## Phase 2: Evaporating Cloud (What to Change To?)

### Step 2.1: Build the Conflict Structure

```
                    ┌─────────────────┐
                    │   OBJECTIVE     │
                    │       (A)       │
                    │ [Common goal]   │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
    ┌─────────────────┐           ┌─────────────────┐
    │  REQUIREMENT    │           │  REQUIREMENT    │
    │       (B)       │           │       (C)       │
    │ [Need this...]  │           │ [Need this...]  │
    └────────┬────────┘           └────────┬────────┘
             │                             │
             ▼                             ▼
    ┌─────────────────┐           ┌─────────────────┐
    │  PREREQUISITE   │◄─CONFLICT─►│  PREREQUISITE   │
    │       (D)       │           │      (D')       │
    │ [Must do this]  │           │ [Must do this]  │
    └─────────────────┘           └─────────────────┘
```

**Objective (A):** [What we ultimately want]
**Requirement (B):** [Necessary for A]
**Requirement (C):** [Also necessary for A]
**Prerequisite (D):** [Necessary for B]
**Prerequisite (D'):** [Necessary for C, but conflicts with D]

### Step 2.2: Surface Hidden Assumptions

| Arrow | Assumption | Validity |
|-------|------------|----------|
| A → B | [Why B is needed for A] | [challenge it] |
| A → C | [Why C is needed for A] | [challenge it] |
| B → D | [Why D is needed for B] | [challenge it] |
| C → D' | [Why D' is needed for C] | [challenge it] |
| D ↔ D' | [Why D and D' cannot coexist] | **[ATTACK THIS]** |

### Step 2.3: Find the Injection
*The action that invalidates an assumption and breaks the conflict*

**Weakest Assumption:** [The assumption most likely to be wrong]

**Injection:** [Specific action that makes D and D' compatible, or eliminates the need for one]

---

## Phase 3: Future Reality Tree (How to Cause Change?)

### Step 3.1: Build Forward Causal Chain

```
[INJECTION] → leads to → [Outcome 1] → leads to → [Outcome 2] → ... → [OBJECTIVE ACHIEVED]
```

| Step | If... | Then... | CLR Valid? |
|------|-------|---------|------------|
| 1 | [Injection implemented] | [First effect] | ✓ |
| 2 | [First effect occurs] | [Second effect] | ✓ |
| 3 | [Second effect occurs] | [Objective achieved] | ✓ |

### Step 3.2: Hunt for Negative Branches
*Assume the injection succeeds - what could go wrong?*

| Negative Branch | Severity | Trimming Injection |
|-----------------|----------|-------------------|
| [Unintended consequence 1] | [h/m/l] | [Secondary fix] |
| [Unintended consequence 2] | [h/m/l] | [Secondary fix] |

### Step 3.3: Final Solution Package

**Primary Injection:** [Main solution]

**Trimming Injections:** [Secondary fixes to prevent negative branches]

**Expected Outcomes:**
1. [UDE 1] eliminated because [reason]
2. [UDE 2] eliminated because [reason]
3. [UDE 3] eliminated because [reason]

---

## Summary

| Element | Finding |
|---------|---------|
| **Root Cause** | [From Phase 1] |
| **Core Conflict** | [D] vs [D'] |
| **Broken Assumption** | [The assumption we invalidated] |
| **Primary Injection** | [Main solution] |
| **Trimming Injections** | [Side-effect preventions] |
| **Confidence** | [h/m/l based on CLR validation pass rate] |
```

## Quality Checks

- Every causal link passed CLR validation
- Root cause connects to multiple UDEs (not just one)
- Conflict structure has genuine opposing prerequisites
- Injection attacks an assumption, not a requirement
- Future tree includes negative branch analysis
- Trimming injections address all high-severity risks

## Common Mistakes

- **Stopping at symptoms**: "Sales are down" is a UDE, not a root cause
- **Weak CLR validation**: Accepting "sounds reasonable" instead of rigorous checks
- **Fake conflicts**: D and D' don't actually conflict, just feel uncomfortable
- **Solution-first thinking**: Jumping to injections before understanding the conflict
- **Ignoring negative branches**: Assuming the fix has no side effects

## CLR Validator Prompt (For Adversarial Review)

Use this to critique any causal chain:

```
Review the following causal link: "[CAUSE] leads to [EFFECT]"

Check each reservation:
1. CLARITY: Do I understand both statements precisely?
2. ENTITY EXISTENCE: Is there evidence [CAUSE] actually exists?
3. CAUSALITY EXISTENCE: Is there a proven mechanism connecting them?
4. CAUSE SUFFICIENCY: Would [CAUSE] alone produce [EFFECT], or are other causes required?
5. ADDITIONAL CAUSE: Could something else independently cause [EFFECT]?
6. CAUSE-EFFECT REVERSAL: Could [EFFECT] actually be causing [CAUSE]?
7. PREDICTED EFFECT: If [CAUSE] exists, what other effects should we observe?
8. TAUTOLOGY: Is this circular reasoning?

Verdict: VALID / INVALID (specify which reservation failed)
Required revision: [if invalid, what must change]
```

## Example

**Problem:** "Our software shipping cycle is too slow"

**Phase 1: Current Reality Tree**

UDEs:
1. Releases take 3 weeks instead of target 1 week
2. Customer complaints about outdated features
3. Team morale declining

Causal Chain (after CLR validation):
```
[Slow releases] ← [Too many bugs found late] ← [Insufficient testing] ← [No time for testing]
                                             ↖
                                              [Developers rushing] ← [Pressure to ship fast]
```

Root Cause: Conflict between speed pressure and quality needs

**Phase 2: Evaporating Cloud**

- Objective (A): Deliver value to customers quickly
- Requirement (B): Ship features fast (to stay competitive)
- Requirement (C): Ship stable features (to maintain trust)
- Prerequisite (D): Minimize testing time
- Prerequisite (D'): Maximize testing time

Assumption attacked: "Testing takes a long time"

**Injection:** Implement automated CI/CD pipeline with parallel test suites

**Phase 3: Future Reality Tree**

```
[CI/CD Pipeline] → [Tests run in 10 min vs 2 days] → [Bugs caught immediately] → [Less rework] → [Faster shipping + Higher quality]
```

Negative Branch: "Developers may write fewer tests if automated"
Trimming Injection: Code coverage gates in CI (must maintain 80%+)

**Final Solution:**
- Primary: Automated CI/CD pipeline
- Trimming: Coverage gates, test-writing training
- Expected: 1-week cycles with fewer post-release bugs
