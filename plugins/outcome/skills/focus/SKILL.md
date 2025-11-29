---
name: focus
description: Execute the focus transition workflow - move outcome to in-progress, update all tracking files, load context, present ready message. Invoked by /focus command after selection.
---

<objective>
Execute the focus transition workflow for a pre-validated outcome. This skill is invoked by the `/focus` command after it has:
1. Validated the outcome exists in queued state
2. Defocused any currently focused outcomes
3. Checked dependencies

The skill owns the TRANSITION logic:
- State change (queued → in-progress)
- Directory move
- Cross-reference updates
- Session registration
- Context loading
- Ready message
</objective>

<input_expected>
When invoked, expect these parameters from the command:
- **Selected outcome**: directory label (e.g., `001-jwt-authentication`)
- **Outcome ID**: numeric ID (e.g., `1`)
- **Session ID**: current session UUID
</input_expected>

<transition_workflow>

<phase name="state-transition">
## Phase 1: State Transition

1. **Update outcome_track.json**
   ```bash
   # Location: outcomes/<current-state>/<directory-label>/outcome_track.json
   # Current state may be: queued, ready, or blocked (not completed)
   ```

   Update fields:
   ```json
   {
     "outcome": {
       "state": "in-progress",
       "updatedAt": "<current-ISO-timestamp>"
     }
   }
   ```

2. **Move outcome directory**
   ```bash
   # From queued, ready, or blocked → in-progress
   mv outcomes/<current-state>/<directory-label>/ outcomes/in-progress/<directory-label>/
   ```
</phase>

<phase name="capability-updates">
## Phase 2: Capability Cross-Reference Updates

3. **For each capability in capabilityContributions:**

   Read the outcome's `capabilityContributions` array to get capability paths.

   For each capability:
   - Read `capabilities/<capability-id>/capability_track.json`
   - Find entry in `outcomes.requiredOutcomes[]` where `outcomeTrackingFile` matches old path
   - Update `outcomeTrackingFile`:
     - Old: `outcomes/queued/<label>/outcome_track.json`
     - New: `outcomes/in-progress/<label>/outcome_track.json`
   - Write updated capability_track.json
</phase>

<phase name="session-registration">
## Phase 3: Session Registration

4. **Update sessions_summary.json**

   Read `status/sessions_summary.json` and update:

   ```json
   {
     "summary": {
       "currentFocusedOutcome": "<outcome-directory-label>",
       "lastUpdated": "<current-timestamp>"
     },
     "activeSessions": [
       {
         "sessionId": "<current-session>",
         "focusedOutcomes": [{
           "outcomeId": <outcome-numeric-id>,
           "outcomeName": "<outcome-name>",
           "trackingFile": "outcomes/in-progress/<label>/outcome_track.json",
           "focusedAt": "<current-timestamp>"
         }],
         "lastActivityAt": "<current-timestamp>"
       }
     ]
   }
   ```

   Also update `indexByOutcome`:
   ```json
   {
     "indexByOutcome": {
       "<outcome-id>": ["<session-id>"]
     }
   }
   ```
</phase>

<phase name="summary-updates">
## Phase 4: Outcome Summary Updates

5. **Update outcome_summary.json**

   Read `status/outcome_summary.json` and update:

   - Find outcome in `outcomes[]` array by id
   - Update fields:
     ```json
     {
       "state": "in-progress",
       "trackingFile": "outcomes/in-progress/<label>/outcome_track.json",
       "updatedAt": "<current-timestamp>"
     }
     ```

   - Update `indexByState`:
     - Remove outcome id from source state array (`queued[]`, `ready[]`, or `blocked[]`)
     - Add outcome id to `in-progress[]` array

   - Update `summary`:
     ```json
     {
       "outcomesByState": {
         "<source-state>": <decrement>,
         "in-progress": <increment>
       },
       "lastUpdated": "<current-timestamp>"
     }
     ```
</phase>

<phase name="transition-logging">
## Phase 5: Transition Logging

6. **Update outcome-statement.md**

   Location: `outcomes/in-progress/<label>/outcome-statement.md`

   Find or create "State Transition Log" section. If it doesn't exist, append:
   ```markdown
   ---

   ## State Transition Log

   | Date | From | To | Session | Notes |
   |------|------|-----|---------|-------|
   ```

   Add new row:
   ```markdown
   | <YYYY-MM-DD HH:MM> | <source-state> | in-progress | <session-id-short> | Focus initiated |
   ```

   Use short session ID (first 8 characters) for readability.
   Source state can be: queued, ready, or blocked.
</phase>

<phase name="context-loading">
## Phase 6: Context Loading

7. **Clear current context**

   Signal that context should be cleared to start fresh.

8. **Load outcome context files**

   Read and present:
   - `outcomes/in-progress/<label>/outcome-statement.md` (primary)

   Identify additional context from outcome_track.json:
   - Task files if `tasks[]` array has entries
   - Files in `tasks[].context[]` arrays
</phase>

<phase name="ready-message">
## Phase 7: Ready Message

9. **Present work-ready message**

   Format:
   ```
   Ready to start work on: [outcome.name - title cased]

   Outcome: [directoryLabel]
   Description: [outcome.description]
   Token Budget: [outcome.estimatedTokens] tokens

   Projects:
   - [primary project.projectName] (primary) - [affectedAreas]
   [- secondary/integration projects if any]

   Observable Effects to Achieve:
   1. [First observableEffect.effect - truncated to 100 chars]
   2. [Second observableEffect.effect - truncated]
   [... up to 4 effects shown]

   Tasks: [tasks.length] defined
   [or: "No tasks defined yet - describe what to implement"]

   Primary Capability: [primary capabilityId] (+[maturityContribution]% on completion)

   Session [session-id-short] now focused on this outcome.

   What would you like to work on first?
   ```
</phase>

</transition_workflow>

<files_modified>
| File | Updates |
|------|---------|
| `outcomes/in-progress/<label>/outcome_track.json` | state, updatedAt |
| `outcomes/in-progress/<label>/outcome-statement.md` | Transition log entry |
| `capabilities/<id>/capability_track.json` | requiredOutcomes path (for each linked capability) |
| `status/sessions_summary.json` | currentFocusedOutcome, session.focusedOutcomes (array of objects), indexByOutcome |
| `status/outcome_summary.json` | state, trackingFile, indexByState, summary counts |
</files_modified>

<validation_checklist>
After transition, verify:
- [ ] outcome_track.json has `state: "in-progress"`
- [ ] Directory exists at `outcomes/in-progress/<label>/`
- [ ] Directory no longer exists at `outcomes/queued/<label>/`
- [ ] All capability_track.json files have updated paths
- [ ] sessions_summary.json has `currentFocusedOutcome` set to outcome directory label
- [ ] Current session has outcome object in `focusedOutcomes` array
- [ ] outcome_summary.json has correct state and path
- [ ] indexByState arrays are correct
- [ ] Transition logged in outcome-statement.md
</validation_checklist>

<error_recovery>
If any step fails:

**Directory move failed:**
- Check permissions on outcomes directories
- Verify source directory exists
- Do not proceed with other updates

**JSON update failed:**
- Log which file failed
- Attempt to rollback any partial changes
- Report specific error to user

**Capability update failed:**
- Log which capability couldn't be updated
- Continue with other capabilities
- Report incomplete update at end
</error_recovery>

<success_criteria>
Skill execution complete when:
- All 5 tracking files updated correctly
- Directory successfully moved
- Context cleared and loaded
- Ready message displayed
- User can immediately begin work on the outcome
</success_criteria>

<output_format>
## TOON Return Format (Subagent Usage)

When this skill is invoked as a subagent, return in TOON format:

**Success:**
```toon
@type: Action
actionStatus: CompletedActionStatus
name: focus
object: 005-authentication
result: outcomes/2-in-progress/005-authentication
```

**Failure (blocked outcome):**
```toon
@type: Action
actionStatus: FailedActionStatus
name: focus
object: 005-authentication
error: Outcome is blocked, cannot focus
```

**Fields:**
- `@type`: Action (general operation)
- `actionStatus`: CompletedActionStatus or FailedActionStatus
- `name`: focus
- `object`: outcome directory label
- `result`: Path to the focused outcome directory (success only)
- `error`: Error message (failure only)

**Usage by calling command:**
The `/outcome:focus` command delegates file operations to this skill and expects this TOON return format. The command parses the `result` field to load outcome_track.json into main context.
</output_format>