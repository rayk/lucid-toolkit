---
description: Create a new outcome with proper structure, capability linkage, and workspace integration
argument-hint: [outcome-name or description]
---

<objective>
Produce a complete outcome statement that builds toward capabilities following workspace schema and conventions.

Outcomes are units of tactical work that BUILD capabilities. Each outcome:
- Describes WHAT to achieve (not HOW to implement)
- Specifies observable effects in Given-When-Then format
- Links to capabilities with maturity contribution percentages
- Starts in `queued` stage in the outcomes directory
</objective>

<critical_constraints>
**FORMAT REQUIREMENTS - MUST FOLLOW:**

1. **YAML Frontmatter is MANDATORY** - The outcome-statement.md MUST start with proper YAML frontmatter between `---` delimiters.

2. **NO Placeholder Text** - NEVER write "TBD", "TODO", "[placeholder]", or empty sections. If information is unknown, write "None identified" or "Not applicable".

3. **Outcome IDs MUST follow pattern** - `^[0-9]+-[a-z0-9]+(-[a-z0-9]+){0,4}$`
   - CORRECT: `001-jwt-auth`, `005-data-model`, `010.1-session-mgmt`
   - WRONG: `JWT Auth`, `DataModel`, `1-jwt`

4. **Achievement Focus** - Outcomes describe WHAT to accomplish, never HOW (no process prescriptions).

5. **Given-When-Then Effects** - Observable effects MUST use Gherkin format with actor perspectives.

6. **Single File Output** - Only create `outcome-statement.md` in the outcome directory.
</critical_constraints>

<context>
**Files to Read** (read these directly):

| Purpose | Path |
|---------|------|
| Workspace config | `.claude/project-info.toon` (in workspace root) |
| Outcomes schema | `@templates/data/outcomes-info-schema.toon` |
| Actor registry | `@templates/data/actor-registry-schema.toon` |

**Note:** The `@templates/` paths are relative to the ws plugin directory.
</context>

<process>

## Phase 1: Load Context (2-3 Read calls max)

1. **Read project-info.toon** from workspace root (`.claude/project-info.toon`)
   - Extract `outcomes.path` for output location
   - Note existing outcome IDs to validate uniqueness
   - Get next sequence number

2. **Read reference schemas** (if needed for actor selection):
   - `@templates/data/actor-registry-schema.toon` - actors by domain
   - `@templates/data/outcomes-info-schema.toon` - understand structure

## Phase 2: Determine Outcome Identity

3. **Parse $ARGUMENTS**:
   - If clear intent provided: Extract name and purpose
   - If ambiguous: Ask user for clarification using AskUserQuestion

4. **Generate outcome ID**:
   - Sequence number: 3-digit zero-padded (e.g., 001, 005, 012)
   - Name: kebab-case descriptor (e.g., `jwt-auth`, `data-model`)
   - Full ID: `{sequence}-{name}` (e.g., `005-jwt-auth`)
   - For child outcomes: `{parent}.{child}-{name}` (e.g., `005.1-session-mgmt`)

## Phase 3: Gather Details

5. **Core Information** (REQUIRED):
   - **Achievement**: 1-2 sentences describing WHAT to accomplish
   - **Purpose**: Why this outcome is needed
   - **Stage**: Always `queued` for new outcomes

6. **Observable Effects** (REQUIRED - minimum 2):
   - Each effect in Given-When-Then format
   - Each effect tied to an actor perspective
   - Cover success cases AND error handling

7. **Capability Contributions** (REQUIRED - at least 1):
   - Capability ID (must exist in workspace)
   - Maturity contribution percentage (typically 5-20%)
   - Rationale for contribution

8. **Actor Involvement** (REQUIRED - at least 1):
   - Actor ID from registry (kebab-case)
   - Relationship: beneficiary | stakeholder | contributor | approver | informed

9. **Scope Boundaries**:
   - **Included**: 3-5 specific responsibilities
   - **Excluded**: 3-5 explicit non-goals

10. **Token Budget Estimate**:
    - very-low: <25K tokens
    - low: 25-75K tokens
    - average: 75-150K tokens
    - high: 150-200K tokens
    - If >200K: Must split into parent/child structure

## Phase 4: Generate and Sync

11. **Create outcome directory**:
    ```
    {outcomes.path}/queued/{outcome-id}/
    ```
    - Create subdirectories: `reports/`, `evidence/`

12. **Generate outcome-statement.md**:
    - Start with YAML frontmatter (see template below)
    - Follow with markdown body sections
    - Save to `{outcome-dir}/outcome-statement.md`

13. **Sync workspace indexes**:
    ```
    Skill("outcome-index-sync")
    ```

</process>

<yaml_frontmatter_template>
The YAML frontmatter MUST follow this exact structure:

```yaml
---
identifier: 005-outcome-name        # Matches directory name
name: Human-Readable Outcome Name   # Display name
stage: queued                       # queued | ready | in-progress | blocked | completed
priority: P2                        # P1 | P2 | P3

achievement: |
  Achieve [specific result] so that [business/user benefit].

purpose: |
  Why this outcome is needed and what problem it solves.

tokenBudget: average               # very-low | low | average | high

capabilityContributions:
  - capabilityId: capability-id
    contribution: 15               # percentage (typically 5-20%)
    rationale: How this advances the capability

actors:
  - id: actor-id                   # MUST be kebab-case
    relationship: beneficiary      # beneficiary | stakeholder | contributor | approver | informed

dependencies:
  dependsOn: []                    # List of outcome-ids that must complete first
  enables: []                      # List of outcome-ids unlocked by this

# For child outcomes only:
# parentOutcome: 005-parent-name
# parentContribution: 40           # What % of parent's work this represents
---
```
</yaml_frontmatter_template>

<observable_effects_template>
Each observable effect MUST use this structure in the markdown body:

```markdown
### Effect 1: [Short Title]
**Actor**: [actor-id from registry]

```gherkin
Given [precondition/context]
When [action/trigger]
Then [observable outcome]
```

**Verification**: [How to prove this effect exists]
```

**Anti-patterns to AVOID:**
- Implementation artifacts: "Tests pass", "File created", "Code reviewed"
- Process prescriptions: "Use TDD", "Follow agile"
- Vague effects: "Works better", "Is improved"

**Patterns to FOLLOW:**
- Behavioral changes: "User can authenticate"
- Observable states: "Unauthorized access is prevented"
- Measurable outcomes: "Response time under 200ms"
</observable_effects_template>

<anti_patterns>
**NEVER DO THESE:**

| Anti-Pattern | Correct Approach |
|--------------|------------------|
| Write "TBD" or "TODO" | Write concrete content or "None identified" |
| Process prescriptions ("Use TDD") | Achievement focus ("Users can authenticate") |
| Implementation artifacts ("Tests pass") | Behavioral effects ("Invalid requests rejected") |
| Title Case actor IDs (`Lot Owner`) | Kebab-case (`lot-owner`) |
| Capability dependencies | Outcome dependencies only (outcomes BUILD capabilities) |
| Token budget >200K without splitting | Create parent with child outcomes |
| Leave empty sections | Populate or state "Not applicable" |
</anti_patterns>

<output>
**Files created:**
- `{outcomes.path}/queued/{outcome-id}/outcome-statement.md`
- `{outcomes.path}/queued/{outcome-id}/reports/` (directory)
- `{outcomes.path}/queued/{outcome-id}/evidence/` (directory)
</output>

<output_format>
When returning results, use TOON format:

```toon
@type: CreateAction
actionStatus: CompletedActionStatus
@id: 005-outcome-name
result: Created outcome for [capability] with [contribution]% contribution

filesCreated[1]: outcome-statement.md
dirsCreated[2]: reports,evidence
stage: queued
```
</output_format>

<epilogue>
After successful outcome creation, sync workspace indexes:

```
Skill("outcome-index-sync")
```

This ensures outcomes-info.toon and project-info.toon reflect the new outcome.
</epilogue>

<success_criteria>
- Outcome directory created in `{outcomes.path}/queued/`
- outcome-statement.md has valid YAML frontmatter
- At least 2 observable effects in Given-When-Then format
- At least 1 capability contribution with valid capability ID
- At least 1 actor involvement with valid actor ID
- Achievement description is behavioral (not implementation-focused)
- No placeholder text (TBD, TODO, etc.)
- Token budget within acceptable range
- Workspace indexes synced via outcome-index-sync skill
</success_criteria>
