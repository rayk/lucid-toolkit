---
description: Create a new outcome with proper structure, schema validation, capability linkage, and project association
argument-hint: [outcome-name or description]
---

<objective>
Create a new outcome based on $ARGUMENTS following workspace schema and conventions.

Outcomes are units of tactical work that BUILD capabilities. Each outcome:
- Describes WHAT to achieve (not HOW to implement)
- Specifies observable effects (behavioral changes proving completion)
- Links to capabilities with maturity contribution percentages
- **Links to at least one project** from project_map.json
- Starts in `queued` state in `outcomes/0-queued/` directory
</objective>

<delegation_mandate>
CRITICAL: This workflow requires 10+ tool operations. You MUST delegate.

Phase 1 (Main Context - 0-2 tools max):
- Parse $ARGUMENTS to extract outcome intent
- If critical info missing, use AskUserQuestion (1 tool)
- Then IMMEDIATELY delegate Phase 2

Phase 2 (Delegated via Task tool):
- ALL file operations happen in subagent
- Token budget: 3000 (sonnet model)
- Return format: JSON with created files list

DO NOT read schemas, project_map, or any files in main context.
The subagent has access to all files and will handle validation.
</delegation_mandate>

<context>
Existing outcomes: !`find outcomes/0-queued outcomes/1-ready outcomes/2-in-progress outcomes/3-blocked outcomes/4-completed -maxdepth 1 -mindepth 1 -type d -exec basename {} \; 2>/dev/null | sort`
Available capabilities: !`find capabilities -name "capability_track.json" -exec dirname {} \; 2>/dev/null | xargs -I{} basename {}`
Available projects: !`jq -r '.projects[].name' project_map.json 2>/dev/null || echo "No project_map.json found"`
Next outcome number: !`find outcomes -type d -name "[0-9]*-*" 2>/dev/null | xargs -I{} basename {} | grep -oE "^[0-9]+" | sort -n | tail -1 | xargs -I{} expr {} + 1 | xargs printf "%03d"`
</context>

<phase1_main_context>
Parse $ARGUMENTS and determine if you have enough information:

Required information (infer from $ARGUMENTS or ask):
- Outcome name (generate from description if not explicit)
- Achievement description (WHAT to accomplish)
- Primary project (which project from Available projects list)
- Primary capability (which capability from Available capabilities list)

If $ARGUMENTS provides clear intent → proceed directly to delegation
If $ARGUMENTS is ambiguous → use AskUserQuestion ONCE to clarify, then delegate

Example sufficient input:
"Neo4J sync for luon project ontology tracking"
→ Name: ontology-sync, Project: luon, Capability: infer from context

Example insufficient input:
"make something better"
→ Ask: What should be achieved? Which project? Which capability?
</phase1_main_context>

<phase2_delegation>
After Phase 1, delegate with this Task call:

```
Task(general-purpose, sonnet):

Create outcome {NUMBER}-{NAME} in outcomes/0-queued/ with these specifications:

**Token Budget:** Target 3000 tokens for response.

**Outcome Details:**
- Name: {extracted name}
- Description: {extracted description}
- Purpose: {inferred or provided}
- Primary Project: {project name} (involvement: primary)
- Primary Capability: {capability id}
- Maturity Contribution: {estimate 5-20% based on scope}

**Required Actions:**
1. Read schema at schemas/outcome_track_schema.json
2. Read project_map.json to get project details and affected modules
3. Create directory: outcomes/0-queued/{NUMBER}-{NAME}/
4. If creating child, nest under parent: outcomes/0-queued/{PARENT_NUMBER}-{PARENT_NAME}/{NUMBER}.{X}-{NAME}/
   - For children: set `capabilityContributions: []` and `parentContribution: <percentage>` (ask user for %)
   - Children contribute to PARENT, not directly to capability
5. Create subdirectories: reports/, evidence/
6. Generate outcome_track.json following schema exactly (state: "queued")
7. Generate outcome-statement.md with Given-When-Then effects
8. Update capability's builtByOutcomes array
9. Update outcome_summary.json with new entry
10. If outcome has dependencies, update dependent outcome's outcomeDependencies

**Return Format (TOON):**
```toon
@type: CreateAction
actionStatus: CompletedActionStatus
@id: NNN-outcome-name
result: Created [outcome-name] for [primary-project]

filesCreated[2]: outcome_track.json,outcome-statement.md
crossRefsUpdated[2]: capability_track.json,outcome_summary.json
```
</phase2_delegation>

<process>
1. **Parse user input** from $ARGUMENTS to understand desired outcome
2. **Determine next sequence number** (3-digit zero-padded, e.g., 001, 002)
3. **Generate outcome name** following pattern `^[a-z0-9]+(-[a-z0-9]+){0,4}$`
4. **Gather required information** by asking user if not provided:
   - Achievement description (WHAT to accomplish, not HOW)
   - Purpose (why this outcome is needed)
   - At least 2 observable effects in Given-When-Then format with actor perspectives
   - Primary capability contribution (capabilityId, maturityContribution %, rationale)
   - **At least one project** (projectName from project_map.json, involvement: primary/secondary/integration, affectedAreas, rationale)
   - At least one actor involvement (beneficiary, stakeholder, contributor, approver, or informed)
   - Token budget estimate (very-low <25K, low 25-75K, average 75-150K, high 150-200K)

5. **DELEGATE** all file operations to Task(general-purpose) - see <phase2_delegation>
</process>

<validation>
Before creating, verify:
- [ ] Outcome name matches pattern `^[a-z0-9]+(-[a-z0-9]+){0,4}$`
- [ ] Directory label matches pattern `^[0-9]+-[a-z0-9]+(-[a-z0-9]+){0,4}$`
- [ ] At least 2 observable effects defined
- [ ] At least 1 capability contribution with valid path
- [ ] **At least 1 project** with valid projectName from project_map.json
- [ ] At least 1 actor involvement specified
- [ ] Achievement description is outcome-focused (no process prescriptions)
- [ ] Token budget within acceptable range (recommend split if >200K)
</validation>

<anti_patterns>
Reject outcomes that contain:
- Process prescriptions: "Use TDD", "Follow agile", "Implement with X library"
- Implementation artifacts as effects: "Tests pass", "File created", "Code reviewed"
- Vague achievements: "Improve", "Enhance", "Optimize" (without quantification)
- Capability dependencies (outcomes BUILD capabilities, don't depend on them)
</anti_patterns>

<output>
Files created:
- `outcomes/0-queued/{NNN}-{name}/outcome_track.json` - Machine-readable tracking
- `outcomes/0-queued/{NNN}-{name}/outcome-statement.md` - Human-readable definition
- `outcomes/0-queued/{NNN}-{name}/reports/` - Directory for execution reports
- `outcomes/0-queued/{NNN}-{name}/evidence/` - Directory for verification evidence

For child outcomes:
- `outcomes/0-queued/{PARENT}-{name}/{NNN}.{X}-{child-name}/` - Nested under parent directory
</output>

<output_format>
## TOON Format (Subagent Returns)

When delegating outcome creation to a subagent:

```toon
@type: CreateAction
actionStatus: CompletedActionStatus
@id: 005-ontology-sync
result: Created ontology sync outcome for Neo4J integration

filesCreated[2]: outcome_track.json,outcome-statement.md
crossRefsUpdated[2]: capability_track.json,outcome_summary.json
```

**Fields:**
- `@type`: CreateAction (artifact creation)
- `actionStatus`: CompletedActionStatus if successful
- `@id`: outcome directory label
- `result`: Summary of what was created
- `filesCreated[N]`: Inline array of files created
- `crossRefsUpdated[N]`: Inline array of tracking files updated
</output_format>

<success_criteria>
- Outcome directory created in `outcomes/0-queued/` (or nested under parent if child)
- `outcome_track.json` validates against schema with state="queued"
- `outcome-statement.md` follows template structure
- Capability reference updated with new outcome path
- **Project linkage** established with valid project from project_map.json
- No schema validation errors
- Achievement description is behavioral (not implementation-focused)
- If child outcome, properly nested under parent directory
</success_criteria>

<project_involvement_types>
**primary** - Main project where the outcome's work is implemented
**secondary** - Project affected but not the main focus
**integration** - Project involved for integration/compatibility purposes
</project_involvement_types>

<parent_child_contribution_model>
**For child outcomes (when parentOutcome is specified):**
- Set `capabilityContributions: []` (empty - children don't contribute directly to capabilities)
- Set `parentContribution: <percentage>` (what % of parent's work this child represents)
- All children of a parent must have parentContribution values that sum to 100%
- Capability maturity updates ONLY when parent completes (all children done)
- Do NOT add child paths to capability's builtByOutcomes - only parent path

**For standalone/parent outcomes:**
- Set `capabilityContributions` with capability paths and maturity percentages
- Set `parentContribution: null` (they don't contribute to another outcome)
- Add path to capability's builtByOutcomes array
</parent_child_contribution_model>