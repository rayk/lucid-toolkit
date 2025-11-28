# Second-Order Thinking: Consequence Chains

Think through the consequences of consequences. First-order thinking stops at immediate effects; second-order follows the chain.

## When to Use

- Making decisions with long-term implications
- Actions might trigger feedback loops
- Need to anticipate unintended consequences
- Evaluating interventions in complex systems
- "And then what?" needs to be answered

## The Levels

- **First-order**: Immediate, obvious effects
- **Second-order**: Effects of the effects
- **Third-order**: Effects of the effects of the effects (usually where you stop)

## Execution Template

```markdown
**Action:** [what's being considered or implemented]

**Context:** [relevant background on the system/situation]

---

## First-Order Effects (Immediate)
*What happens right away? The obvious, direct consequences.*

| Effect | Magnitude | Timing |
|--------|-----------|--------|
| [Direct effect 1] | [high/medium/low] | [immediate/days/weeks] |
| [Direct effect 2] | [high/medium/low] | [immediate/days/weeks] |

---

## Second-Order Effects (And Then What?)
*For each first-order effect, what does IT cause?*

| First-Order | Leads To | Magnitude | Timing |
|-------------|----------|-----------|--------|
| [Effect 1] | → [Consequence A] | [h/m/l] | [weeks/months] |
| [Effect 1] | → [Consequence B] | [h/m/l] | [weeks/months] |
| [Effect 2] | → [Consequence C] | [h/m/l] | [weeks/months] |

---

## Third-Order Effects (And Then?)
*Follow the most significant chains further*

| Second-Order | Leads To | Notes |
|--------------|----------|-------|
| [Consequence A] | → [Downstream result] | [why this matters] |
| [Consequence C] | → [Downstream result] | [why this matters] |

---

## Feedback Loops Identified
*Self-reinforcing or self-correcting dynamics*

| Loop | Type | Mechanism |
|------|------|-----------|
| [Description] | Reinforcing / Balancing | [How it feeds back] |

---

## Delayed Consequences
*Effects that aren't obvious initially but matter long-term*

| Consequence | Why Delayed | When It Hits |
|-------------|-------------|--------------|
| [Effect] | [Mechanism] | [Timeline] |

---

## Revised Assessment

**Initial gut reaction:** [What the action seemed like at first]

**After tracing chains:** [What it looks like now]

**Verdict:** [Is the action still worth it?]

**What to monitor:** [Early indicators of second-order effects]
```

## Quality Checks

- Chains are traced causally (not just associated)
- Includes negative AND positive downstream effects
- Identifies feedback loops (crucial in complex systems)
- Delayed consequences made explicit
- Assessment actually changes based on analysis (or confirms)

## Common Mistakes

- Stopping at first-order effects
- Only tracing the optimistic path
- Missing feedback loops
- Assuming linear cause-effect in complex systems
- Not considering adaptive responses from other actors

## Second-Order Questions

- "And then what happens?"
- "How will others respond to this?"
- "What does this make possible that wasn't before?"
- "What does this make impossible that was possible before?"
- "What equilibrium does this disrupt?"

## Example

**Action:** Implement strict code review policy (all PRs need 2 approvals)

**First-Order Effects:**
| Effect | Magnitude | Timing |
|--------|-----------|--------|
| Fewer bugs reach production | High | Immediate |
| PRs take longer to merge | High | Immediate |
| Reviewers spend more time reviewing | Medium | Immediate |

**Second-Order Effects:**
| First-Order | Leads To | Magnitude | Timing |
|-------------|----------|-----------|--------|
| PRs take longer | → Developers batch changes into larger PRs | Medium | Weeks |
| PRs take longer | → Frustration, pressure to rubber-stamp | Medium | Weeks |
| Larger PRs | → Reviews become superficial (too much to review) | High | Months |
| More review time | → Less time for own development work | Medium | Weeks |

**Third-Order Effects:**
| Second-Order | Leads To | Notes |
|--------------|----------|-------|
| Superficial reviews | → Bug rate returns to baseline | Defeats original purpose |
| Less dev time | → Slower feature delivery | Business pressure increases |

**Feedback Loops:**
| Loop | Type | Mechanism |
|------|------|-----------|
| Large PR → Bad review → More bugs → Stricter rules → Larger PRs | Reinforcing | Policy creates the problem it solves |

**Revised Assessment:**
**Initial:** "More review = fewer bugs, obviously good"
**After tracing:** Policy likely backfires within 3-6 months

**Verdict:** Modify approach - require 2 approvals only for critical paths, keep 1 approval for smaller changes, add PR size limits
