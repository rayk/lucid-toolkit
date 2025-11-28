---
name: session info
description: Display current Claude Code session information and recent activity
---

<objective>
Display comprehensive information about the current Claude Code session including environment, statistics, focused outcomes, and recent session history.

This disambiguates "session status" (Claude Code session tracking) from "workspace status" (outcomes/capabilities).
</objective>

<context>
Session data: @status/sessions_summary.json
</context>

<process>
1. Read the current session from `activeSessions` array (match by current session ID or most recent)
2. Display **Current Session** section:
   - Session ID (truncated for readability)
   - Started at (human-readable time ago)
   - Session source (startup/resume/clear)
   - Git branch and commit
   - Permission mode
   - Duration so far
3. Display **Session Statistics**:
   - Events logged
   - Files modified
   - Tasks completed/failed
   - Git commits
   - Subagents launched
   - Tool usage counts (top 5)
4. Display **Focused Outcomes** (if any):
   - Outcome name and ID
   - Current task being worked on
   - Capabilities affected
5. Display **Last Session Summary** from `lastWorked`:
   - What was accomplished
   - Key decisions made
   - Next steps identified
6. Display **Recent Activity** (last 3-5 sessions from `recentHistory`):
   - Duration and accomplishments
   - Session end reason
   - Uncommitted files warning if any
7. Flag any **Stale Sessions** that may indicate crashes
</process>

<output_format>
Format the output as a clear, scannable report:

```
## Current Session
- ID: abc123... (truncated)
- Started: 2 hours ago (startup)
- Branch: master @ 18e036b
- Mode: default
- Duration: 45 min

## Statistics
| Metric | Value |
|--------|-------|
| Events | 12 |
| Files Modified | 4 |
| Tasks | 2 completed, 0 failed |
| Commits | 1 |
| Subagents | 3 |

## Tool Usage (Top 5)
- Read: 25
- Edit: 12
- Bash: 8
- Grep: 5
- Task: 3

## Focused Outcomes
(none currently focused)

## Last Session
- Completed: 1 hour ago
- Accomplishments: feat(outcomes): add 5-state workflow
- Duration: 20 min

## Recent Sessions (72h)
1. 034f7c23 - 0.3 min - feat(outcomes): add 5-state workflow
2. 6b937628 - 0.1 min - fix(commands): correct path
3. 3220fed7 - 20.5 min - fix(commands): correct path

## Warnings
⚠️ 1 stale session detected (possible crash)
```
</output_format>

<success_criteria>
- Current session information displayed accurately
- Statistics reflect actual session activity
- Focused outcomes shown if any are active
- Recent history provides context for work continuity
- Stale sessions flagged for user attention
- Output is scannable and not overwhelming
</success_criteria>
