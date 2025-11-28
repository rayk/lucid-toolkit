# Occam's Razor: Simplest Explanation

Among competing explanations, prefer the one with fewest assumptions. Simplest doesn't mean easiest - it means fewest moving parts.

## When to Use

- Multiple explanations seem plausible
- Diagnosis is unclear with competing theories
- Tempted to construct elaborate explanations
- Need to cut through complexity to find truth
- Debugging: many possible causes

## Execution Template

```markdown
**Phenomenon:** [what you're trying to explain]

**Known Facts:**
- [Observed fact #1]
- [Observed fact #2]
- [Observed fact #3]

---

## Candidate Explanations

| Explanation | Required Assumptions |
|-------------|---------------------|
| [Theory A] | 1. [assumption], 2. [assumption], 3. [assumption] |
| [Theory B] | 1. [assumption], 2. [assumption] |
| [Theory C] | 1. [assumption] |

---

## Assumption Audit

| Assumption | Evidence | Verdict |
|------------|----------|---------|
| [Assumption from above] | [Supporting/contradicting evidence] | SUPPORTED / UNSUPPORTED / UNKNOWN |
| [Assumption from above] | [Supporting/contradicting evidence] | SUPPORTED / UNSUPPORTED / UNKNOWN |

---

## Simplest Valid Explanation

**Winner:** [The explanation with fewest UNSUPPORTED assumptions]

**Why This Wins:**
- Explains all observed facts: [yes/no for each fact]
- Assumptions required: [count]
- Unsupported assumptions: [count]

**What It Explains:** [How this theory accounts for the observations]

---

## What Would Change the Answer
*Evidence that would shift to a different explanation*

- If we observed [X], then [other theory] becomes more likely because...
```

## Quality Checks

- All plausible explanations enumerated (not just two)
- Assumptions are explicit and countable
- "Supported" vs "unsupported" is evidence-based
- Simplest explanation still accounts for ALL facts
- Not oversimplifying (must fit observations)

## Common Mistakes

- Confusing "simple" with "familiar" or "comfortable"
- Ignoring inconvenient facts that don't fit simple theory
- Counting assumptions inconsistently across theories
- Treating absence of evidence as evidence of absence

## The Razor in Practice

Occam's Razor is a **heuristic, not a law**. It says:
- Don't multiply entities beyond necessity
- The explanation requiring fewer assumptions is **more likely** to be true
- But simpler isn't always right - just start there

## Example

**Phenomenon:** Website traffic dropped 40% last week

**Known Facts:**
- Traffic dropped starting Tuesday
- Google organic traffic down 60%
- Direct traffic unchanged
- No site changes deployed last week

**Candidate Explanations:**
| Explanation | Required Assumptions |
|-------------|---------------------|
| Google algorithm update | 1. Google changed algorithm |
| Competitor took rankings | 1. Competitor improved, 2. They targeted our keywords, 3. Google re-ranked |
| Technical SEO issue | 1. Something broke, 2. It specifically affects Google, 3. We missed it |
| Seasonal variation | 1. This week is always low, 2. Pattern holds this year |

**Assumption Audit:**
| Assumption | Evidence | Verdict |
|------------|----------|---------|
| Google changed algorithm | Industry reports confirm update Tuesday | SUPPORTED |
| Competitor improved | No evidence checked yet | UNKNOWN |
| Something broke | No changes deployed, GSC shows no errors | UNSUPPORTED |
| Seasonal pattern | Last year same week was normal | UNSUPPORTED |

**Simplest Valid Explanation:**
**Winner:** Google algorithm update
- Only requires 1 supported assumption
- Timing matches exactly (Tuesday)
- Explains why only Google traffic affected

**What Would Change:** If we find technical errors in Google Search Console, technical issue becomes more likely
