---
description: Validate context tracking health and detect zombie sessions
---

Run comprehensive context validation to check for:
- Sessions with missing transcript files
- Zombie sessions (old with no activity)
- Discrepancies in session state
- Recommendations for cleanup

<process>
1. **Load Context Summary**
   - Read `status/context_summary.json`
   - Count active sessions

2. **Validate Each Session**
   - Check transcript file exists
   - Calculate session age
   - Flag issues:
     - Missing transcript → MISSING TRANSCRIPT
     - Age > 24 hours → ZOMBIE SESSION
     - Age > 12 hours → STALE SESSION

3. **Generate Report**
   - List all issues found
   - Provide remediation commands
</process>

<output_format>
```
Validating Context Health...

Active Sessions: 5

Checking for issues...

MISSING TRANSCRIPT: session-abc123
   Path: ~/.claude/sessions/abc123.jsonl
   Started: 2025-01-15T10:00:00Z

ZOMBIE SESSION: session-def456
   Age: 36 hours
   Started: 2025-01-14T02:00:00Z

STALE SESSION: session-ghi789
   Age: 14 hours
   Started: 2025-01-15T20:00:00Z

Recommendations:

To clean up zombie sessions and missing transcripts:
  /context:update

For aggressive cleanup (2h threshold):
  /context:update --strict --verbose

To preview changes without applying:
  /context:update --dry-run --verbose
```
</output_format>

<severity_levels>
| Level | Condition | Action |
|-------|-----------|--------|
| CRITICAL | Missing transcript | Archive session |
| HIGH | Zombie (>24h) | Review and cleanup |
| MEDIUM | Stale (>12h) | Monitor |
| LOW | Normal (<12h) | No action |
</severity_levels>

<success_criteria>
- All sessions validated
- Issues categorized by severity
- Actionable recommendations provided
</success_criteria>
