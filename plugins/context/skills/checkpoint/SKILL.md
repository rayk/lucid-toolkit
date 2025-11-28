---
name: checkpoint
description: Session tracking and work resumption context. Use at session start, end, or when work context needs preservation for crash recovery and continuity.
---

<skill_definition>
<purpose>Session tracking and work resumption context</purpose>
<trigger>Session start, end, or when work context needs preservation</trigger>
</skill_definition>

<core_principle>
**Automatic session lifecycle tracking enables work resumption and crash recovery.**

Every session captures:
- Environment snapshot at start
- Statistics from transcript at end
- Accomplishments and next steps
</core_principle>

<session_lifecycle>
## Session States

| State | Location | Duration |
|-------|----------|----------|
| Active | activeSessions[] | Until exit |
| Recent | recentHistory[] | 72 hours |
| Stale | activeSessions[] (flagged) | Until reconciliation |
| Archived | Pruned | Deleted |

### State Transitions
```
Start → Active
Active → Recent (normal end)
Active → Stale (1h inactivity)
Stale → Recent (reconciliation)
Recent → Archived (>72h)
```
</session_lifecycle>

<session_data>
## Session Data Captured

### At Session Start
- Session ID and source (startup/resume/clear)
- Git branch and commit hash
- Working directory
- Permission mode
- Transcript path

### During Session
- Events logged (capped at 100)
- Focused outcomes
- Tool usage counts
- Files modified

### At Session End
- Duration calculation
- Token consumption (from transcript)
- Tasks completed/failed
- Git commits made
- Accomplishments summary
- Uncommitted files count
</session_data>

<work_resumption>
## Work Resumption Context

The `lastWorked` object provides resumption data:

```json
{
  "sessionId": "sess-xyz",
  "completedAt": "2025-01-15T10:00:00Z",
  "outcomes": [
    {
      "outcomeId": 5,
      "outcomeName": "Authentication",
      "lastTask": "Implement token refresh",
      "workSummary": "Added JWT refresh logic"
    }
  ],
  "context": {
    "gitBranch": "feature/auth",
    "filesModified": ["src/auth.ts", "src/token.ts"],
    "keyDecisions": ["Using RS256 algorithm"],
    "nextSteps": ["Add tests", "Update docs"]
  }
}
```

### Using Resumption Context
1. Check `lastWorked` for recent session
2. Review outcomes and tasks in progress
3. Note key decisions made
4. Continue from next steps
</work_resumption>

<stale_detection>
## Stale Session Detection

### Detection Criteria
- No activity for >1 hour
- Session still in activeSessions[]
- Possible causes: crash, network loss, closed terminal

### Indicators in Data
- `isStale: true` flag
- `lastActivityAt` timestamp old
- Listed in `staleSessionsDetected[]`

### Recovery
1. Run `/context:info` to see stale warnings
2. Run reconciliation to clean up
3. Sessions moved to history with crash reason
</stale_detection>

<checkpoint_operations>
## Checkpoint Commands

### `/context:info`
Display current session context:
- Session ID and duration
- Statistics (events, files, tasks, tokens)
- Focused outcomes
- Last session summary
- Stale session warnings

### `/context:checkpoint`
Manual checkpoint to preserve state:
- Captures current accomplishments
- Notes key decisions
- Saves next steps
- Updates session statistics

### `/context:compact`
Reduce context window usage:
- Summarizes conversation history
- Archives intermediate results
- Preserves essential context only
- Reports tokens saved

### `/context:budget`
Display token budget status:
- Current consumption
- Available headroom
- Delegation recommendations
- Warning thresholds
</checkpoint_operations>

<transcript_parsing>
## Statistics from Transcript

Session end parses the conversation transcript:

| Statistic | Source |
|-----------|--------|
| tokensConsumed | Token count from API |
| filesModified | Write/Edit tool calls |
| tasksCompleted | Successful operations |
| tasksFailed | Error responses |
| gitCommits | Bash with git commit |
| toolUsageCounts | Tool name frequency |
| subagentsLaunched | Task tool calls |

### Automatic Accomplishment Generation
If not provided, accomplishments derived from:
- Files modified count
- Commits made
- Tasks completed
- Outcomes worked on
</transcript_parsing>

<indexes>
## Quick Lookup Indexes

### indexByOutcome
```json
{
  "outcomes/in-progress/005-auth/outcome_track.json": ["sess-abc", "sess-def"]
}
```
Find sessions that worked on specific outcomes.

### indexByBranch
```json
{
  "feature/auth": ["sess-abc"],
  "main": ["sess-xyz"]
}
```
Find sessions by git branch.
</indexes>

<best_practices>
## Checkpoint Best Practices

1. **Let Hooks Handle It**: SessionStart/End hooks manage lifecycle automatically

2. **Manual Checkpoints**: Use when:
   - About to attempt risky operation
   - Completed significant milestone
   - Context getting large
   - Before switching focus

3. **Work Resumption**: Start sessions by checking:
   - `lastWorked.nextSteps` for continuation
   - `lastWorked.keyDecisions` for context
   - `staleSessionsDetected` for cleanup

4. **72-Hour Window**: Recent history auto-prunes
   - Sufficient for work resumption
   - Keeps data manageable
   - Archive important context elsewhere
</best_practices>
