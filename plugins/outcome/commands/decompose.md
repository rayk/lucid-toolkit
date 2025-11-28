---
description: Decompose an outcome into child outcomes while preserving capability contributions
argument-hint: <outcome-directory-label>
---

<objective>
Decompose outcome $ARGUMENTS into logical child outcomes that together achieve the parent's capability contribution.

Decomposition is appropriate when an outcome:
- Has multiple distinct observable effects that could be delivered independently
- Exceeds token budget estimates (>200K suggests decomposition)
- Spans multiple systems or integration points that can be tackled separately
- Would benefit from incremental delivery of value

The parent outcome becomes type "parent" (aggregator), and new child outcomes are created as type "atomic".
</objective>

<context>
Schema: @schemas/outcome_track_schema.json
Parent outcome: @outcomes/*/$ARGUMENTS/outcome_track.json
Outcome statement: @outcomes/*/$ARGUMENTS/outcome-statement.md
</context>

<decomposition_model>
**Directory naming convention (NESTED structure):**
```
outcomes/{N-classification}/
└── {NNN}-{parent-name}/                    # type: "parent"
    ├── outcome_track.json
    ├── outcome-statement.md
    ├── {NNN}.1-{child-name}/               # NESTED under parent
    │   ├── outcome_track.json              # type: "atomic", parentOutcome: "{NNN}-{parent-name}"
    │   └── outcome-statement.md
    ├── {NNN}.2-{child-name}/               # NESTED under parent
    │   ├── outcome_track.json
    │   └── outcome-statement.md
    └── {NNN}.3-{child-name}/               # NESTED under parent
        ├── outcome_track.json
        └── outcome-statement.md
```

**Parent outcome changes:**
- `type`: "atomic" -> "parent"
- `children`: [] -> ["NNN.1-child-name", "NNN.2-child-name", ...]
- `integrationValidation`: [] -> ["All child outcomes completed", "Integration tests pass", ...]
- Observable effects become aggregate ("Given all child outcomes complete...")

**Child outcome structure:**
- `type`: "atomic"
- `parentOutcome`: "{NNN}-{parent-name}"
- `capabilityContributions`: [] (empty - children do NOT have direct capability contributions)
- `parentContribution`: Percentage of parent's work this child represents (all children must sum to 100%)
- Own observable effects (subset of parent's or new specific ones)
- Same state as parent (all in same state folder)
</decomposition_model>

<process>
1. **Locate and validate** the outcome specified in $ARGUMENTS
   - Must exist in outcomes/{0-queued|1-ready|2-in-progress|3-blocked}/
   - Must be type "atomic" (cannot decompose already-decomposed outcomes)
   - Extract parent number (NNN) for child numbering
   - Note current classification (children will be nested under parent in same classification)

2. **Analyze the outcome** to propose decomposition:
   - Review observable effects - each may become a child outcome
   - Review scope.included items - each may map to a child
   - Review capability contributions - will be distributed across children
   - Review token budget - distribute proportionally

3. **Present proposed decomposition** to user:
   ```
   Proposed decomposition of {NNN}-{outcome-name}:

   Parent: {NNN}-{outcome-name} (type: parent)
   └── Integration validation: [criteria...]

   Children:
   ├── {NNN}.1-{name}: {description}
   │   └── Capability: {id} +{X}%, Observable effects: [1, 2]
   ├── {NNN}.2-{name}: {description}
   │   └── Capability: {id} +{Y}%, Observable effects: [3]
   └── {NNN}.3-{name}: {description}
       └── Capability: {id} +{Z}%, Observable effects: [4, 5, 6]

   Total capability contribution: X + Y + Z = {parent's original contribution}%
   ```

4. **Gather user feedback** using AskUserQuestion:
   - Allow renaming children
   - Allow redistributing observable effects
   - Allow adjusting capability contribution splits
   - Allow adding/removing children
   - Confirm integration validation criteria

5. **Validate decomposition integrity**:
   - Sum of child `parentContribution` values = 100%
   - All observable effects assigned to exactly one child OR parent's integration validation
   - No orphaned scope items
   - Token budgets distributed reasonably

6. **Execute decomposition** (only after user approval):

   a. **Update parent outcome_track.json**:
      - Set `type`: "parent"
      - Set `children`: ["{NNN}.1-...", "{NNN}.2-...", ...]
      - Set `integrationValidation`: [user-approved criteria]
      - Update observable effects to aggregate form
      - Clear `capabilityContributions` (children own these now) OR keep as aggregate

   b. **Create child directories NESTED under parent**:
      ```
      outcomes/{N-classification}/{NNN}-{parent-name}/{NNN}.{X}-{child-name}/
      ├── outcome_track.json
      ├── outcome-statement.md
      ├── reports/
      └── evidence/
      ```
      Children are physically nested inside the parent directory.

   c. **Generate child outcome_track.json** for each:
      - `type`: "atomic"
      - `parentOutcome`: "{NNN}-{parent-name}"
      - `capabilityContributions`: [] (empty - children don't contribute directly)
      - `parentContribution`: percentage of parent's work (must sum to 100% across siblings)
      - `observableEffects`: assigned effects
      - `state`: same as parent
      - `projects`: inherit from parent (or subset)
      - `actors`: inherit from parent (or subset)

   d. **Generate child outcome-statement.md** for each

7. **Update cross-references**:
   - Keep ONLY parent path in capability_track.json `builtByOutcomes` (children are tracked via parent)
   - Do NOT add child paths to builtByOutcomes - they contribute via parent

8. **Validate all created files** against schema
</process>

<validation>
Before executing decomposition:
- [ ] Parent outcome exists and is type "atomic"
- [ ] Proposed children cover all scope.included items
- [ ] All observable effects assigned to children or integration validation
- [ ] Child parentContribution values sum to 100%
- [ ] Child names follow pattern `^[a-z0-9]+(-[a-z0-9]+){0,4}$`
- [ ] Child directory labels follow pattern `^[0-9]+\.[0-9]+-[a-z0-9]+(-[a-z0-9]+){0,4}$`
- [ ] User has approved the decomposition plan
</validation>

<capability_contribution_rules>
**Parent-Child Contribution Model:**
- Parent outcomes OWN `capabilityContributions` (e.g., +25% to capability)
- Child outcomes have `capabilityContributions: []` (empty)
- Children declare `parentContribution` as % of parent's work (must sum to 100%)
- Capability maturity updates ONLY when parent completes (all children done)

**Example:**
```
Parent: obligation-discovery +25% (parent owns this contribution)

After decomposition (using parentContribution):
├── Child 1: parentContribution: 40%  (represents 40% of parent's work)
├── Child 2: parentContribution: 35%  (represents 35% of parent's work)
└── Child 3: parentContribution: 25%  (represents 25% of parent's work)
                                ----
                          Sum: 100% of parent

When parent completes → capability gets the full +25%
```

Children do NOT have direct capabilityContributions - only parentContribution.
The parent's capabilityContributions remain on the parent and are applied when the parent completes.
</capability_contribution_rules>

<integration_validation_examples>
Parent outcomes should define criteria that verify children work together:

- "All child outcomes completed successfully"
- "End-to-end workflow test passes across all components"
- "No integration gaps between child deliverables"
- "Combined functionality achieves original outcome's purpose"
- "Performance meets aggregate requirements"
</integration_validation_examples>

<output>
Files modified:
- `outcomes/{N-classification}/{NNN}-{parent}/outcome_track.json` - Updated to type "parent"
- `outcomes/{N-classification}/{NNN}-{parent}/outcome-statement.md` - Updated with decomposition info

Files created (per child, NESTED under parent):
- `outcomes/{N-classification}/{NNN}-{parent}/{NNN}.{X}-{child}/outcome_track.json`
- `outcomes/{N-classification}/{NNN}-{parent}/{NNN}.{X}-{child}/outcome-statement.md`
- `outcomes/{N-classification}/{NNN}-{parent}/{NNN}.{X}-{child}/reports/`
- `outcomes/{N-classification}/{NNN}-{parent}/{NNN}.{X}-{child}/evidence/`

Cross-references:
- `capabilities/.../capability_track.json` - only parent in builtByOutcomes (children tracked via parent)
</output>

<success_criteria>
- Parent outcome converted to type "parent" with children array populated
- All child outcomes created with correct parentOutcome reference
- Child parentContribution values sum to 100%
- All observable effects distributed appropriately
- Integration validation criteria defined on parent
- All files validate against schema
- Cross-references updated in capability_track.json files
- User approved the decomposition before execution
</success_criteria>

<rollback>
If decomposition fails partway through:
1. Delete any created child directories
2. Restore parent outcome_track.json from git (or backup)
3. Restore capability_track.json cross-references
4. Report what failed and why
</rollback>
