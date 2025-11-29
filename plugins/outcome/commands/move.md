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
- Updates ALL outcome path references in capability_track.json files:
  - outcomes.requiredOutcomes[].outcomeTrackingFile
  - outcomes.builtByOutcomes[].outcomeTrackingFile
  - outcomes.enablesOutcomes[].outcomeTrackingFile
- Updates outcome_summary.json with new paths:
  - outcomes[].trackingFile
  - indexByState arrays
- Updates capability_summary.json with new paths:
  - indexByOutcome keys (old path → new path)
  - Capability progress counters and maturity metrics
- Records transition in outcome-statement.md
- For completed outcomes: updates capability maturity calculations
- Validates classification transition rules before moving
</objective>

<delegation_mandate>
CRITICAL: Moving outcomes requires 10-30+ file operations. You MUST delegate.

Phase 1 (Main Context - 0-3 tools max):
- Parse $ARGUMENTS to extract outcome IDs and target state
- Validate arguments (outcome exists, valid transition)
- IMMEDIATELY delegate Phase 2

Phase 2 (Delegated via Task tool):
- ALL file operations happen in subagent
- Agent: general-purpose
- Model: sonnet (standard) OR opus (parent trees with 5+ children)

DO NOT read tracking files in main context.
</delegation_mandate>

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

   For each outcome being moved (parent and all children):
   ```json
   {
     "outcome": {
       "state": "<new-state>",
       "updatedAt": "<current-timestamp>",
       "completedAt": "<timestamp-if-completed, null-otherwise>"
     }
   }
   ```

   **Note for parent outcomes**: Update parent's outcome_track.json AND all child outcome_track.json files with new state and timestamps. Parent and children share the same classification state.

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

8. **Update capability path references**

   **Critical**: When an outcome moves between state directories, ALL file paths referencing it must be updated across tracking files.

   For each capability in outcome_track.json's capabilityContributions:

   a. **Read the capability_track.json file**
      - Location: capabilities/{capability-id}/capability_track.json

   b. **Calculate old and new outcome paths**
      - Old path: outcomes/{old-classification}/{directory-label}/outcome_track.json
      - New path: outcomes/{new-classification}/{directory-label}/outcome_track.json
      - For parent outcomes: path is to parent directory (e.g., outcomes/0-queued/005-parent/outcome_track.json)
      - For child outcomes: paths include parent directory (e.g., outcomes/0-queued/005-parent/005.1-child/outcome_track.json)
      - **Important**: When parent moves, ALL child outcome paths must also be updated across all tracking files

   c. **Update paths in capability_track.json arrays**
      - In `outcomes.requiredOutcomes[]`: Find entry with outcomeTrackingFile matching old path → update to new path
      - In `outcomes.builtByOutcomes[]`: Find entry with outcomeTrackingFile matching old path → update to new path
      - In `outcomes.enablesOutcomes[]`: Find entry with outcomeTrackingFile matching old path → update to new path

   d. **Handle state-specific transitions**
      - If moving TO `completed`:
        - Remove from `requiredOutcomes[]`
        - Add to `builtByOutcomes[]` with contributionPercent and completedDate (current timestamp)
        - Recalculate `currentMaturity` = sum of all builtByOutcomes[].contributionPercent
      - If moving FROM `completed` (reopening):
        - Remove from `builtByOutcomes[]`
        - Add back to `requiredOutcomes[]` with contributionPercent
        - Recalculate `currentMaturity`
      - For all other moves (queued ↔ ready ↔ in-progress ↔ blocked):
        - Only update the path in requiredOutcomes[] (no maturity changes)

   e. **Write updated capability_track.json**

   f. **Update metadata timestamps**
      - Set capability_track.json `metadata.updated` to current timestamp

9. **Update outcome_summary.json**

   **Critical**: The outcome_summary.json contains multiple references to outcome paths that must all be updated.

   a. **Update outcomes[] entry**
      - Find entry where `id` matches the outcome being moved
      - Update fields:
        - `state`: new state (queued, ready, in-progress, blocked, or completed)
        - `trackingFile`: new path (outcomes/{new-classification}/{directory-label}/outcome_track.json)
        - `updatedAt`: current timestamp
        - `completedAt`: current timestamp if moving to completed, null otherwise

   b. **Update indexByState**
      - Remove outcome ID from old state array (e.g., indexByState.queued)
      - Add outcome ID to new state array (e.g., indexByState["in-progress"])
      - Ensure no duplicate IDs in any state array

   c. **Recalculate summary statistics**
      - Update `summary.outcomesByState[old-state]`: decrement count
      - Update `summary.outcomesByState[new-state]`: increment count
      - Update `summary.lastUpdated`: current timestamp

   d. **Write updated outcome_summary.json**

10. **Update capability_summary.json**

    **Critical**: The capability_summary.json maintains a bi-directional index (indexByOutcome) that maps outcome paths to capability IDs.

    a. **Update indexByOutcome**
       - Find all entries in indexByOutcome with key matching old outcome path
       - For each match:
         - Store the array of capability IDs
         - Delete the old path key: `delete indexByOutcome[old-path]`
         - Create new path key with same capability IDs: `indexByOutcome[new-path] = [capability-ids]`

    b. **Update capability entries (if moving to/from completed)**
       - For each capability in capabilityContributions:
         - Find capability in `capabilities[]` array by folderName
         - If moving TO completed:
           - Update `atomicProgress.completedOutcomesCount`: increment by 1
           - Update `atomicProgress.inProgressOutcomesCount` or `atomicProgress.queuedOutcomesCount`: decrement by 1
           - Update `currentMaturity`: new value from capability_track.json
           - Update `maturityGap`: targetMaturity - currentMaturity
           - Update `maturityRange`: recalculate based on new currentMaturity
           - Update `outcomeActivity.lastOutcomeCompleted`: new outcome path
           - Update `outcomeActivity.lastCompletedDate`: current timestamp
           - Update `outcomeActivity.daysSinceLastProgress`: 0
         - If moving FROM completed (reopening):
           - Update `atomicProgress.completedOutcomesCount`: decrement by 1
           - Update `atomicProgress.inProgressOutcomesCount`: increment by 1 (if moving to in-progress)
           - Update `currentMaturity`: new value from capability_track.json
           - Update `maturityGap` and `maturityRange` accordingly
       - Update `updatedAt` timestamp for each affected capability

    c. **Recalculate summary statistics (if moving to/from completed)**
       - Recalculate `summary.totalOutcomesCompleted`
       - Recalculate `summary.averageMaturity`
       - Recalculate `summary.maturityDistribution` counts if capabilities changed maturityRange
       - Recalculate `summary.capabilitiesByActivityState` if activity states changed

    d. **Update metadata timestamp**
       - Set `summary.lastUpdated` to current timestamp

    e. **Write updated capability_summary.json**

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
- [ ] ALL capability_track.json files updated with new outcome paths:
  - [ ] Path updated in outcomes.requiredOutcomes[].outcomeTrackingFile (or removed if completed)
  - [ ] Path updated in outcomes.builtByOutcomes[].outcomeTrackingFile (or added if completed)
  - [ ] Path updated in outcomes.enablesOutcomes[].outcomeTrackingFile
  - [ ] If completed: maturity recalculated and builtByOutcomes updated
  - [ ] metadata.updated timestamp set to current time
- [ ] outcome_summary.json updated with new paths:
  - [ ] outcomes[].trackingFile updated to new path
  - [ ] outcomes[].state updated to new state
  - [ ] outcomes[].completedAt set if moving to completed
  - [ ] Outcome ID removed from old indexByState array
  - [ ] Outcome ID added to new indexByState array
  - [ ] summary.outcomesByState counts recalculated
- [ ] capability_summary.json updated with new paths:
  - [ ] Old outcome path key removed from indexByOutcome
  - [ ] New outcome path key added to indexByOutcome with same capability IDs
  - [ ] If completed: capability.atomicProgress counters updated
  - [ ] If completed: capability.currentMaturity and maturityGap recalculated
  - [ ] If completed: capability.outcomeActivity updated
  - [ ] summary statistics recalculated
- [ ] outcome-statement.md has transition log entry
- [ ] All JSON files validate against schemas
- [ ] No orphaned references to old paths remain in any file
</verification>

<success_criteria>
- All specified outcomes moved to target state
- Cross-references intact in ALL tracking files:
  - capability_track.json files:
    - All occurrences of old outcome path replaced with new path
    - Paths updated in requiredOutcomes[], builtByOutcomes[], and enablesOutcomes[]
    - For completed outcomes: outcome moved from requiredOutcomes to builtByOutcomes
  - outcome_summary.json:
    - outcomes[].trackingFile updated to new path
    - indexByState arrays correctly reflect new state
    - Summary statistics recalculated
  - capability_summary.json:
    - indexByOutcome keys updated (old path removed, new path added)
    - Capability progress metrics updated if outcome completed
    - Summary statistics recalculated if needed
- For completed outcomes:
  - Capability maturity correctly recalculated
  - Capability progress counters updated
  - outcomeActivity reflects completion
- Transition logged in outcome-statement.md
- All JSON files pass schema validation
- No orphaned references to old paths remain in any file
- Parent-child outcomes moved together as a unit (if applicable)
</success_criteria>

<output_format>
## Standard Output (Human-Readable)

On success:
```
Moved [N] outcome(s) to [target-state]:
- [label-1]: [old-state] → [new-state]
- [label-2]: [old-state] → [new-state]

Capability maturity updates (if completing):
- [cap-id]: [old]% → [new]% (+[delta]%)
```

## TOON Format (Machine-Readable)

For subagent returns and structured data exchange:

```toon
@type: UpdateAction
actionStatus: CompletedActionStatus
name: move-outcomes
result: Moved [N] outcomes to [target-state]

transitions[N]{@id,fromStatus,toStatus}:
001-jwt-auth,PotentialActionStatus,ActiveActionStatus
002-session-mgmt,PotentialActionStatus,ActiveActionStatus

maturity[N]{capability,from,to,delta}:
authentication-system,45,47,+2
```

**ActionStatusType Mapping:**
- queued, ready, pending → `PotentialActionStatus`
- in-progress, active → `ActiveActionStatus`
- completed, success → `CompletedActionStatus`
- blocked, failed → `FailedActionStatus`

**Fields:**
- `@type`: UpdateAction (state transitions)
- `actionStatus`: CompletedActionStatus if successful
- `name`: move-outcomes
- `result`: Summary message
- `transitions[N]`: Tabular array with outcome @id, fromStatus, toStatus
- `maturity[N]`: Tabular array with capability, from, to, delta (only if completing outcomes)
</output_format>

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