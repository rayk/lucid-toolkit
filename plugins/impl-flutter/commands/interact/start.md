---
name: interact/start
description: Start an interactive Flutter debug or development session with live issue tracking
argument-hint: <debug|dev> [device-id]
---

<objective>
Start an interactive Flutter session in $1 mode on device $2.

**Session Modes:**
- **debug**: Manual testing session - user walks the app, reports issues (defects, enhancements, missing features)
- **dev**: Development session - user requests features/fixes, agents implement with hot reload

This command bootstraps the app, establishes DTD connection, and activates the session recorder.
</objective>

<context>
Available devices: !`flutter devices --machine 2>/dev/null | head -20`
Project root: !`pwd`
Plan folder exists: !`test -d plan && echo "yes" || echo "no - will create"`
</context>

<session_initialization>
## Mode Detection

Parse $1 to determine session type:
- `debug` or `test` → Debug/testing session (issue tracking mode)
- `dev` or `develop` → Development session (implementation mode)

If $1 is empty or unrecognized, ask user:
```
Which session type?
- debug: Manual testing, issue tracking, generates diagnostic report
- dev: Feature development with live implementation
```

## Device Selection

If $2 is provided, use that device ID.
If not provided, list devices and ask user to select.
</session_initialization>

<bootstrap_protocol>
## Starting the Session

**1. Verify project is Flutter:**
```bash
test -f pubspec.yaml && grep -q "flutter:" pubspec.yaml && echo "Flutter project" || echo "Not a Flutter project"
```

**2. Ensure plan directory exists:**
```bash
mkdir -p plan
```

**3. Start Flutter app in background:**
```bash
flutter run -d $DEVICE_ID --debug
```
Run with `run_in_background: true`. Capture the shell ID.

**4. Wait for startup indicators:**
Monitor output for:
- "Syncing files to device"
- "Flutter run key commands"
- "A Dart VM Service is available at:"

**5. Extract VM Service URL:**
Parse: `A Dart VM Service is available at: http://127.0.0.1:xxxxx/yyy=/`
Convert to WebSocket: `ws://127.0.0.1:xxxxx/yyy=/ws`

**6. Verify DTD connection:**
```
get_runtime_errors
```
If fails, wait and retry (app may still be starting).
</bootstrap_protocol>

<session_state>
## Initialize Session State

Create and maintain throughout session:

```json
{
  "session_id": "sess-{mode}-MM-DD-HH-mm",
  "mode": "debug|dev",
  "device_id": "$DEVICE_ID",
  "shell_id": "(from background command)",
  "vm_url": "(from startup)",
  "started_at": "ISO timestamp",
  "issues": [],
  "changes": [],
  "current_screen": null
}
```

Store this mentally or use a temp file for persistence.
</session_state>

<debug_mode_behavior>
## Debug Session Behavior

When mode is `debug`:

**User Input Patterns to Recognize:**

| Pattern | Classification | Example |
|---------|---------------|---------|
| "screen: X, area: Y, widget: Z" | Location context | "screen: login, area: form, widget: password field" |
| "it should ... but currently ..." | Defect | "it should show error, but currently shows nothing" |
| "it would be better if ..." | Enhancement | "it would be better if the button was larger" |
| "it's missing ..." or "I can't see ..." | Defect (missing) | "I can't see the submit button" |
| "when I tap X, Y happens" | Behavior observation | "when I tap login, nothing happens" |

**For Each Issue Reported:**

1. **Capture Location Context:**
   - Screen name (if provided)
   - Area/section (if provided)
   - Widget/component (if provided)

2. **Delegate to Session Recorder:**
   ```
   Task(impl-flutter:flutter-session-recorder)

   Analyze this user-reported issue:
   - Location: [screen/area/widget]
   - Description: [user's exact words]
   - Session mode: debug
   - VM URL: [current VM URL]

   Return:
   1. Issue classification (defect/enhancement/missing)
   2. Diagnostic analysis with file paths
   3. Confidence score (0-100)
   4. Suggested fix with confidence score
   ```

3. **Record in Session State:**
   Add to `issues` array with diagnostic results.

4. **Acknowledge to User:**
   "Recorded: [brief summary]. Continue testing or say 'stop' to end session."
</debug_mode_behavior>

<dev_mode_behavior>
## Development Session Behavior

When mode is `dev`:

**User Input Patterns:**

| Pattern | Action |
|---------|--------|
| "add ...", "implement ...", "create ..." | New feature request |
| "fix ...", "change ...", "update ..." | Modification request |
| "remove ...", "delete ..." | Removal request |

**For Each Request:**

1. **Delegate to Coder:**
   ```
   Task(impl-flutter:flutter-coder)

   Implement: [user's request]
   Context:
   - Current screen: [if known]
   - VM URL: [for hot reload verification]

   Return:
   - Files changed/created
   - Summary of implementation
   - Any errors encountered
   ```

2. **Apply Hot Reload:**
   After coder returns, apply changes:
   ```
   hot_reload
   ```
   If hot reload fails, try `hot_restart`.

3. **Record in Session State:**
   Add to `changes` array:
   ```json
   {
     "request": "user's original request",
     "files": ["list of changed files"],
     "summary": "what was implemented",
     "timestamp": "ISO"
   }
   ```

4. **Confirm to User:**
   "Implemented: [summary]. Files: [list]. Please verify."
</dev_mode_behavior>

<restart_protocol>
## App Restart Protocol

When hot reload fails or app crashes:

1. **Kill background shell:**
   ```
   KillShell <shell_id>
   ```

2. **Restart app:**
   ```bash
   flutter run -d $DEVICE_ID --debug
   ```
   With `run_in_background: true`

3. **Wait for startup** (check for "Flutter run key commands")

4. **Recapture VM URL** (it changes every restart)

5. **Update session state** with new shell_id and vm_url

6. **Notify user:**
   "App restarted. New VM URL captured. Ready to continue."
</restart_protocol>

<process>
1. Parse arguments: mode = $1, device = $2
2. If mode missing, ask user to choose debug or dev
3. If device missing, list devices and ask user to select
4. Verify Flutter project (pubspec.yaml exists)
5. Create plan/ directory if needed
6. Start app in background, capture shell ID
7. Wait for VM Service URL, extract and convert to WebSocket
8. Verify DTD connection with get_runtime_errors
9. Initialize session state with session_id based on mode and timestamp
10. Announce session started with mode-specific instructions
11. Enter feedback loop:
    - Debug mode: Record issues, delegate diagnostics to recorder
    - Dev mode: Delegate implementations to coder, apply hot reload
12. On "stop" or "/interact/stop", trigger session end
</process>

<user_instructions>
## After Session Starts

**For Debug Sessions:**
```
Session started in DEBUG mode.

Report issues using natural language:
- Location: "screen: [name], area: [section], widget: [component]"
- Defects: "it should [expected] but currently [actual]"
- Enhancements: "it would be better if [suggestion]"
- Missing: "I can't see [expected element]"

Say "stop" or use /interact/stop to end and generate report.
```

**For Dev Sessions:**
```
Session started in DEV mode.

Request changes using natural language:
- "add a logout button to the profile screen"
- "fix the login form validation"
- "change the primary color to blue"

Changes are applied via hot reload. Say "stop" to end session.
```
</user_instructions>

<success_criteria>
- Flutter app running on specified device
- DTD connection verified (get_runtime_errors succeeds)
- Session state initialized with correct mode
- User informed of mode-specific input patterns
- Ready to receive and process user feedback
- Issues/changes being recorded in session state
</success_criteria>

<constraints>
## Hard Rules

- NEVER read implementation files in main context - always delegate
- ALWAYS capture VM URL changes after restarts
- ALWAYS confirm issue recording to user
- ALWAYS apply hot_reload after dev changes
- Keep main context lean - delegate analysis work
- If context feels heavy, delegate more aggressively
</constraints>
