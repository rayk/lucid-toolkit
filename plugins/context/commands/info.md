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
   - Read context tracking file from workspace
   - Parse active sessions and recent history
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
**Default Output**:
- Session summary (ID, duration, branch)
- Key statistics (files, tasks, tokens)
- Context health indicator
- Active outcomes
- Warnings

**Verbose Output** (--verbose):
- Full session details
- Complete statistics table
- Recent history (last 3 sessions)
- All focused outcomes with details
- Tool usage breakdown
</output_format>

<success_criteria>
- Session data loaded successfully
- Current session identified
- Statistics calculated correctly
- Context health assessed
- Warnings surfaced if present
- Output is scannable and actionable
</success_criteria>
