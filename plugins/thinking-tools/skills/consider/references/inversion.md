# Inversion: Failure Mode Analysis

Instead of asking "How do I succeed?", ask "What would guarantee failure?" then systematically avoid those things.

## When to Use

- Planning something important where failure is costly
- Optimistic planning feels incomplete
- Need to surface risks that positive thinking misses
- Want to build defensive strategies
- "Pre-mortem" before launching

## Execution Template

```markdown
**Goal:** [what success looks like - be specific]

---

## Guaranteed Failure Modes
*What would definitely cause this to fail?*

| Failure Mode | Why It Fails | Avoidance Strategy |
|--------------|--------------|-------------------|
| [Way to fail #1] | [Mechanism of failure] | [Specific action to avoid] |
| [Way to fail #2] | [Mechanism of failure] | [Specific action to avoid] |
| [Way to fail #3] | [Mechanism of failure] | [Specific action to avoid] |
| [Way to fail #4] | [Mechanism of failure] | [Specific action to avoid] |

---

## Anti-Goals (Never Do List)
*Behaviors and actions to explicitly prohibit*

- [ ] Never: [behavior to eliminate]
- [ ] Never: [behavior to eliminate]
- [ ] Never: [behavior to eliminate]

---

## Success by Avoidance
*Path to success via negativa*

By simply NOT doing [list key avoidances], success becomes much more likely because:
[Explanation of how avoiding failures creates success conditions]

---

## Remaining Risks
*What's left after avoiding obvious failures?*

| Risk | Mitigation | Acceptable? |
|------|------------|-------------|
| [Residual risk] | [How to handle] | YES/NO |

---

## Failure Triggers to Monitor
*Early warning signs that you're heading toward failure*

- Warning sign: [observable indicator]
- Warning sign: [observable indicator]
```

## Quality Checks

- Failure modes are specific and realistic (not generic)
- Avoidance strategies are actionable (not "be careful")
- Surfaces risks that optimistic planning would miss
- Anti-goals are clear behavioral boundaries
- Remaining risks are acknowledged, not hidden

## Common Mistakes

- Being too abstract ("poor communication" - what specifically?)
- Only listing external failures (include self-inflicted wounds)
- Avoidance strategies that are just "try harder"
- Not being honest about embarrassing failure modes

## Inversion Questions

- "What would make this definitely fail?"
- "How could I sabotage this if I wanted to?"
- "What mistakes do others make in this situation?"
- "What would I regret not having done?"
- "What's the stupidest thing I could do here?"

## Example

**Goal:** Launch successful SaaS product in 6 months

**Guaranteed Failure Modes:**
| Failure Mode | Why It Fails | Avoidance Strategy |
|--------------|--------------|-------------------|
| Build without customer input | Creates product nobody wants | Weekly customer interviews from day 1 |
| Perfectionism before launch | Never ship, run out of runway | Define MVP, launch at 80% |
| Solo founder burnout | Can't sustain pace alone | Find co-founder or build support system |
| Ignore unit economics | Grow into bankruptcy | Model CAC/LTV before scaling |
| Technical debt avalanche | Can't iterate fast enough | Refactor budget: 20% of sprint |

**Anti-Goals:**
- [ ] Never: Build features without user request/data
- [ ] Never: Delay launch for "one more thing"
- [ ] Never: Scale marketing before retention is proven

**Success by Avoidance:**
By NOT building in isolation, NOT perfectionist-delaying, and NOT scaling prematurely, we maintain focus on validated learning and sustainable growth.

**Remaining Risks:**
| Risk | Mitigation | Acceptable? |
|------|------------|-------------|
| Market timing wrong | Stay lean, extend runway | YES |
| Competitor moves faster | Focus on niche, not feature parity | YES |
