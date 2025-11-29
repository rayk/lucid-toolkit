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
Template reference: @templates/capability-statement-template.md
Schema validation: @schemas/capability_track_schema.json
Requirements guide: @research/capability/capability-requirements.md
Example reference: @research/capability/capability-example-complete.md
About capabilities: @research/capability/about-capability.md
</context>

<process>
1. **Gather Capability Identity**:
   - If $ARGUMENTS provided: Use as starting point for capability name/description
   - Otherwise: Ask user what capability they want to define
   - Generate capability ID following pattern: `^[a-z0-9]+(-[a-z0-9]+)*$`
   - Validate ID uniqueness against existing capabilities

2. **Capture Strategic Foundation**:
   - **Purpose**: What does this capability enable the system to DO? (action-oriented: "Enable the system to...")
   - **Type**: Atomic (built from outcomes) or Composed (built from sub-capabilities)?
   - **Domain**: Strategic category (e.g., "Data Security & Privacy", "Product Lifecycle")
   - **Target Maturity**: What percentage makes this "good enough"? (typically 60-100%)

3. **Identify Actor Involvement** (REQUIRED):
   - Load actors from `status/actor_summary.json`
   - Present actors organized by domain (Ownership & Governance, External Service & Professional, etc.)
   - User selects 1+ actors this capability involves/impacts
   - For each selected actor capture:
     - **Relationship type**: requires | provides | consumes | enables | governs
     - **Criticality**: essential | important | optional
     - **Description**: How the actor relates to this capability
   - Validate selected actor IDs exist in the registry

4. **Map Core Business Values** (REQUIRED):
   - Present the 34 core values framework
   - User selects 1-3 primary values this capability delivers
   - For each value:
     - Contribution percentage (must sum to ≤100%)
     - Rationale with measurable business impact
   - Optional: 0-2 secondary values with rationale

5. **Define Value Proposition**:
   - Risk Mitigation: Quantified security/compliance/reliability improvements
   - User Experience: Measurable UX improvements
   - Development Velocity: Time/effort savings for developers
   - Compliance: Standards/regulations met

6. **Establish Boundaries**:
   - **Included**: 3-5 specific responsibilities (what IS this capability?)
   - **Excluded**: 3-5 explicit non-goals (prevent scope creep)

7. **Define Maturity Milestones**:
   For each threshold (30%, 60%, 80%, 100%):
   - Status description
   - Concrete deliverables
   - What becomes possible at this maturity level

   Follow progressive complexity:
   - 30%: Experimental (proof of concept validated)
   - 60%: Tactical (usable in constrained production)
   - 80%: Production (reliable, well-documented)
   - 100%: Comprehensive (industry-leading)

8. **Establish Measurement Criteria**:
   - **Criteria**: 3-5 assessment methods (How do we assess current maturity?)
   - **Evidence**: 3-5 observable artifacts (What demonstrates progress?)
   - **Metrics**: 3-5 quantified thresholds with target/current/gap table

9. **Map Dependencies**:
   - **Prerequisites**: Capabilities that MUST exist before this can progress (with minimum maturity)
   - **Enables**: Capabilities that are UNLOCKED by this capability
   - **Validate for Circular Dependencies**: Before saving, detect cycles in prerequisite chains
     - For each prerequisite P specified for new capability C:
       - Load P's capability_track.json
       - Recursively trace P's prerequisites
       - If C is encountered in the chain, report cycle with full path
       - Algorithm: Use depth-first search with path tracking
       - Example cycle: "auth-system → user-management → role-based-access → auth-system"
     - Show clear error: "Circular dependency detected: [path]"
     - Prevent creation until cycle is resolved

10. **Define Composition** (based on type):
    - **For Atomic**: List required outcomes with maturity contribution percentages
    - **For Composed**: List sub-capabilities with weights (must sum to 1.0 / 100%)
      - Validate weights sum to 1.0 with tolerance of 0.001
      - If validation fails, show error with all weights and total
      - Example error: "Composition weights must sum to 1.0. Current weights: [0.25, 0.35, 0.20, 0.15] = 0.95"

11. **Generate Complete Statement**:
    - Populate template with all gathered information
    - Populate actors array in capability_track.json
    - **Validate no circular dependencies exist** (Step 9)
    - Validate against schema requirements
    - Check quality indicators (no placeholders, quantified values, measurable criteria)
    - Save to `capabilities/[capability-id]/capability-statement.md`
    - Save to `capabilities/[capability-id]/capability_track.json`
</process>

<success_criteria>
- Capability statement file created in correct location
- Capability tracking JSON file created with actors populated
- All required template sections completed (no "TBD" or empty sections)
- Capability ID follows naming pattern `^[a-z0-9]+(-[a-z0-9]+)*$`
- **Actor involvement includes 1+ actors with relationship type, criticality, and description**
- Core values mapping includes 1-3 primary values with rationale and contribution percentages
- Purpose statement uses action verbs ("Enable the system to...")
- All 4 maturity milestones (30/60/80/100%) have concrete deliverables
- Measurement section includes specific metrics with target values
- Scope includes both inclusions AND exclusions
- Dependencies clearly documented (if any)
- **No circular dependencies detected in prerequisite chain**
- Composition section matches capability type (atomic vs composed)
- Quality checklist at end shows all items verified
- Document validates against capability_track_schema.json structure
</success_criteria>

<output>
Files created:
- `capabilities/[capability-id]/capability-statement.md` - Complete capability definition
- `capabilities/[capability-id]/capability_track.json` - Schema-compliant tracking file with actors

The files will follow the workspace template structure with all sections populated.
</output>

<verification>
Before completing, verify:
- [ ] File saved to `capabilities/[capability-id]/capability-statement.md`
- [ ] File saved to `capabilities/[capability-id]/capability_track.json`
- [ ] **Actors array populated with 1+ actors (actorId, relationshipType, criticality, description)**
- [ ] Core values section has 1-3 primary values with measurable rationale
- [ ] All maturity milestones (30/60/80/100%) defined with concrete deliverables
- [ ] Measurement criteria include quantified metrics (numbers, percentages, thresholds)
- [ ] Scope includes both included AND excluded items
- [ ] **No circular dependencies exist in prerequisite chain**
- [ ] Composition section matches type (atomic=outcomes, composed=sub-capabilities)
- [ ] **For composed capabilities: composedOf weights sum to 1.0 (tolerance: 0.001)**
- [ ] No "TBD", "TODO", or placeholder text in completed sections
- [ ] Quality checklist at template end shows verification
- [ ] Document structure matches template exactly
</verification>

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

<34_core_values_reference>
When gathering core values mapping, present these 34 values organized by category:

**Technical Quality** (4):
- Dependability, Performance, Security, Maintainability

**Business & Strategic** (4):
- Efficiency, Scalability, Time-to-Market, User Experience (UX)

**Communication & Process** (3):
- Transparency, Interoperability, Compliance

**Revenue & Market** (3):
- Revenue Enablement, Market Differentiation, Customer Acquisition

**User & Stakeholder** (9):
- Convenience, Personalization, Trust & Confidence, Empowerment
- Responsiveness, Predictability, Control & Autonomy, Peace of Mind
- Accessibility

**Operational** (5):
- Flexibility, Resilience, Observability, Cost Optimization, Data Quality

**Learning & Growth** (2):
- Learnability, Discovery

**Social & Environmental** (4):
- Fairness & Equity, Community & Connection, Sustainability, Privacy

Each capability should map to 1-3 PRIMARY values (with contribution % and rationale).
</28_core_values_reference>

<actor_registry_reference>
When gathering actor involvement, load actors from `status/actor_summary.json` and present by domain:

**Ownership & Governance**:
- lot-owner, owners-corporation, strata-committee, office-bearer, resident-tenant, tenant-representative, voluntary-worker

**External Service & Professional**:
- building-manager, strata-manager, property-developer, insurer, insurance-broker, lawyer, building-consultant, quantity-surveyor, auditor, valuer, tradesperson

**Regulatory & Adjudicative**:
- ncat, vcat, qcat, bccm-office, nsw-fair-trading, consumer-affairs-victoria, local-council, whs-regulator

**Industry & Non-Government**:
- standards-australia

**Relationship Types** (from schema):
- `requires`: Actor needs this capability
- `provides`: Actor delivers this capability
- `consumes`: Actor uses this capability
- `enables`: Actor makes this capability possible
- `governs`: Actor regulates/oversees this capability

**Criticality Levels**:
- `essential`: Critical to actor's role
- `important`: Significant but not critical
- `optional`: Nice to have

Each capability MUST identify 1+ actors with relationship type, criticality, and description.
</actor_registry_reference>
