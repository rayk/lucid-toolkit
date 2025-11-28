---
description: Delete a capability and clean up all references in outcomes and summaries
argument-hint: <capability-id>
---

<objective>
Safely delete capability $ARGUMENTS from the workspace, including:
- Removing it from capability_summary.json (all indexes and arrays)
- Deleting its directory in capabilities/
- Removing references from all outcome tracking files
- Updating outcome_summary.json to remove capability references

This ensures complete cleanup with no orphaned references or broken cross-references.
</objective>

<context>
Current capability summary: @status/capability_summary.json
Capability summary schema: @schemas/capability_summary_schema.json
Outcome summary: @status/outcome_summary.json
Outcome tracking schema: @schemas/outcome_track_schema.json
</context>

<process>
1. Read capability_summary.json to verify capability $ARGUMENTS exists
2. Identify the capability's tracking file path from the summary
3. Read capability_track.json to identify all outcomes that reference this capability
4. For each outcome that references this capability:
   - Read the outcome_track.json file
   - Remove the capability reference from the capabilities array
   - Update the outcome_track.json file
5. Remove capability from capability_summary.json:
   - Remove from capabilities array
   - Remove from all indexes (indexByDomain, indexByType, indexByStatus, indexByActivityState, indexByMaturityRange)
   - Remove from blockedCapabilities array
   - Remove from atRiskCapabilities array
   - Update all related from indexByOutcome entries
   - Recalculate summary statistics (totalCapabilities, capabilitiesByType, etc.)
6. Remove capability from outcome_summary.json indexByCapability
7. Delete the capability directory: capabilities/$ARGUMENTS/
8. Verify all files are updated and consistent
</process>

<verification>
Before completing, verify:
- Capability removed from all arrays in capability_summary.json
- Capability removed from all indexes in capability_summary.json
- Summary statistics recalculated correctly in capability_summary.json
- All outcome_track.json files no longer reference the deleted capability
- indexByCapability in outcome_summary.json no longer references the capability
- Capability directory deleted from filesystem
- All JSON files validate against their schemas
</verification>

<success_criteria>
- Capability $ARGUMENTS no longer exists in capability_summary.json
- Capability directory capabilities/$ARGUMENTS/ deleted
- No outcome_track.json files reference the deleted capability
- outcome_summary.json indexByCapability does not contain the deleted capability
- All modified JSON files validate against schemas
- Cross-reference integrity maintained
- No orphaned references remain
</success_criteria>