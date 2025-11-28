# Token Budget Enforcement

Default assumption: Any request requires delegation.

Direct execution ONLY when operation meets ALL criteria:

| Criteria | Threshold |
|----------|-----------|
| Tool calls | Exactly 1-2, with certainty |
| File path | Known and specific |
| Output tokens | <500, predictable |
| Search component | None |

If uncertain about ANY row → Delegate.

## Delegation Budgets by Operation Type

| Operation Type | Budget | Model |
|----------------|--------|-------|
| File search, pattern matching | 1500 | haiku |
| Yes/no validation | 800 | haiku |
| Code analysis, flow tracing | 2000 | sonnet |
| Multi-file fix + commit | 2500 | sonnet |
| Synthesis, complex reasoning | 3000 | opus |
