---
description: Complete an in-progress outcome - moves to completed, updates capability maturity
argument-hint: <outcome-id or directory-label>
allowed-tools: Bash
---

<objective>
Complete outcome `$ARGUMENTS` by executing the optimized shell script. This:
- Validates completion requirements (all effects verified, children state=success if parent)
- Moves outcome from 2-in-progress to 4-completed
- For parent outcomes: moves entire nested tree together
- Updates capability maturity based on contribution (ONLY for parents/standalone outcomes)
- Removes from focused outcomes
- Logs completion in transition history

**Parent-Child Contribution Model:**
- Child outcomes: Update parent's childStates[child]=success, do NOT update capability maturity
- Parent outcomes: Verify all childStates are "success", THEN apply capabilityContributions to capability
- Standalone atomic outcomes: Apply capabilityContributions to capability directly
</objective>

<context>
2-In-Progress: !`ls outcomes/2-in-progress/ 2>/dev/null | grep -E "^[0-9]+-" | tr '\n' ' ' || echo "none"`
Session: !`jq -r '.activeSessions | sort_by(.startedAt) | last | .sessionId' status/sessions_summary.json 2>/dev/null`
</context>

<process>

1. **Resolve outcome label** from `$ARGUMENTS`:
   ```bash
   # If numeric, find matching directory
   ls outcomes/2-in-progress/ | grep -E "^0*${ARGUMENTS}-" | head -1
   ```

2. **Validate completion requirements**:
   - Check all observable effects have verified=true
   - If parent outcome: check all children have state=success in childStates
   - Warn if requirements not met, require user confirmation to proceed

3. **Execute complete script**:
   ```bash
   ./scripts/complete-outcome.sh "<resolved-label>" "<session-id>"
   ```
   Script will:
   - Move from outcomes/2-in-progress/ to outcomes/4-completed/
   - For parent outcomes: move entire nested tree
   - Update capability maturity
   - Update cross-references

4. **Parse output** and present completion summary:
   - If `COMPLETE_SUCCESS`: Show outcome completed, new capability maturity
   - If error: Report the issue

</process>

<output_format>
## Standard Output (Human-Readable)

On success:
```
Outcome Completed: [outcome_name]

Label: [outcome_label]
Capability: [primary_capability]
Maturity: [old]% → [new]% (+[contribution]%)

Moved to: outcomes/4-completed/[label]/
```

## TOON Format (Machine-Readable)

For subagent returns and structured data exchange:

```toon
@type: UpdateAction
actionStatus: CompletedActionStatus
@id: 005-authentication
result: Outcome completed, capability maturity updated

transition:
fromStatus: ActiveActionStatus
toStatus: CompletedActionStatus

maturityUpdate{capability,from,to,delta}:
authentication-system,45,55,+10
```

**Fields:**
- `@type`: UpdateAction (state transition)
- `actionStatus`: CompletedActionStatus
- `@id`: outcome directory label
- `result`: Summary message
- `transition`: Single state change (fromStatus, toStatus)
- `maturityUpdate`: Single-row tabular with capability, from, to, delta
</output_format>

<warnings>
- Ensure all observable effects have been verified before completing
- For parent outcomes: ALL children must have state=success before parent can complete
- Check that any required approvals (e.g., security-team) are obtained
- Completion cannot be easily undone (though can be reopened via /outcome:move if needed)
</warnings>

<child_completion_behavior>
When completing a **child outcome** (has parentOutcome set):
1. Update parent's childStates to mark this child as "success"
2. Do NOT update capability maturity (children have capabilityContributions: [])
3. Do NOT add child to capability's builtByOutcomes
4. Parent progress can be calculated: sum of completed children's parentContribution values

When completing a **parent outcome** (has children array):
1. Verify ALL childStates are "success" (reject completion otherwise)
2. Apply parent's capabilityContributions to capability maturity
3. Parent path is already in capability's builtByOutcomes (was added at creation)

When completing a **standalone atomic outcome** (no parent, no children):
1. Apply capabilityContributions to capability maturity
2. Path should already be in capability's builtByOutcomes
</child_completion_behavior>