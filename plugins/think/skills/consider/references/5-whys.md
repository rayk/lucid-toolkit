# 5-Whys: Root Cause Analysis

Drill to root cause by asking "why" repeatedly until you hit actionable bedrock.

## When to Use

- Something broke and you need to prevent recurrence
- Symptoms keep reappearing despite fixes
- You're treating effects, not causes
- Need to find the intervention point

## Execution Template

```markdown
**Problem:** [clear, specific statement of what went wrong]

**Why 1:** [surface cause - the immediate, obvious reason]
↓
**Why 2:** [deeper - why did Why 1 happen?]
↓
**Why 3:** [even deeper - why did Why 2 happen?]
↓
**Why 4:** [approaching root - why did Why 3 happen?]
↓
**Why 5:** [root cause - why did Why 4 happen?]

**Root Cause:** [the actual thing to fix - should be actionable]

**Intervention:** [specific action at the root level that prevents recurrence]

**Verification:** [how to confirm the root cause is correct]
```

## Quality Checks

- Each "why" genuinely digs deeper (not sideways)
- Stops at actionable root (not infinite regress like "human nature")
- Root cause is something you can actually change
- Intervention addresses root, not symptoms
- Answer would prevent the original problem from recurring

## Common Mistakes

- Stopping too early (at symptoms, not causes)
- Going too abstract ("people make mistakes")
- Branching into multiple causes without following one thread
- Proposing fixes at surface level despite finding root

## Example

**Problem:** Customer reported data loss after update

**Why 1:** Database migration failed mid-execution
**Why 2:** Migration script timed out
**Why 3:** Script wasn't optimized for large tables
**Why 4:** No performance testing on production-scale data
**Why 5:** Test environment doesn't match production size

**Root Cause:** Test environment data volume doesn't reflect production

**Intervention:** Create production-scale test dataset, add migration performance benchmarks to CI

**Verification:** Run next migration against production-scale test data first
