---
description: Report misbehavior of any ws plugin component for later debugging
argument-hint: <problem description>
model-hint: haiku
allowed-tools: [Bash, Write, AskUserQuestion]
---

<objective>
Capture a fault report for ws plugin misbehavior, preserving enough context to enable debugging later.

This command:
- Captures user's description of the problem
- Records session ID and debug log reference
- Identifies recent actions before the report
- Saves structured report to ~/.claude/fault directory
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
   - Area: cap (Capabilities) | out (Outcomes) | des (Designs) | pln (Plans) | exe (Execution)
   - Component type: command | skill | subagent | hook
   - Component name (e.g., /ws:version, specific skill)

3. **Gather Context Automatically**:
   - Extract session ID from ~/.claude/debug/latest
   - Get debug log filename from the symlink
   - Capture last 50 lines of relevant activity

4. **Create Report File**:
   - Generate report ID: `ws-fault-YYYYMMDD-HHMMSS`
   - Path: `~/.claude/fault/{report-id}.json`

5. **Save Report**:
   ```json
   {
     "id": "ws-fault-20251202-153045",
     "reportedAt": "2025-12-02T15:30:45Z",
     "session": {
       "id": "abc12345-...",
       "debugLog": "abc12345-...txt",
       "logPath": "~/.claude/debug/abc12345-...txt"
     },
     "component": {
       "plugin": "ws",
       "area": "cap",
       "type": "command",
       "name": "/ws:version"
     },
     "problem": {
       "description": "User's description of what went wrong",
       "expected": "What user expected to happen",
       "actual": "What actually happened"
     },
     "recentActions": [
       "2025-12-02T15:30:00Z executePreToolHooks called for tool: Read",
       "2025-12-02T15:30:01Z Hook output received..."
     ],
     "status": "open"
   }
   ```

6. **Display Confirmation**:
   ```
   ## Fault Report Created

   ID: ws-fault-20251202-153045
   Component: /ws:version (command)
   Area: cap (Capabilities)

   Session: abc12345-...
   Debug log: abc12345-...txt

   Problem: [User description]

   Report saved to: ~/.claude/fault/ws-fault-20251202-153045.json

   To debug later:
   - Review debug log: ~/.claude/debug/abc12345-...txt
   - Use /debug-plugin command with this report
   ```
</process>

<questions>
If problem description doesn't clearly identify the component, ask:

1. **Which area?** (cap, out, des, pln, exe)
2. **What type?** (command, skill, subagent, hook)
3. **What name?** (e.g., /ws:version)
4. **What did you expect?** (optional but helpful)
</questions>

<success_criteria>
- Problem description captured
- Session ID recorded
- Debug log path saved
- Component identified
- Recent actions captured
- Report saved to ~/.claude/fault/
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
@id: fault/ws-fault-20251202-153045
name: ws-fault-report
reportNumber: ws-fault-20251202-153045
dateCreated: 2025-12-02T15:30:45Z
actionStatus: CompletedActionStatus

session{id,debugLog}:
abc12345-...,abc12345-...txt

component{plugin,area,type,name|tab}:
ws	cap	command	/ws:version

x-problem: Command ran step-by-step instead of displaying cached content instantly
x-recentActionsCount: 5
x-reportPath: ~/.claude/fault/ws-fault-20251202-153045.json
```
</output_format>
