---
name: get-claude-logs
description: Access and analyze Claude Code debug logs efficiently. Use when investigating hook failures, session issues, MCP problems, or any Claude Code behavior that needs diagnosis.
allowed-tools:
  - Bash
  - Grep
---

<objective>
Efficiently access and analyze Claude Code debug logs to diagnose issues with minimal token usage and maximum insight.
</objective>

<quick_start>
**The golden rule: Read comprehensively ONCE, not incrementally multiple times.**

```bash
# For current session issues (hooks, startup, recent activity)
tail -2000 ~/.claude/debug/latest

# For specific patterns across recent activity
tail -2000 ~/.claude/debug/latest | grep -E "pattern1|pattern2|pattern3"

# For time-based analysis (last 5 minutes of activity)
tail -5000 ~/.claude/debug/latest | grep "$(date +%Y-%m-%d)"
```

**NEVER use Read tool on log files** - they exceed token limits and will fail or waste tokens.
</quick_start>

<log_locations>
**Primary log file:**

```bash
~/.claude/debug/latest
```

This is a symlink to the current session's debug log.

**All debug logs:**

```bash
~/.claude/debug/
```

Organized by timestamp. Each file is a complete session log.

**Session-specific environment:**

```bash
~/.claude/session-env/<session-id>/
```

Contains session-specific state files.

**Shell snapshots:**

```bash
~/.claude/shell-snapshots/
```

Contains shell state captures for debugging.
</log_locations>

<log_structure>
**Log entry format:**

```
2025-11-20T02:53:40.688Z [DEBUG] Message content here
2025-11-20T02:53:40.689Z [ERROR] Error message here
2025-11-20T02:53:41.107Z [INFO] Informational message
```

**Components:**

- Timestamp: ISO 8601 format with milliseconds
- Level: `[DEBUG]`, `[INFO]`, `[ERROR]`, `[WARN]`
- Message: Contextual information

**Common log patterns:**

- Hook execution: `Getting matching hook commands for <HookType>`
- Hook results: `Matched X unique hooks for query "..."`
- Tool usage: `executePreToolHooks called for tool: <ToolName>`
- MCP activity: `MCP server "<name>": ...`
- Permissions: `Permission suggestions for <Tool>`
- Errors: `[ERROR]` tag with stack traces
</log_structure>

<efficient_search_workflow>
<step_1>
**Determine the time scope of your issue**

- Current session problem? → Recent logs (tail -2000)
- Startup/initialization issue? → Very recent logs (tail -500)
- Pattern across sessions? → Search multiple log files
- Specific timestamp? → Use grep with date/time
</step_1>

<step_2>
**Do ONE comprehensive read**

```bash
# Capture to temp file for multiple analyses
tail -2000 ~/.claude/debug/latest > /tmp/debug_snapshot.log

# Now grep multiple times without re-reading the file
grep -i "error" /tmp/debug_snapshot.log
grep "SessionStart" /tmp/debug_snapshot.log
grep "MCP" /tmp/debug_snapshot.log
```

This is MUCH more efficient than:

```bash
# INEFFICIENT - re-reads file 3 times
tail -2000 ~/.claude/debug/latest | grep -i "error"
tail -2000 ~/.claude/debug/latest | grep "SessionStart"
tail -2000 ~/.claude/debug/latest | grep "MCP"
```
</step_2>

<step_3>
**Use context flags to see surrounding lines**

```bash
# Show 5 lines before and after matches
grep -C5 "pattern" /tmp/debug_snapshot.log

# Show 10 lines after matches
grep -A10 "pattern" /tmp/debug_snapshot.log

# Show 10 lines before matches
grep -B10 "pattern" /tmp/debug_snapshot.log
```

This reveals the timeline and context around events.
</step_3>
</efficient_search_workflow>

<common_diagnostic_patterns>
<hook_failures>
**Find hook execution:**

```bash
tail -2000 ~/.claude/debug/latest | grep -E "SessionStart|SessionEnd|Hook output|Matched.*hooks"
```

**Key indicators:**

- "Matched X unique hooks" → Hook was found and triggered
- "Hook output does not start with {" → Hook crashed (returned non-JSON)
- No "Matched" message → Hook not configured or matcher didn't match
</hook_failures>

<mcp_issues>
**Find MCP server activity:**

```bash
tail -2000 ~/.claude/debug/latest | grep "MCP server" | grep -E "ERROR|failed|timeout"
```

**Common patterns:**

- "Connection failed" → Server not running or wrong port
- "No token data found" → Expected but often harmless
- "Tool 'X' completed successfully" → Tool worked
</mcp_issues>

<tool_execution>
**Trace tool usage:**

```bash
tail -2000 ~/.claude/debug/latest | grep -E "executePreToolHooks|PostToolUse|PermissionRequest"
```

**Shows:**

- Which tools were called
- What hooks fired for those tools
- Permission checks and approvals
</tool_execution>

<permission_issues>
**Find permission requests and decisions:**

```bash
tail -2000 ~/.claude/debug/latest | grep -E "Permission suggestions|Applying permission update"
```

**Shows:**

- What permissions were requested
- What rules were added
- Session vs global permission changes
</permission_issues>

<errors_and_warnings>
**Find all errors:**

```bash
tail -2000 ~/.claude/debug/latest | grep -E "\[ERROR\]|\[WARN\]"
```

**With context (recommended):**

```bash
tail -2000 ~/.claude/debug/latest | grep -B5 -A5 "\[ERROR\]"
```
</errors_and_warnings>
</common_diagnostic_patterns>

<anti_patterns>
**DON'T: Incremental searching**

```bash
tail -100 ~/.claude/debug/latest | grep "pattern"   # Too small, no results
tail -200 ~/.claude/debug/latest | grep "pattern"   # Still searching...
tail -500 ~/.claude/debug/latest | grep "pattern"   # Getting closer...
tail -1000 ~/.claude/debug/latest | grep "pattern"  # Maybe now?
# ... wastes tokens, fragments context
```

**DO: Comprehensive single read**

```bash
tail -2000 ~/.claude/debug/latest | grep "pattern"  # Get everything once
```

**DON'T: Use Read tool**

```bash
Read(~/.claude/debug/latest)  # Exceeds token limits, will fail
```

**DO: Use Bash with tail**

```bash
Bash: tail -2000 ~/.claude/debug/latest
```

**DON'T: Multiple separate tail commands**

```bash
Bash: tail -100 ~/.claude/debug/latest | grep "error"
Bash: tail -100 ~/.claude/debug/latest | grep "warn"
Bash: tail -100 ~/.claude/debug/latest | grep "hook"
```

**DO: Single tail, multiple patterns**

```bash
tail -100 ~/.claude/debug/latest | grep -E "error|warn|hook"
```

**DON'T: Start too narrow**

```bash
# Assumes you know exactly what to search for
tail -100 ~/.claude/debug/latest | grep "SessionStart with query: startup"
```

**DO: Start broad, then narrow**

```bash
# Get full context first, then search within it
tail -2000 ~/.claude/debug/latest > /tmp/debug.log
grep "SessionStart" /tmp/debug.log
```
</anti_patterns>

<sizing_guide>
**How much to tail?**

| Issue Type               | Recommended Size | Reasoning                          |
|--------------------------|------------------|------------------------------------|
| Current session startup  | 500-1000 lines   | Startup happens quickly            |
| Hook execution           | 1000-2000 lines  | Hooks fire during lifecycle events |
| Tool usage investigation | 2000-3000 lines  | May span multiple operations       |
| Session history          | 5000+ lines      | Covers more time                   |
| Cross-session patterns   | Multiple files   | Need historical data               |

**Rule of thumb:** When in doubt, use **tail -2000** - it's the sweet spot for most diagnostics.
</sizing_guide>

<timeline_analysis>
**Understanding event sequences:**

Logs are chronological. To understand what happened:

1. Find the key event (error, hook trigger, etc.)
2. Look at 20-50 lines BEFORE it (what led to this?)
3. Look at 20-50 lines AFTER it (what was the consequence?)

```bash
# Example: Understanding a hook failure
tail -2000 ~/.claude/debug/latest | grep -B30 -A30 "Hook output does not start"
```

This shows:

- What triggered the hook (30 lines before)
- What happened when it failed (the error line)
- What Claude Code did next (30 lines after)
</timeline_analysis>

<performance_tips>
**Token optimization:**

| Approach        | Commands        | Token Usage   | Time |
|-----------------|-----------------|---------------|------|
| **Efficient**   | 1-3 Bash calls  | 10,000-15,000 | Fast |
| **Inefficient** | 8-12 Bash calls | 40,000-60,000 | Slow |

**The difference:**

- Efficient: One comprehensive read, analyze in temp file
- Inefficient: Multiple incremental searches, re-reading file each time

**Savings:** 60-75% fewer tokens, 50% faster diagnosis
</performance_tips>

<success_criteria>
You're using debug logs efficiently when:

- You use 3 or fewer Bash commands for the diagnostic phase
- You read comprehensively once, not incrementally
- You use grep with context flags (-A, -B, -C)
- You understand the timeline by reading surrounding lines
- Total token usage < 15,000 for log analysis

You're being inefficient when:

- You make 5+ separate tail/grep commands
- You start with tail -100 and keep increasing
- You try to use Read tool on logs
- You search for narrow patterns before understanding context
- Token usage > 40,000 for log analysis
</success_criteria>

<examples>
<example_1>
**Scenario:** Diagnose why SessionStart hook failed

**Efficient approach:**

```bash
# Single comprehensive read
tail -2000 ~/.claude/debug/latest > /tmp/session_diag.log

# Find hook execution timeline
grep -E "SessionStart|Hook output|Matched.*hooks" /tmp/session_diag.log

# Get context around failure
grep -B20 -A10 "Hook output does not start" /tmp/session_diag.log
```

**Result:** 3 commands, ~12,000 tokens, found root cause
</example_1>

<example_2>
**Scenario:** Investigate MCP server connection issues

**Efficient approach:**

```bash
# Get recent activity
tail -3000 ~/.claude/debug/latest | grep "MCP server" > /tmp/mcp_activity.log

# Find errors with context
grep -C10 -E "ERROR|failed|timeout" /tmp/mcp_activity.log
```

**Result:** 2 commands, ~8,000 tokens, identified connection problem
</example_2>

<example_3>
**Scenario:** Understand why a tool wasn't called

**Efficient approach:**

```bash
# Comprehensive recent log
tail -2000 ~/.claude/debug/latest > /tmp/tool_trace.log

# Find tool execution flow
grep -E "executePreToolHooks|PostToolUse|Permission" /tmp/tool_trace.log

# Check what tools were actually called
grep "called for tool:" /tmp/tool_trace.log
```

**Result:** 3 commands, ~10,000 tokens, found permission blocking issue
</example_3>
</examples>
