---
name: interact/stop
description: Stop the interactive Flutter session and generate session notes file
argument-hint: [--discard]
---

<objective>
Stop the current interactive Flutter session and generate the session notes file.

**Outputs by session mode:**
- Debug session: `plan/sess-debug-MM-DD-HH-mm.md` - Issues with diagnostics and suggested fixes
- Dev session: `plan/sess-dev-MM-DD-HH-mm.md` - Requests and file changes

Use `--discard` ($ARGUMENTS contains "discard") to stop without generating the report.
</objective>

<context>
Current time: !`date "+%m-%d-%H-%M"`
Plan directory: !`ls -la plan/ 2>/dev/null | head -10 || echo "plan/ not found"`
</context>

<stop_protocol>
## Stopping the Session

**1. Stop the Flutter app:**
```
KillShell <shell_id>
```

**2. Check for discard flag:**
If $ARGUMENTS contains "discard":
- Acknowledge session discarded
- Do not generate report
- Exit

**3. Generate session report:**
Based on session mode, create the appropriate file.
</stop_protocol>

<debug_session_report>
## Debug Session Report Format

**Filename:** `plan/sess-debug-{MM-DD-HH-mm}.md`

```markdown
# Debug Session Report

**Session ID:** sess-debug-{timestamp}
**Started:** {ISO timestamp}
**Ended:** {ISO timestamp}
**Device:** {device_id}
**Duration:** {calculated}

## Summary

- **Total Issues:** {count}
- **Defects:** {count}
- **Enhancements:** {count}
- **Missing Features:** {count}

---

## Issues

### Issue 1: {brief title}

**Classification:** Defect | Enhancement | Missing

**Location:**
- Screen: {screen name or "Not specified"}
- Area: {area or "Not specified"}
- Widget: {widget or "Not specified"}

**User Description:**
> {exact user words}

**Diagnostic Analysis:**

| Aspect | Finding |
|--------|---------|
| Probable Cause | {analysis} |
| File Path | `{path/to/file.dart:line}` |
| Related Files | `{other files}` |

**Diagnostic Confidence:** {0-100}%

**Suggested Fix:**
```dart
// Location: {file:line}
// Change: {description}
- {old code}
+ {new code}
```

**Fix Confidence:** {0-100}%

**Verification Steps:**
1. {step to verify the fix works}
2. {additional verification}

---

### Issue 2: ...

(repeat for each issue)

---

## Session Context

**Screens Visited:**
- {list of screens mentioned}

**Runtime Errors Observed:**
```
{any errors from get_runtime_errors during session}
```

**Widget Tree Snapshots:**
{relevant widget tree excerpts if captured}

---

## For Implementing Agent

This report is optimized for consumption by Claude Code agents.

**To fix all issues:**
```
Task(impl-flutter:flutter-coder)
Fix all issues in plan/sess-debug-{timestamp}.md
Verify each fix with hot_reload and get_runtime_errors.
```

**To verify fixes:**
```
Task(impl-flutter:flutter-tester)
Write tests for issues documented in plan/sess-debug-{timestamp}.md
```
```
</debug_session_report>

<dev_session_report>
## Development Session Report Format

**Filename:** `plan/sess-dev-{MM-DD-HH-mm}.md`

```markdown
# Development Session Report

**Session ID:** sess-dev-{timestamp}
**Started:** {ISO timestamp}
**Ended:** {ISO timestamp}
**Device:** {device_id}
**Duration:** {calculated}

## Summary

- **Total Requests:** {count}
- **Completed:** {count}
- **Partial:** {count}
- **Failed:** {count}

---

## Changes Log

### Change 1: {brief title}

**User Request:**
> {exact user words}

**Implementation:**

| Aspect | Detail |
|--------|--------|
| Files Changed | `{file1.dart}`, `{file2.dart}` |
| Files Created | `{new_file.dart}` (if any) |
| Status | Completed | Partial | Failed |

**Changes Made:**

**{file1.dart}:**
```dart
// Lines {start}-{end}
{summary of changes or diff}
```

**{file2.dart}:**
```dart
{summary of changes}
```

**Hot Reload Result:** Success | Failed (required restart)

**Verification Notes:**
{any observations about the implementation}

---

### Change 2: ...

(repeat for each change)

---

## Files Modified This Session

| File | Changes | Status |
|------|---------|--------|
| `lib/screens/login.dart` | Added validation | Completed |
| `lib/widgets/button.dart` | Style updates | Completed |
| ... | ... | ... |

## New Files Created

| File | Purpose |
|------|---------|
| `lib/utils/validator.dart` | Form validation helpers |
| ... | ... |

---

## For Verification Agent

This report is optimized for verification by Claude Code agents.

**To verify all changes:**
```
Task(impl-flutter:flutter-tester)
Verify implementations in plan/sess-dev-{timestamp}.md
Write tests for each change if not already tested.
```

**To review code quality:**
```
dart_analyzer
dart_format
```
```
</dev_session_report>

<report_generation>
## Generating the Report

**1. Determine session mode from session state**

**2. For Debug Sessions - Delegate to Recorder:**
```
Task(impl-flutter:flutter-session-recorder)

Generate final debug session report.
Session data:
- Session ID: {session_id}
- Started: {started_at}
- Device: {device_id}
- Issues: {JSON array of all recorded issues}

Output format: Markdown following the debug session report template.
Include diagnostic confidence and fix confidence for each issue.
```

**3. For Dev Sessions - Compile from session state:**
Aggregate all changes from session state into the dev report format.

**4. Write the file:**
```
Write to: plan/{session_id}.md
```

**5. Confirm to user:**
```
Session ended. Report saved to: plan/{session_id}.md

Summary:
- {issue/change count}
- {key findings or completions}

To implement fixes: Task(impl-flutter:flutter-coder) with the report
To verify: Task(impl-flutter:flutter-tester) with the report
```
</report_generation>

<process>
1. Retrieve session state (session_id, mode, issues/changes, timestamps)
2. Kill the Flutter app background shell
3. Check for --discard flag
   - If discarding: acknowledge and exit
4. Calculate session duration
5. If debug mode:
   - Delegate final report generation to session-recorder
   - Write debug report to plan/
6. If dev mode:
   - Compile changes from session state
   - Write dev report to plan/
7. Confirm report location and summary to user
8. Provide next-step commands for implementation/verification
</process>

<success_criteria>
- Flutter app process terminated cleanly
- Session report file created in plan/ directory
- Report contains all recorded issues/changes
- Debug reports include diagnostic and fix confidence scores
- Dev reports include all file changes with status
- Report formatted for consumption by other agents
- User informed of report location and next steps
</success_criteria>

<constraints>
## Hard Rules

- ALWAYS kill the app process before generating report
- NEVER lose recorded issues/changes
- ALWAYS include confidence scores in debug reports
- ALWAYS include file paths in reports for agent consumption
- Delegate report generation for debug sessions to recorder agent
- Keep reports structured for machine parsing
</constraints>
