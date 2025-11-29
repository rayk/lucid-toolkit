---
description: Edit an existing outcome's properties, observable effects, capability contributions, or project associations
argument-hint: <outcome-id> [field-to-edit]
---

<objective>
Edit an existing outcome identified by $1 (outcome directory label like `001-jwt-authentication`).

If $2 is provided, edit that specific field. Otherwise, present available edit options.

This command modifies outcome properties while maintaining schema compliance and cross-reference integrity.
</objective>

<context>
Schema: @schemas/outcome_track_schema.json
Project map: @project_map.json
Existing outcomes: !`find outcomes -type d -name "[0-9]*-*" 2>/dev/null | sed 's/.*\///' | sort`
Target outcome location: !`find outcomes -type d -name "$1" 2>/dev/null | head -1`
Available projects: !`jq -r '.projects[].name' project_map.json 2>/dev/null || echo "No project_map.json found"`
</context>

<editable_fields>
**Core Properties:**
- `description` - Achievement description (WHAT to accomplish)
- `purpose` - Why this outcome is needed
- `scope` - Included/excluded items

**Observable Effects:**
- `effects:add` - Add a new observable effect
- `effects:edit` - Modify an existing effect
- `effects:remove` - Remove an effect (must keep minimum 2)
- `effects:verify` - Mark an effect as verified with evidence

**Capability Contributions:**
- `capabilities:add` - Add a capability contribution
- `capabilities:edit` - Modify contribution % or rationale
- `capabilities:remove` - Remove a contribution (must keep minimum 1)

**Projects:**
- `projects:add` - Add a project association (projectName, involvement, affectedAreas, rationale)
- `projects:edit` - Modify project involvement or affected areas
- `projects:remove` - Remove a project association (must keep minimum 1)

**Dependencies:**
- `dependencies:add` - Add outcome dependency
- `dependencies:remove` - Remove dependency
- `enables:add` - Add outcome this enables
- `enables:remove` - Remove enables relationship

**Actors:**
- `actors:add` - Add actor involvement
- `actors:edit` - Modify actor relationship or description
- `actors:remove` - Remove actor (must keep minimum 1)

**Effort & Complexity:**
- `effort` - Update effort estimate and token budget
- `complexity` - Update complexity indicators

**Rationale:**
- `rationale` - Update problem statement, alternatives, constraints, risks

**State (use with caution):**
- `state` - Change outcome state (queued, ready, in-progress, blocked, completed)
- `blocker` - Add or resolve blocker (only when state is blocked)
</editable_fields>

<process>
1. **Locate outcome** using $1 (search in queued/, in-progress/, completed/)
2. **Read current outcome_track.json** from the outcome directory
3. **Determine edit scope**:
   - If $2 provided: Edit that specific field
   - If no $2: Show current values and ask what to edit

4. **For field-specific edits**:

   **description/purpose/scope:**
   - Show current value
   - Accept new value from user
   - Validate no process prescriptions

   **effects:add:**
   - Prompt for: effect (Given-When-Then), actorPerspective, verificationMethod
   - Add to observableEffects array with verified: false

   **effects:verify:**
   - Show unverified effects
   - User selects which to verify
   - Prompt for evidence: type, reference, verifiedBy
   - Set verified: true, add evidence object with verifiedAt timestamp

   **capabilities:add/edit:**
   - Show available capabilities
   - Prompt for: capabilityId, capabilityPath, maturityContribution, rationale, isPrimary
   - Validate capability path exists

   **projects:add/edit:**
   - Show available projects from project_map.json
   - Prompt for: projectName, involvement (primary/secondary/integration), affectedAreas, rationale
   - Validate projectName exists in project_map.json

   **state:**
   - Validate state transition is allowed
   - If transitioning to blocked: require blocker details
   - If transitioning to completed: verify all effects are verified
   - Update updatedAt timestamp

5. **Update outcome_track.json** with changes
6. **Update outcome-statement.md** to reflect changes
7. **Update cross-references** if capability contributions changed
8. **Validate** updated JSON against schema
</process>

<state_transitions>
Valid transitions:
- queued → ready (when all dependencies complete)
- queued → blocked (external blocker)
- ready → in-progress (execution starts)
- ready → blocked (blocker discovered)
- in-progress → completed (all effects verified)
- in-progress → blocked (blocker encountered)
- blocked → ready (blocker resolved)
- blocked → queued (requires re-planning)

Invalid transitions (reject):
- completed → any (completed is terminal, use revert command instead)
- Any state → completed (without all effects verified)
</state_transitions>

<validation>
After edit, verify:
- [ ] outcome_track.json validates against schema
- [ ] Minimum 2 observable effects maintained
- [ ] Minimum 1 capability contribution maintained
- [ ] Minimum 1 project association maintained
- [ ] Minimum 1 actor involvement maintained
- [ ] No process prescriptions in description
- [ ] Cross-references updated if paths changed
- [ ] updatedAt timestamp updated
</validation>

<output>
Files modified:
- `outcomes/{state}/{outcome-id}/outcome_track.json` - Updated tracking data
- `outcomes/{state}/{outcome-id}/outcome-statement.md` - Updated human-readable doc
</output>

<output_format>
## TOON Format (Subagent Returns)

For outcome edit operations:

```toon
@type: UpdateAction
actionStatus: CompletedActionStatus
@id: 001-jwt-authentication
result: Updated description field

filesUpdated[2]: outcome_track.json,outcome-statement.md
field: description
oldValue: Implement JWT authentication
newValue: Implement JWT authentication with refresh token support
```

**For effects:verify:**
```toon
@type: UpdateAction
actionStatus: CompletedActionStatus
@id: 001-jwt-authentication
result: Verified 2 observable effects

verified[2]{position,effect}:
1,Users can authenticate with valid credentials
2,Invalid tokens are rejected with 401 status

evidence[2]{type,reference}:
test-results,tests/auth_test.py::test_valid_auth
test-results,tests/auth_test.py::test_invalid_token
```

**Fields:**
- `@type`: UpdateAction (field modification)
- `actionStatus`: CompletedActionStatus if successful
- `@id`: outcome directory label
- `result`: Summary of what was edited
- `filesUpdated[N]`: Inline array of files modified
- `field`: Field that was edited
- `oldValue`: Previous value (optional)
- `newValue`: New value (optional)
- `verified[N]`: Tabular array of verified effects (for effects:verify)
- `evidence[N]`: Tabular array of evidence (for effects:verify)
</output_format>

<success_criteria>
- Requested field(s) updated correctly
- Schema validation passes
- Minimum requirements maintained (effects, capabilities, projects, actors)
- Cross-references remain valid
- Both JSON and markdown files synchronized
- updatedAt timestamp reflects edit time
</success_criteria>

<project_involvement_types>
**primary** - Main project where the outcome's work is implemented
**secondary** - Project affected but not the main focus
**integration** - Project involved for integration/compatibility purposes
</project_involvement_types>

<examples>
**Edit description:**
```
/outcome:edit 001-jwt-authentication description
```

**Add observable effect:**
```
/outcome:edit 001-jwt-authentication effects:add
```

**Verify an effect with evidence:**
```
/outcome:edit 001-jwt-authentication effects:verify
```

**Add a project association:**
```
/outcome:edit 001-jwt-authentication projects:add
```

**Change state to in-progress:**
```
/outcome:edit 001-jwt-authentication state
```

**Interactive mode (no field specified):**
```
/outcome:edit 001-jwt-authentication
```
</examples>