---
description: Interactive Flutter development session with hot reload and live debugging
argument-hint: [device-id]
---

<objective>
Start and manage an interactive Flutter development session on device $ARGUMENTS.

This command orchestrates:
- App lifecycle (start, monitor, restart)
- Hot reload cycles for rapid iteration
- Routing user feedback to specialist agents
- DTD (Dart Tooling Daemon) connection management

The goal is efficient development with minimal context consumption through immediate delegation.
</objective>

<session_bootstrap>
## Starting the Session

**1. List available devices (if no device specified):**
```bash
flutter devices
```

**2. Start app in background:**
```bash
# Use project's run script if available
./scripts/run.sh -d $ARGUMENTS 2>&1
# OR standard flutter run
flutter run -d $ARGUMENTS --debug
```
Run with `run_in_background: true`. Capture the shell ID for later management.

**3. Wait for startup indicators:**
Check output for:
- "Syncing files to device"
- "Flutter run key commands"

**4. Capture VM Service URL:**
Extract from output: `A Dart VM Service is available at: http://127.0.0.1:xxxxx/yyy=/`
Convert to WebSocket: `ws://127.0.0.1:xxxxx/yyy=/ws`

**5. Test DTD connection:**
```
get_runtime_errors
```
If this fails, app not ready or SDK version mismatch (use restart workflow instead).
</session_bootstrap>

<session_state>
## Track These Values

Maintain throughout session:
- **Device:** $ARGUMENTS
- **Shell ID:** (from background command)
- **VM URL:** (changes on each restart)
- **Last Action:** (for context recovery)

Update VM URL after every app restart - it changes each time.
</session_state>

<feedback_loop>
## Processing User Feedback

When user reports an observation:

### Step 1: Quick Log Check (Main Context)
One brief command only:
```bash
grep -E "Error|Exception|WARNING" /tmp/claude/tasks/<shell_id>.output | tail -10
```

### Step 2: Classify the Request
| Type | Indicators |
|------|------------|
| UX/UI | visual, layout, animation, navigation, theme, color, text, autofill |
| Bug/Error | crash, hang, spin, wrong behavior, doesn't work |
| Data | not saving, not loading, sync, offline, Firestore |
| Performance | slow, jank, frame drops, memory |
| Platform | native, iOS-specific, Android-specific, permissions |

### Step 3: Delegate Immediately
Route to specialist agent. Do NOT read implementation files in main context.

| Classification | Agent | Prompt Template |
|---------------|-------|-----------------|
| UX/UI | `impl-flutter:flutter-ux` | "User on [screen]. Observes: [issue]. Check [suspected file] for [likely cause]. Return specific changes." |
| Runtime Error | `impl-flutter:flutter-debugger` | "User reports: [issue]. VM URL: [url]. Check logs and runtime state. Diagnose and fix." |
| Data Issue | `impl-flutter:flutter-data` | "User reports: [data issue]. Check the [operation] flow in [area]. Return fix." |
| New Feature | `impl-flutter:flutter-coder` | "Implement: [feature]. Follow project patterns. Return implementation." |
| Test Needed | `impl-flutter:flutter-tester` | "Write test for: [behavior]. Cover [scenarios]." |
| Build/Env | `impl-flutter:flutter-env` | "App won't [issue]. Check environment and fix." |

### Step 4: Apply Changes
After agent returns:
- If DTD connected: `hot_reload`
- If hot_reload fails: restart app (see restart protocol)
- If structural change: restart app

### Step 5: Confirm
Tell user: "Changes applied. Please test [specific action]."
</feedback_loop>

<hot_reload_protocol>
## Hot Reload Strategy

**Works for:**
- Widget build() changes
- Method body changes
- Property value changes

**Requires restart:**
- Static field initializers
- main() function
- New dependencies
- Enum additions
- Hot reload rejection

**Command:**
```
hot_reload
```
If DTD not connected or fails, use restart protocol.
</hot_reload_protocol>

<restart_protocol>
## App Restart Protocol

When hot reload fails or app crashes:

1. **Kill background shell:**
   ```
   KillShell <shell_id>
   ```

2. **Restart app:**
   Same command as bootstrap with `run_in_background: true`

3. **Wait for startup:**
   Check for "Flutter run key commands"

4. **Recapture VM URL:**
   Extract new URL from output (it changes every restart)

5. **Reconnect DTD:**
   ```
   connect_dart_tooling_daemon uri=<new_ws_url>
   ```

6. **Verify:**
   ```
   get_runtime_errors
   ```
</restart_protocol>

<delegation_rules>
## Context Preservation Rules

### Always Delegate (Never in Main Context)
- File reads for understanding code
- Multi-line edits
- Investigation work
- Any change requiring code analysis

### Keep in Main Context
- App lifecycle (start/stop/restart)
- Brief log checks (`grep | tail -10`)
- User communication
- Hot reload commands
- DTD connection management

### Prompt Construction for Agents
Include in every delegation:
1. What user observed (their words)
2. Brief log context (if relevant errors found)
3. VM Service URL (for runtime debugging)
4. Suspected file/area (if known)
5. Expected deliverable ("Return the specific changes made")
</delegation_rules>

<process>
1. **Bootstrap**: Start app on $ARGUMENTS, capture shell ID and VM URL
2. **Connect**: Establish DTD connection for hot reload capability
3. **Loop**:
   - Receive user feedback
   - Quick log check (main context)
   - Delegate to specialist agent
   - Apply result via hot_reload or restart
   - Confirm with user what to test
4. **Recover**: On app crash, restart and recapture VM URL
5. **Checkpoint**: After 5+ cycles, briefly summarize session state
</process>

<success_criteria>
- App running on target device
- Hot reload working (or restart protocol functional)
- User feedback processed within 1-2 interactions
- No implementation files read in main context
- Specialist agents handle all code changes
- Session can continue through multiple feedback cycles
</success_criteria>

<constraints>
## Hard Rules

- NEVER read implementation files in main context
- NEVER make edits in main context
- ALWAYS delegate to most specific agent
- ALWAYS update VM URL after restart
- ALWAYS tell user what to test after changes
- Keep log checks to `tail -10` or `grep | tail -10`
- If context feels heavy, delegate more aggressively
</constraints>
