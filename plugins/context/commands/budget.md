---
description: Display token budget status and delegation recommendations
argument-hint: [--forecast N]
---

<objective>
Show current token budget status, consumption patterns, and recommendations for delegation to preserve context headroom.

This command:
- Displays current token consumption
- Shows consumption breakdown by category
- Calculates remaining budget
- Provides delegation recommendations
- Forecasts based on planned operations
</objective>

<process>
1. **Load Budget Status**:
   - Current token count from session
   - Model context limit
   - Consumption rate (tokens/minute)

2. **Display Current Status**:
   ```
   ## Token Budget Status

   Current: 45,000 tokens
   Limit: 100,000 tokens
   Available: 55,000 tokens (55%)

   Status: [HEALTHY | WARNING | CRITICAL]
   ████████████░░░░░░░░ 45%
   ```

3. **Show Consumption Breakdown**:
   ```
   ## Consumption Breakdown

   ┌─────────────────────┬─────────┬─────┐
   │ Category            │ Tokens  │ %   │
   ├─────────────────────┼─────────┼─────┤
   │ System prompt       │ 8,000   │ 18% │
   │ Conversation        │ 22,000  │ 49% │
   │ Tool results        │ 12,000  │ 27% │
   │ Current message     │ 3,000   │ 6%  │
   └─────────────────────┴─────────┴─────┘
   ```

4. **Calculate Delegation Thresholds**:
   ```
   ## Delegation Thresholds

   At current usage (45%):
   - Direct ops: Up to 2 operations
   - 3+ ops: Delegate to subagent

   At 60% (WARNING):
   - Direct ops: Single operation only
   - 2+ ops: Delegate to subagent

   At 80% (CRITICAL):
   - All new work: Delegate
   - Consider: /context:compact
   ```

5. **Provide Recommendations**:
   ```
   ## Recommendations

   Current headroom allows:
   - 5-6 file reads (~10k tokens each)
   - 2-3 multi-file operations
   - 10+ delegated subagent tasks

   To preserve context:
   - Use haiku for searches (1500 token budget)
   - Delegate compound requests
   - Request TOON format from subagents
   ```

6. **Forecast (if --forecast N provided)**:
   ```
   ## Forecast: N planned operations

   Estimated consumption:
   - File reads (3): ~15,000 tokens
   - Code analysis: ~5,000 tokens
   - Edit operations: ~3,000 tokens
   Total: ~23,000 tokens

   Projected usage: 68,000 / 100,000 (68%)

   Recommendation: Delegate 2+ file reads to subagent
   ```
</process>

<budget_guidelines>
## Token Budget Reference

| Operation Type | Budget | Model |
|----------------|--------|-------|
| File search | 1500 | haiku |
| Yes/no validation | 800 | haiku |
| Code analysis | 2000 | sonnet |
| Multi-file fix | 2500 | sonnet |
| Complex synthesis | 3000 | opus |

## Warning Thresholds

| Usage | Status | Action |
|-------|--------|--------|
| <60% | HEALTHY | Normal operation |
| 60-80% | WARNING | Delegate 2+ ops |
| >80% | CRITICAL | Delegate all, compact |
</budget_guidelines>

<success_criteria>
- Current usage calculated
- Breakdown by category shown
- Thresholds and recommendations provided
- Forecast calculated (if requested)
- Actionable guidance provided
</success_criteria>

<output>
Displayed to user:
- Current token status with visual bar
- Consumption breakdown
- Delegation thresholds
- Recommendations
- Forecast (if requested)
</output>
