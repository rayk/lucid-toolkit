---
description: Create a complete capability statement following workspace standards
argument-hint: [capability-name or description]
---

<objective>
Produce a complete capability statement that complies with the workspace schema and template requirements.

This command creates a comprehensive capability definition that:
- Maps to 1-3 core business values from the 34-value framework
- Uses YAML frontmatter as the single source of truth for tracking data
- Captures strategic context, maturity milestones, and measurement criteria
</objective>

<critical_constraints>
**FORMAT REQUIREMENTS - MUST FOLLOW:**

1. **YAML Frontmatter is MANDATORY** - The capability-statement.md MUST start with proper YAML frontmatter between `---` delimiters. Do NOT use markdown metadata sections.

2. **NO capability_track.json** - This file is DEPRECATED. All tracking data goes in YAML frontmatter only.

3. **NO Placeholder Text** - NEVER write "TBD", "TODO", "[placeholder]", or empty sections. If information is unknown, write a concrete statement like "No outcomes currently assigned" or "None identified".

4. **Actor IDs MUST be kebab-case** - Pattern: `^[a-z0-9]+(-[a-z0-9]+)*$`
   - CORRECT: `lot-owner`, `strata-manager`, `platform-developers`
   - WRONG: `Lot Owner`, `StrataManager`, `Platform Developers`

5. **Single File Output** - Only create `capability-statement.md`. No other files.
</critical_constraints>

<context>
**Files to Read** (read these directly, do NOT use toon-specialist):

| Purpose | Path |
|---------|------|
| Template structure | `@templates/outputs/capability-statement-template.md` |
| Core values (34 values) | `@templates/data/core-values-schema.toon` |
| Actor registry | `@templates/data/actor-registry-schema.toon` |
| Workspace config | `.claude/workspace-info.toon` (in workspace root) |

**Note:** The `@templates/` paths are relative to the ws plugin directory. In the installed workspace, these resolve to the plugin's templates folder.
</context>

<process>

## Phase 1: Load Context (2-3 Read calls max)

1. **Read workspace-info.toon** from workspace root (`.claude/workspace-info.toon`)
   - Extract `capabilities.path` for output location
   - Note existing capability IDs to validate uniqueness

2. **Read the template** to understand exact YAML frontmatter structure
   - `@templates/outputs/capability-statement-template.md`

3. **Read reference schemas** (if needed for actor/value selection):
   - `@templates/data/core-values-schema.toon` - 34 core values by category
   - `@templates/data/actor-registry-schema.toon` - actors by domain

## Phase 2: Gather Capability Identity

4. **Determine capability name and ID**:
   - If `$ARGUMENTS` provided: Use as starting point
   - Otherwise: Ask user what capability to define
   - Generate ID: `^[a-z0-9]+(-[a-z0-9]+)*$` pattern
   - Validate ID is unique (not in existing capabilities)

5. **Capture strategic foundation**:
   - **Purpose**: Action-oriented ("Enable the system to...")
   - **Type**: `atomic` (built from outcomes) or `composed` (built from sub-capabilities)
   - **Domain**: Strategic category
   - **Target Maturity**: 60-100% typically

## Phase 3: Gather Details (Ask user or infer from context)

6. **Actor Involvement** (REQUIRED - at least 1 actor):
   - Present actors from registry organized by domain
   - For each selected actor:
     - `id`: kebab-case identifier (e.g., `lot-owner`, `strata-manager`)
     - `relationship`: requires | provides | consumes | enables | governs
     - `criticality`: essential | important | optional

7. **Core Business Values** (REQUIRED - 1-3 primary values):
   - Present 34 values from core-values-schema.toon
   - For each selected value:
     - Contribution percentage (must sum to 100%)
     - Rationale with measurable business impact
   - Optional: 0-2 secondary values

8. **Value Proposition** (categorized benefits):
   - Risk Mitigation: Quantified improvements
   - User Experience: Measurable UX gains
   - Development Velocity: Time/effort savings
   - Compliance: Standards met

9. **Scope Boundaries**:
   - **Included**: 3-5 specific responsibilities
   - **Excluded**: 3-5 explicit non-goals

10. **Maturity Milestones** (all 4 required with concrete deliverables):
    - 30% Experimental: Proof of concept validated
    - 60% Tactical: Usable in constrained production
    - 80% Production: Reliable, well-documented
    - 100% Comprehensive: Industry-leading

11. **Measurement Criteria**:
    - Criteria: 3-5 assessment methods
    - Evidence: 3-5 observable artifacts
    - Metrics: Table with Target/Current/Gap

12. **Dependencies**:
    - Prerequisites: Capabilities needed first (with min maturity)
    - Enables: Capabilities unlocked by this one

13. **Composition** (based on type):
    - Atomic: Note that outcomes will be added later (NO TBD!)
    - Composed: Sub-capabilities with weights (must sum to 100%)

## Phase 4: Generate and Validate

14. **Generate capability-statement.md**:
    - Start with YAML frontmatter (see template below)
    - Follow with markdown body sections
    - Save to `{capabilities.path}/[capability-id]/capability-statement.md`

15. **Validate with capability-checker**:
    ```
    Task(
      subagent_type="ws:capability-checker",
      prompt="Validate capability at {path}"
    )
    ```
    - VALID → Complete
    - NEEDS_ATTENTION → Review warnings with user
    - INVALID → Fix critical issues, re-validate

</process>

<yaml_frontmatter_template>
The YAML frontmatter MUST follow this exact structure:

```yaml
---
identifier: capability-id           # kebab-case, matches directory name
name: Human-Readable Name           # Display name
type: atomic                        # atomic | composed
status: active                      # active | deprecated | planned
domain: strategic-domain            # e.g., security, infrastructure

maturity:
  current: 0                        # 0-100, starts at 0 for new capabilities
  target: 80                        # 0-100, strategic goal

coreValues:
  primary:
    - value: Value Name
      contribution: 60
    - value: Another Value
      contribution: 40

actors:
  - id: actor-id                    # MUST be kebab-case
    relationship: requires          # requires | provides | consumes | enables | governs
    criticality: essential          # essential | important | optional

relationships:
  prerequisites: []                 # or list.md of {capability, minMaturity}
  enables: []                       # or list.md of capability-ids

# For type: composed only
# subCapabilities:
#   - id: sub-cap-id
#     weight: 40                    # Must sum to 100

validation:
  lastChecked: null
  status: UNCHECKED
---
```
</yaml_frontmatter_template>

<anti_patterns>
**NEVER DO THESE:**

| Anti-Pattern | Correct Approach |
|--------------|------------------|
| Create `capability_track.json` | All tracking in YAML frontmatter |
| Write "TBD" or "TODO" anywhere | Write concrete content or "None identified" |
| Use Title Case actor IDs (`Lot Owner`) | Use kebab-case (`lot-owner`) |
| Markdown metadata section (`## Metadata`) | YAML frontmatter between `---` |
| Glob/search for template files | Read from known paths directly |
| Invoke toon-specialist to read schemas | Read TOON files directly with Read tool |
| Leave empty sections | Populate or state "None" / "Not applicable" |
</anti_patterns>

<output>
**File created:**
- `{capabilities.path}/[capability-id]/capability-statement.md`

The file contains:
- YAML frontmatter with machine-parseable tracking data
- Markdown body following workspace template structure
</output>

<output_format>
When returning results, use TOON format:

```toon
@type: CreateAction
actionStatus: CompletedActionStatus
@id: capability-id
result: Created capability with initial maturity 0%

filesCreated[1]: capability-statement.md
validationStatus: VALID
```

**No `crossRefsUpdated` field** - we no longer update capability_track.json or summary files.
</output_format>

<epilogue>
After successful capability creation, sync workspace indexes:

```
Skill("capability-index-sync")
```

This ensures capabilities-info.toon and project-info.toon reflect the new capability.
</epilogue>
