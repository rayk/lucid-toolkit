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
   - Read `status/sessions_summary.json`
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

<output_format>
**Default Output** (Markdown):
- Issue listing with descriptions
- Severity categorization
- File paths and timestamps
- Remediation recommendations

**TOON Format** (for machine consumption):
Add `output_format: toon` to command metadata when consumed by automation or health monitoring.

```toon
@type: Action
name: context-validation
actionStatus: FailedActionStatus
x-activeSessions: 5
x-issuesFound: 3
x-criticalIssues: 1
x-highIssues: 1
x-mediumIssues: 1

errors[1]{sessionId,severity,issue,age|tab}:
session-abc123	CRITICAL	MISSING TRANSCRIPT	24h

warnings[2]{sessionId,severity,issue,age|tab}:
session-def456	HIGH	ZOMBIE SESSION	36h
session-ghi789	MEDIUM	STALE SESSION	14h

recommendations[2]: Run /context:update to clean up,Use /context:update --strict for aggressive cleanup
```

**With All Healthy Sessions:**
```toon
@type: Action
name: context-validation
actionStatus: CompletedActionStatus
x-activeSessions: 3
x-issuesFound: 0

result: All sessions healthy, no action required
```

**When to use TOON:**
- Health monitoring automation
- Session cleanup scripts
- Subagent health checks

**Keep markdown for:**
- Human-facing validation reports
- Detailed issue explanations
- Interactive remediation guidance
</output_format>
