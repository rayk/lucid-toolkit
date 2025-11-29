---
description: Display current session context and status
argument-hint: [--verbose]
---

<objective>
Show comprehensive session context including current status, statistics, and work resumption information.

This command displays:
- Current session ID, duration, and environment
- Session statistics (events, files, tasks, tokens)
- Focused outcomes and capabilities
- Last session summary with accomplishments
- Context window health indicators
- Stale session warnings
</objective>

<process>
1. **Load Session Data**:
   - Read `.lucid/current_session.json` for active session
   - Read `status/sessions_summary.json` for history
   - Calculate current session duration

2. **Display Current Session**:
   ```
   ## Current Session
   ID: sess-xyz123
   Started: 2025-01-15 10:30:00 (45 min ago)
   Source: startup | resume | clear
   Branch: feature/auth @ abc1234
   Permission: default | plan | acceptEdits
   ```

3. **Display Statistics**:
   ```
   ## Session Statistics
   ┌─────────────────┬───────┐
   │ Metric          │ Value │
   ├─────────────────┼───────┤
   │ Events logged   │ 23    │
   │ Files modified  │ 5     │
   │ Tasks completed │ 8     │
   │ Tasks failed    │ 1     │
   │ Git commits     │ 2     │
   │ Tokens consumed │ 45000 │
   │ Subagents used  │ 4     │
   └─────────────────┴───────┘
   ```

4. **Display Context Health**:
   ```
   ## Context Health
   Token usage: 45,000 / 100,000 (45%)
   Status: [HEALTHY | WARNING | CRITICAL]

   Recommendation: [None | Consider compacting | Delegate remaining work]
   ```

5. **Display Focused Work** (if any):
   ```
   ## Focused Outcomes
   - [005] Authentication System (3 tasks completed)
     Current: Implement token refresh
     Capabilities: auth-system, security
   ```

6. **Display Last Session Summary** (if available):
   ```
   ## Last Session (completed 2h ago)
   Duration: 1h 23min | Tokens: 67,000
   Branch: feature/auth

   Accomplishments:
   - Implemented JWT token validation
   - Added refresh token endpoint

   Next Steps:
   - Add unit tests for token service
   - Update API documentation
   ```

7. **Display Warnings** (if any):
   ```
   ## ⚠️ Warnings
   - 2 stale sessions detected (possible crashes)
     Run /context:checkpoint to reconcile
   ```
</process>

<output_format>
**Default Output** (Markdown):
- Session summary (ID, duration, branch)
- Key statistics (files, tasks, tokens)
- Context health indicator
- Active outcomes
- Warnings

**Verbose Output** (--verbose, Markdown):
- Full session details
- Complete statistics table
- Recent history (last 3 sessions)
- All focused outcomes with details
- Tool usage breakdown

**TOON Format** (for machine consumption):
Add `output_format: toon` to command metadata when consumed by subagents or for data exchange.

```toon
@type: Action
@id: session/sess-xyz123
name: current-session
actionStatus: ActiveActionStatus
startTime: 2025-01-15T10:30:00Z
x-duration: 45min
x-source: startup
x-branch: feature/auth
x-commitSha: abc1234
x-permission: default

stats{metric,value}:
eventsLogged,23
filesModified,5
tasksCompleted,8
tasksFailed,1
gitCommits,2
tokensConsumed,45000
subagentsUsed,4

health:
usage: 45000
limit: 100000
percent: 45
status: HEALTHY

focusedOutcomes[1]{@id,tasksCompleted,currentTask|tab}:
005-authentication	3	Implement token refresh
```

**When to use TOON:**
- Subagent return values showing session state
- Cross-plugin data exchange requiring session info
- Status displays consumed by automation

**Keep markdown for:**
- Human-facing terminal output
- Verbose explanatory text
- Last session summary narratives
</output_format>

<success_criteria>
- Session data loaded successfully
- Current session identified
- Statistics calculated correctly
- Context health assessed
- Warnings surfaced if present
- Output is scannable and actionable
</success_criteria>
