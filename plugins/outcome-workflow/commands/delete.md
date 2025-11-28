---
description: Delete an outcome and clean up all cross-references in capabilities and summaries
argument-hint: <outcome-directory-label>
---

<objective>
Safely delete outcome $ARGUMENTS from the workspace, including:
- Removing the outcome directory from outcomes/{state}/
- Removing outcome from outcome_summary.json (all arrays and indexes)
- Removing outcome references from capability_track.json files (requiredOutcomes, builtByOutcomes, enablesOutcomes)
- Removing outcome from capability_summary.json indexByOutcome
- Updating summary statistics in both summary files

This ensures complete cleanup with no orphaned references or broken cross-references.
</objective>

<context>
Outcome summary: @status/outcome_summary.json
Outcome summary schema: @schemas/outcome_summary_schema.json
Capability summary: @status/capability_summary.json
Capability summary schema: @schemas/capability_summary_schema.json
Capability track schema: @schemas/capability_track_schema.json
Outcome track schema: @schemas/outcome_track_schema.json
Existing outcomes: !`find outcomes -type d -name "[0-9]*-*" 2>/dev/null | sed 's/.*\///' | sort`
</context>

<process>
1. **Locate the outcome**
   - Search across all states: outcomes/queued/, outcomes/ready/, outcomes/in-progress/, outcomes/blocked/, outcomes/completed/
   - Find directory matching $ARGUMENTS (e.g., "001-jwt-authentication")
   - If not found, report error and exit

2. **Read outcome tracking file**
   - Load outcome_track.json from the located directory
   - Extract: outcome ID, capabilityContributions, state

3. **Verify safe to delete**
   - Check outcome state:
     - If `completed`: Warn that maturity calculations may be affected
     - If `in-progress`: Warn about work-in-progress loss
     - If `blocked`: Note that blocker information will be lost
   - Check if other outcomes depend on this one (via `outcomeDependencies`)
   - Ask user to confirm deletion if any warnings apply

4. **Remove outcome from capability references**
   For each capability in capabilityContributions:
   - Read capability_track.json
   - Remove outcome from `requiredOutcomes` array (match by outcomeTrackingFile path)
   - Remove outcome from `builtByOutcomes` array (match by outcomeTrackingFile path)
   - Remove outcome from `enablesOutcomes` array (match by outcomeTrackingFile path)
   - If outcome was in `builtByOutcomes`, recalculate `currentMaturity`
   - Write updated capability_track.json

5. **Update outcome_summary.json**
   - Remove outcome from `outcomes` array (match by id or directoryLabel)
   - Remove outcome ID from `indexByState` appropriate state array
   - Remove outcome ID from all entries in `indexByCapability`
   - Recalculate `summary` statistics:
     - totalOutcomes
     - outcomesByState
     - totalTasks
     - tasksByState
     - totalEstimatedTokens
     - totalConsumedTokens
     - overallCompletionRate
     - lastUpdated

6. **Update capability_summary.json**
   - Remove outcome from `indexByOutcome` entries
   - Update lastUpdated timestamp

7. **Delete outcome directory**
   - Remove entire directory: outcomes/{state}/$ARGUMENTS/
   - This includes outcome_track.json, outcome-statement.md, reports/, evidence/

8. **Validate changes**
   - Verify outcome no longer exists in filesystem
   - Verify outcome removed from outcome_summary.json
   - Verify capability references cleaned up
</process>

<verification>
Before completing, verify:
- Outcome directory deleted from filesystem
- Outcome removed from outcome_summary.json outcomes array
- Outcome ID removed from indexByState in outcome_summary.json
- Outcome ID removed from all indexByCapability entries in outcome_summary.json
- All capability_track.json files no longer reference the deleted outcome
- indexByOutcome in capability_summary.json no longer references the outcome
- Summary statistics recalculated correctly
- All modified JSON files validate against their schemas
</verification>

<success_criteria>
- Outcome directory outcomes/{state}/$ARGUMENTS/ deleted
- Outcome no longer exists in outcome_summary.json
- No capability_track.json files reference the deleted outcome path
- capability_summary.json indexByOutcome does not contain the deleted outcome
- All modified JSON files validate against schemas
- Cross-reference integrity maintained
- No orphaned references remain
- If completed outcome deleted, affected capability maturity recalculated
</success_criteria>