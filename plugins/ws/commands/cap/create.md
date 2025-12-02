---
description: Create a complete capability statement following workspace standards
argument-hint: [capability-name or description]
---

<objective>
Produce a complete capability statement that complies with the workspace schema and template requirements.

This command guides you through creating a comprehensive capability definition that:
- Maps to 1-3 core business values from the 34-value framework
- Follows the capability statement template structure
- Validates against capability_track_schema.json requirements
- Captures strategic context, maturity milestones, and measurement criteria
</objective>

<context>
Template reference: @templates/outputs/capability-statement-template.md
Schema validation: @schemas/capability_track_schema.json
Core values reference: @templates/data/core-values.toon
Actor registry reference: @templates/data/actor-registry.toon
Workspace info: Read workspace-info.toon from workspace root for capabilities.path
</context>

<process>
1. **Load Workspace Context**:
   - Read workspace-info.toon from workspace root
   - Extract `capabilities.path` for output location
   - Note existing capabilities from `capability{...}` entries to validate ID uniqueness

2. **Gather Capability Identity**:
   - If $ARGUMENTS provided: Use as starting point for capability name/description
   - Otherwise: Ask user what capability they want to define
   - Generate capability ID following pattern: `^[a-z0-9]+(-[a-z0-9]+)*$`
   - Validate ID uniqueness against existing capabilities

3. **Capture Strategic Foundation**:
   - **Purpose**: What does this capability enable the system to DO? (action-oriented: "Enable the system to...")
   - **Type**: Atomic (built from outcomes) or Composed (built from sub-capabilities)?
   - **Domain**: Strategic category (e.g., "Data Security & Privacy", "Product Lifecycle")
   - **Target Maturity**: What percentage makes this "good enough"? (typically 60-100%)

4. **Identify Actor Involvement** (REQUIRED):
   - Load actors from `status/actor_summary.json`
   - Present actors organized by domain (reference @templates/data/actor-registry.toon)
   - User selects 1+ actors this capability involves/impacts
   - For each selected actor capture:
     - **Relationship type**: requires | provides | consumes | enables | governs
     - **Criticality**: essential | important | optional
     - **Description**: How the actor relates to this capability
   - Validate selected actor IDs exist in the registry

5. **Map Core Business Values** (REQUIRED):
   - Present the 34 core values framework (reference @templates/data/core-values.toon)
   - User selects 1-3 primary values this capability delivers
   - For each value:
     - Contribution percentage (must sum to d100%)
     - Rationale with measurable business impact
   - Optional: 0-2 secondary values with rationale

6. **Define Value Proposition**:
   - Risk Mitigation: Quantified security/compliance/reliability improvements
   - User Experience: Measurable UX improvements
   - Development Velocity: Time/effort savings for developers
   - Compliance: Standards/regulations met

7. **Establish Boundaries**:
   - **Included**: 3-5 specific responsibilities (what IS this capability?)
   - **Excluded**: 3-5 explicit non-goals (prevent scope creep)

8. **Define Maturity Milestones**:
   For each threshold (30%, 60%, 80%, 100%):
   - Status description
   - Concrete deliverables
   - What becomes possible at this maturity level

   Follow progressive complexity:
   - 30%: Experimental (proof of concept validated)
   - 60%: Tactical (usable in constrained production)
   - 80%: Production (reliable, well-documented)
   - 100%: Comprehensive (industry-leading)

9. **Establish Measurement Criteria**:
   - **Criteria**: 3-5 assessment methods (How do we assess current maturity?)
   - **Evidence**: 3-5 observable artifacts (What demonstrates progress?)
   - **Metrics**: 3-5 quantified thresholds with target/current/gap table

10. **Map Dependencies**:
    - **Prerequisites**: Capabilities that MUST exist before this can progress (with minimum maturity)
    - **Enables**: Capabilities that are UNLOCKED by this capability
    - Note: Circular dependency detection is performed by capability-checker in step 13

11. **Define Composition** (based on type):
    - **For Atomic**: List required outcomes with maturity contribution percentages
    - **For Composed**: List sub-capabilities with weights (should sum to 1.0 / 100%)
    - Note: Weight sum validation is performed by capability-checker in step 13

12. **Generate Complete Statement**:
    - Populate template with all gathered information
    - Populate actors array in capability_track.json
    - Save to `{capabilities.path}/[capability-id]/capability-statement.md`
    - Save to `{capabilities.path}/[capability-id]/capability_track.json`

13. **Validate with Capability Checker**:
    - Call the `capability-checker` subagent with the capability directory path
    - Review the TOON validation report returned
    - If `overallStatus: INVALID` - fix critical issues and re-run checker
    - If `overallStatus: NEEDS_ATTENTION` - review warnings with user, fix as needed
    - If `overallStatus: VALID` - proceed to completion
</process>

<validation>
After saving files, invoke the capability-checker subagent:

```
Task(
  subagent_type="capability-checker",
  prompt="Validate capability at {capabilities.path}/[capability-id]/"
)
```

The checker validates:
- Schema compliance and required fields
- Content completeness (all sections populated)
- No placeholder text (TBD, TODO)
- Cross-reference integrity (no circular dependencies)
- Spelling, grammar, and markdown formatting

**Handle validation results:**
- INVALID → Fix critical issues, re-run validation
- NEEDS_ATTENTION → Present warnings to user, fix if requested
- VALID → Capability creation complete
</validation>

<output>
Files created:
- `{capabilities.path}/[capability-id]/capability-statement.md` - Complete capability definition
- `{capabilities.path}/[capability-id]/capability_track.json` - Schema-compliant tracking file with actors

The files will follow the workspace template structure with all sections populated.
</output>

<output_format>
When returning capability creation results to the main conversation or as a subagent response, use TOON format:

**Capability Creation Result:**
```toon
@type: CreateAction
actionStatus: CompletedActionStatus
@id: authentication-system
result: Created capability with initial maturity 0%

filesCreated[2]: capability_track.json,capability-statement.md
crossRefsUpdated[1]: capability_summary.json
```

**Format Details:**
- `@type: CreateAction` - Artifact creation action
- `@id` - The capability ID that was created
- `result` - Human-readable summary of what was created
- `filesCreated[]` - Inline array of files created (no paths, just filenames)
- `crossRefsUpdated[]` - Inline array of summary/index files updated
- `actionStatus: CompletedActionStatus` - Always completed for successful creation

**Usage:**
- Use TOON when this command is invoked by a subagent
- Allows calling agent to parse results efficiently
- Provides structured confirmation of filesystem changes
- Keep detailed verification output in markdown for human users
</output_format>
