# Token Budget Reference

## Delegation Budgets by Operation Type

| Operation Type | Budget | Model | Use Case |
|----------------|--------|-------|----------|
| File search, pattern matching | 1500 | haiku | Finding files, grepping patterns |
| Yes/no validation | 800 | haiku | Quick binary decisions |
| Code analysis, flow tracing | 2000 | sonnet | Understanding code paths |
| Multi-file fix + commit | 2500 | sonnet | Edits across multiple files |
| Synthesis, complex reasoning | 3000 | opus | Strategic decisions |

---

## Model Selection

### Haiku (1500-2000 tokens)
Best for:
- File search and pattern matching
- Yes/no validation questions
- Simple lookups and data extraction
- High-volume parallel calls

Avoid for:
- Complex code analysis
- Multi-step reasoning
- Architecture decisions

### Sonnet (2000-2500 tokens)
Best for:
- Code analysis and flow tracing
- Multi-file fixes with commits
- Security and vulnerability assessment
- Following complex instructions

Avoid for:
- Simple searches (use haiku)
- Strategic synthesis (use opus)

### Opus (3000+ tokens)
Best for:
- Strategic synthesis and design
- Complex reasoning across domains
- Novel architecture proposals
- When sonnet quality is insufficient

Avoid for:
- Simple searches
- Routine operations
- High-volume tasks

---

## Context Window Thresholds

| Usage % | Status | Recommended Actions |
|---------|--------|---------------------|
| 0-40% | HEALTHY | Normal operations |
| 40-60% | CAUTION | Prefer delegation for 3+ ops |
| 60-80% | WARNING | Delegate 2+ ops, consider compact |
| 80-95% | CRITICAL | Delegate all work, compact now |
| >95% | DANGER | Must compact before continuing |

---

## Output Format Guidelines

### TOON Format (~40% savings)
Use for uniform data structures:

```toon
files[3]{path,type,lines}:
  src/auth.ts,service,145
  src/token.ts,utility,89
  src/session.ts,service,234
```

### JSON Format
Use only for complex, non-uniform objects:

```json
{
  "config": {
    "auth": {"type": "jwt", "expiry": 3600},
    "db": {"host": "localhost", "pool": 10}
  }
}
```

### Summary Format
For subagent responses:

```
## Findings
- Point 1 (file:line)
- Point 2 (file:line)

## Recommendation
Single actionable recommendation
```

---

## External Data Budgets

| Tool | Typical Payload | Budget Cap |
|------|-----------------|------------|
| firecrawl_scrape | 500-5000 | 2500 |
| WebFetch | 500-3000 | 2000 |
| firecrawl_search | 200-1000 | 1500 |
| MCP tools | varies | 2000 |

**Rule**: For N external fetches, budget = `min(N × 200, 2500)`

---

## Subagent Task Templates

### Search Task (Haiku, 1500)
```
Find all files matching [pattern] in [scope].
Return TOON format: files[N]{path,relevance}
```

### Analysis Task (Sonnet, 2000)
```
Analyze [target] for [aspect].
Return: 3-5 key findings, one recommendation.
Max 500 tokens.
```

### Fix Task (Sonnet, 2500)
```
Fix [issue] in [files].
Make edits, commit with message.
Return: files changed, commit hash.
```

### Synthesis Task (Opus, 3000)
```
Given [context], recommend [decision].
Consider: [factors].
Return: recommendation with rationale.
Max 800 tokens.
```

---

## Failure Recovery

| Symptom | Action |
|---------|--------|
| Output >30% over budget | Discard, retry same prompt |
| Wrong format | Discard, retry stricter |
| 2 consecutive failures | Decompose OR escalate model |
| Contradictory answers | Query ambiguous, refine |

**Never**: Parse or repair confused output. Discard and retry.

---

## Budget Calculation Examples

### Example 1: Codebase Search
```
Task: Find auth error handlers
Model: haiku
Budget: 1500 tokens
Output: TOON file list
```

### Example 2: Multi-File Fix
```
Task: Fix CORS configuration
Files: 3 estimated
Model: sonnet
Budget: 2500 tokens
Output: Changes made, commit hash
```

### Example 3: Architecture Decision
```
Task: Evaluate caching strategy
Options: 3 approaches
Model: opus
Budget: 3000 tokens
Output: Recommendation with trade-offs
```
