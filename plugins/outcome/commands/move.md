---
description: Move one or more outcomes between states (queued, ready, in-progress, blocked, completed) with full cross-reference updates
argument-hint: <outcome-ids...> [--to <target-state>]
---

<objective>
Move outcomes specified in $ARGUMENTS between classification directories with complete cross-reference integrity.

Classification transitions: `0-queued` → `1-ready` → `2-in-progress` ⇄ `3-blocked` → `4-completed` (or reverse for corrections)

**Parent-child outcomes move as a unit** - the entire tree moves to the same classification directory.

This command handles the CRITICAL cross-reference updates that maintain workspace integrity:
- Updates outcome_track.json state and timestamps
- Moves outcome directory to new classification folder (0-queued, 1-ready, etc.)
- For parent outcomes: moves entire nested tree together
- Updates ALL capability paths in capability_track.json files
- Updates outcome_summary.json paths and indexes
- Updates capability_summary.json indexByOutcome
- Records transition in outcome-statement.md
- For completed outcomes: updates capability maturity calculations
- Validates classification transition rules before moving
</objective>

<context>
Schemas:
- Outcome track: @schemas/outcome_track_schema.json
- Outcome summary: @schemas/outcome_summary_schema.json
- Capability track: @schemas/capability_track_schema.json
- Capability summary: @schemas/capability_summary_schema.json

Current outcomes by classification:
- 0-Queued: !`ls outcomes/0-queued/ 2>/dev/null | grep -E "^[0-9]+-" | tr '\n' ' '`
- 1-Ready: !`ls outcomes/1-ready/ 2>/dev/null | grep -E "^[0-9]+-" | tr '\n' ' '`
- 2-In-Progress: !`ls outcomes/2-in-progress/ 2>/dev/null | grep -E "^[0-9]+-" | tr '\n' ' '`
- 3-Blocked: !`ls outcomes/3-blocked/ 2>/dev/null | grep -E "^[0-9]+-" | tr '\n' ' '`
- 4-Completed: !`ls outcomes/4-completed/ 2>/dev/null | grep -E "^[0-9]+-" | tr '\n' ' '`

Outcome summary: @status/outcome_summary.json
Capability summary: @status/capability_summary.json
</context>

<process>
## Phase 1: Parse and Validate Input

1. **Parse $ARGUMENTS**
   - Extract outcome identifiers (directory labels like `001-jwt-authentication`)
   - Support multiple outcomes: `001-jwt-auth 002-session-mgmt`
   - Extract target state if provided with `--to`: `queued`, `ready`, `in-progress`, `blocked`, or `completed`
   - If no `--to` specified, infer next logical state (queued→ready→in-progress→completed)

2. **Locate each outcome**
   - Search across all classification directories: outcomes/0-queued/, outcomes/1-ready/, outcomes/2-in-progress/, outcomes/3-blocked/, outcomes/4-completed/
   - Record current classification and full path for each outcome
   - If outcome is a parent, identify all nested children
   - Error if any outcome not found

3. **Validate classification transitions**
   - Map target state to classification directory (queued→0-queued, ready→1-ready, etc.)
   - Apply classification transition rules:
     - 0-queued → 1-ready: Requires design AND all dependencies in 4-completed AND (if parent) all children have designs
     - 1-ready → 2-in-progress: Allowed (triggered by /outcome:focus)
     - 2-in-progress → 3-blocked: Requires blocker information
     - 3-blocked → 2-in-progress: Requires blocker resolution
     - 2-in-progress → 4-completed: Requires all effects verified AND (if parent) all children state=success
   - For parent outcomes: entire tree moves together
   - Parent blocked → cascade block to all children
   - Warn if moving to non-adjacent state - require confirmation

## Phase 2: Pre-Move Checks

4. **For each outcome, verify readiness**

   **Moving to `ready`**:
   - Check outcomeDependencies are all completed
   - Outcome can be started when convenient

   **Moving to `in-progress`**:
   - Best practice: move from `ready` state (dependencies satisfied)
   - If from `queued`: Warn if dependencies are not met (ask user to confirm override)

   **Moving to `blocked`**:
   - Require blocker information (type, description, resolutionPath)
   - Record blockedAt timestamp and blockedBy

   **Moving from `blocked`**:
   - Move blocker to blockerHistory with resolution
   - Set blocker to null

   **Moving to `completed`**:
   - Check all observableEffects have `verified: true` OR ask user to confirm
   - Check all tasks have `state: success` OR warn about incomplete tasks
   - Prompt for work summary/notes to record

5. **Read required files for each outcome**
   - outcome_track.json
   - List of capabilityContributions (capability paths to update)

## Phase 3: Execute Move (Per Outcome)

6. **Update outcome_track.json**
   ```json
   {
     "outcome": {
       "state": "<new-state>",
       "updatedAt": "<current-timestamp>",
       "completedAt": "<timestamp-if-completed, null-otherwise>"
     }
   }
   ```

7. **Move outcome directory**
   ```
   outcomes/<old-classification>/<directory-label>/
   → outcomes/<new-classification>/<directory-label>/
   ```
   For parent outcomes with nested children:
   ```
   outcomes/0-queued/010-parent-name/
   ├── 010.1-child-one/
   ├── 010.2-child-two/
   └── 010.3-child-three/
   → outcomes/1-ready/010-parent-name/
      ├── 010.1-child-one/
      ├── 010.2-child-two/
      └── 010.3-child-three/
   ```
   Entire tree moves as a unit.

8. **Update capability references**
   For each capability in capabilityContributions:
   - Read capability_track.json
   - Update path in `requiredOutcomes[]` from old path to new path
   - If moving to completed:
     - Remove from `requiredOutcomes[]`
     - Add to `builtByOutcomes[]` with completedDate
     - Recalculate `currentMaturity` = sum of builtByOutcomes[].contributionPercent
   - If moving FROM completed (reopening):
     - Remove from `builtByOutcomes[]`
     - Add back to `requiredOutcomes[]`
     - Recalculate `currentMaturity`
   - Write updated capability_track.json

9. **Update outcome_summary.json**
   - Update `outcomes[]` entry:
     - `state`: new state
     - `trackingFile`: new path
     - `updatedAt`: current timestamp
     - `completedAt`: timestamp if completed, null otherwise
   - Update `indexByState`:
     - Remove outcome ID from old state array
     - Add outcome ID to new state array
   - Recalculate `summary.outcomesByState` counts
   - Update `summary.lastUpdated`

10. **Update capability_summary.json**
    - Update `indexByOutcome` with new outcome path
    - Update `lastUpdated` timestamp

11. **Update outcome-statement.md**
    Add transition record section:
    ```markdown
    ---
    ## State Transition Log

    | Date | From | To | Notes |
    |------|------|-----|-------|
    | <timestamp> | <old-state> | <new-state> | <user-provided-notes> |
    ```

## Phase 4: Validation

12. **Validate all modified files**
    - Verify outcome_track.json against schema
    - Verify capability_track.json files against schema
    - Verify outcome_summary.json against schema
    - Verify capability_summary.json against schema

13. **Report results**
    - Summary of outcomes moved
    - New state for each
    - Capability maturity changes (if any)
    - Any warnings or issues encountered
</process>

<state_transitions>
**Classification Transition Rules:**

| From | To | Directory | Gate Condition | Special Actions |
|------|-----|-----------|----------------|-----------------|
| queued | ready | 0-queued → 1-ready | Design exists AND dependencies in 4-completed AND (if parent) all children have designs | Validate design/ directory exists |
| ready | in-progress | 1-ready → 2-in-progress | User executes /outcome:focus | Move entire tree if parent |
| in-progress | blocked | 2-in-progress → 3-blocked | Blocker identified | Record blocker, cascade to children if parent |
| blocked | in-progress | 3-blocked → 2-in-progress | Blocker resolved | Move blocker to history |
| in-progress | completed | 2-in-progress → 4-completed | All effects verified AND (if parent) all children state=success | Update maturity, move entire tree |
| completed | in-progress | 4-completed → 2-in-progress | Reopen | Remove from builtByOutcomes, recalc maturity |
| in-progress | queued | 2-in-progress → 0-queued | Defer | Reset progress if needed |
| in-progress | ready | 2-in-progress → 1-ready | Pause work | Keep progress, allow other work |

**Classification Descriptions:**
- `0-queued`: Newly created, awaiting design
- `1-ready`: Has design, dependencies met, ready to focus
- `2-in-progress`: Currently being worked on (focused)
- `3-blocked`: Work stopped due to blocker
- `4-completed`: All effects verified, work finished

**Parent-Child Rules:**
- Parent and children share ONE classification (move as a unit)
- Parent blocked → all children blocked (cascade down)
- Child can block independently
- Parent can't advance to 1-ready until all children have designs
- Parent can't complete until all children state=success

**Completion Requirements:**
- At least 1 observable effect verified (ideally all)
- All tasks in success state (or explicit override)
- For parents: all children must have state=success
- Work summary provided for transition log
</state_transitions>

<verification>
Before completing, verify for EACH moved outcome:
- [ ] Outcome directory moved to correct state folder
- [ ] outcome_track.json updated with new state and timestamps
- [ ] ALL capability_track.json files updated with new outcome path
- [ ] If completed: maturity recalculated and builtByOutcomes updated
- [ ] outcome_summary.json entry updated with new path and state
- [ ] outcome_summary.json indexByState arrays updated
- [ ] capability_summary.json indexByOutcome updated
- [ ] outcome-statement.md has transition log entry
- [ ] All JSON files validate against schemas
</verification>

<success_criteria>
- All specified outcomes moved to target state
- Cross-references intact in ALL tracking files:
  - capability_track.json (requiredOutcomes/builtByOutcomes paths)
  - outcome_summary.json (trackingFile paths, indexByState)
  - capability_summary.json (indexByOutcome)
- For completed outcomes: capability maturity correctly updated
- Transition logged in outcome-statement.md
- All JSON files pass schema validation
- No orphaned references remain
</success_criteria>

<examples>
**Start work on single outcome:**
```
/outcome:move 001-jwt-authentication --to in-progress
```

**Complete multiple outcomes:**
```
/outcome:move 001-jwt-auth 002-session-mgmt --to completed
```

**Infer next state (queued→in-progress):**
```
/outcome:move 003-api-rate-limiting
```

**Reopen completed outcome:**
```
/outcome:move 005-user-profile --to in-progress
```
</examples>