---
description: Remove focus from current outcome(s) without changing their state - they remain in-progress
allowed-tools: Bash, Read
---

<objective>
Defocus all currently focused outcomes for this session. Outcomes remain in-progress but are no longer actively tracked. This is the inverse of `/outcome:focus`.
</objective>

<context>
Session: !`jq -r '.activeSessions | sort_by(.startedAt) | last | .sessionId' status/sessions_summary.json 2>/dev/null`
Focused: !`jq -r '.activeSessions | sort_by(.startedAt) | last | .focusedOutcomes | if length > 0 then join(", ") else "none" end' status/sessions_summary.json 2>/dev/null`
</context>

<process>

1. **Check if any outcomes are focused**:
   - If `focusedOutcomes` array is empty, report "No outcomes currently focused" and exit

2. **Capture focused outcomes** for reporting:
   ```bash
   jq -r '.activeSessions | sort_by(.startedAt) | last | .focusedOutcomes[]' status/sessions_summary.json
   ```

3. **Update sessions_summary.json** using jq:
   ```bash
   SESSION_ID="<session-id-from-context>"
   TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

   jq --arg sid "$SESSION_ID" --arg ts "$TIMESTAMP" '
     (.activeSessions[] | select(.sessionId == $sid)) |= (
       .focusedOutcomes = [] |
       .lastActivityAt = $ts
     ) |
     .summary.currentFocusedOutcome = "No Focus Set" |
     .summary.lastUpdated = $ts
   ' status/sessions_summary.json > status/sessions_summary.json.tmp && \
   mv status/sessions_summary.json.tmp status/sessions_summary.json
   ```

4. **Report success** with the list of defocused outcomes

</process>

<success_criteria>
- `focusedOutcomes` array is empty for the active session
- `summary.currentFocusedOutcome` is set to "No Focus Set"
- Timestamps are updated
- User is informed which outcomes were defocused
</success_criteria>

<output_format>
On success:
```
Defocused outcomes: [list of outcome labels]

These outcomes remain in-progress and can be resumed with:
  /outcome:focus <outcome-label>
```

If no focus:
```
No outcomes currently focused for this session.
```
</output_format>