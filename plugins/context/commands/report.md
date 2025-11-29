---
description: Report misbehavior of any plugin skill, command, or subagent for later debugging
argument-hint: <problem description>
---

<objective>
Capture a fault report for plugin misbehavior, preserving enough context to enable debugging later.

This command:
- Captures user's description of the problem
- Records session ID and debug log reference
- Identifies recent actions before the report
- Saves structured report to shared/fault directory
</objective>

<context>
Session: !`cat ~/.claude/debug/latest | head -1 | grep -oE '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' || echo "unknown"`
Debug log: !`ls -la ~/.claude/debug/latest | awk '{print $NF}'`
Timestamp: !`date -u +%Y-%m-%dT%H:%M:%SZ`
</context>

<process>
1. **Capture Problem Description**:
   - If $ARGUMENTS provided: Use as problem description
   - Otherwise: Ask user to describe what went wrong

2. **Identify Component** (ask if not clear from description):
   - Plugin name (e.g., capability, context, outcome)
   - Component type: command | skill | subagent | hook
   - Component name (e.g., /capability:snapshot, delegate skill)

3. **Gather Context Automatically**:
   ```bash
   # Get session ID from latest debug log
   SESSION_ID=$(head -1 ~/.claude/debug/latest | grep -oE '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')

   # Get debug log filename
   DEBUG_LOG=$(readlink ~/.claude/debug/latest)

   # Get last 50 lines of activity (for recent actions)
   tail -50 ~/.claude/debug/latest | grep -E "Tool|Hook|command|skill"
   ```

4. **Create Report File**:
   - Generate report ID: `fault-YYYYMMDD-HHMMSS`
   - Path: `shared/fault/{report-id}.json`

5. **Save Report**:
   ```json
   {
     "id": "fault-20251129-153045",
     "reportedAt": "2025-11-29T15:30:45Z",
     "session": {
       "id": "abc12345-...",
       "debugLog": "abc12345-...txt",
       "logPath": "~/.claude/debug/abc12345-...txt"
     },
     "component": {
       "plugin": "capability",
       "type": "command",
       "name": "/capability:snapshot"
     },
     "problem": {
       "description": "User's description of what went wrong",
       "expected": "What user expected to happen",
       "actual": "What actually happened"
     },
     "recentActions": [
       "2025-11-29T15:30:00Z executePreToolHooks called for tool: Read",
       "2025-11-29T15:30:01Z Hook output received..."
     ],
     "status": "open"
   }
   ```

6. **Display Confirmation**:
   ```
   ## Fault Report Created

   ID: fault-20251129-153045
   Component: /capability:snapshot (command)
   Plugin: capability

   Session: abc12345-...
   Debug log: abc12345-...txt

   Problem: [User description]

   Report saved to: shared/fault/fault-20251129-153045.json

   To debug later:
   - Review debug log: ~/.claude/debug/abc12345-...txt
   - Use /debug-plugin command with this report
   ```
</process>

<questions>
If problem description doesn't clearly identify the component, ask:

1. **Which plugin?** (capability, context, outcome, think, workspace, plan)
2. **What type?** (command, skill, subagent, hook)
3. **What name?** (e.g., /capability:snapshot, delegate skill)
4. **What did you expect?** (optional but helpful)
</questions>

<success_criteria>
- Problem description captured
- Session ID recorded
- Debug log path saved
- Component identified
- Recent actions captured
- Report saved to shared/fault/
- User can locate report for debugging
</success_criteria>

<output_format>
**Confirmation Output** (Markdown):
- Report ID and timestamp
- Component details
- Session reference
- File location
- Next steps for debugging

**TOON Format** (for automation):
```toon
@type: Report
@id: fault/fault-20251129-153045
name: fault-report
reportNumber: fault-20251129-153045
dateCreated: 2025-11-29T15:30:45Z
actionStatus: CompletedActionStatus

session{id,debugLog}:
abc12345-...,abc12345-...txt

component{plugin,type,name|tab}:
capability	command	/capability:snapshot

x-problem: Command ran step-by-step instead of displaying cached content instantly
x-recentActionsCount: 5
x-reportPath: shared/fault/fault-20251129-153045.json
```
</output_format>
