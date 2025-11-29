---
description: Create or update design documents (solution + implementation) for an outcome
argument-hint: <outcome-directory-label> [description text to drive design]
---

<objective>
Create or update a `design/` directory within an outcome containing solution design and implementation specification documents.

This command is **idempotent** - safe to run multiple times:
1. First run: Creates new design documents from inference
2. Subsequent runs: Reads existing documents, preserves manual edits, merges new information
3. Always ensures solution-design.md and implementation-design.md are aligned

**Key behaviors:**
- Preserves manual edits made to existing design documents
- Merges new description text with existing content
- Detects and resolves misalignments between solution and implementation docs
- Bumps version number on updates (1.0.0 → 1.1.0 → 1.2.0)
</objective>

<context>
Solution template: @templates/design/solution_design.md
Implementation template: @templates/design/implementation_design.md
</context>

<argument_parsing>
Parse $ARGUMENTS to extract:
- **outcome-directory-label**: First argument (e.g., `001-jwt-authentication`)
- **description-text**: Everything after the first argument - freeform text describing implementation intent, technical approach, or design considerations

Example invocations:
- `/outcome:design 001-jwt-authentication` - Create new or refresh existing
- `/outcome:design 001-jwt-authentication Use FastAPI with Pydantic models` - Create/update with new context
- `/outcome:design 001-jwt-authentication Add Redis caching layer` - Update existing with new requirement
</argument_parsing>

<process>

## Phase 1: Load All Context

1. **Locate outcome directory**:
   - Extract outcome-directory-label from $ARGUMENTS (first token)
   - Search in `outcomes/0-queued/`, `outcomes/1-ready/`, `outcomes/2-in-progress/`, `outcomes/3-blocked/`
   - If not found, report error and exit
   - Note: If parent outcome has children, all children need designs before parent can advance to 1-ready

2. **Detect existing design documents**:
   - Check if `design/` directory exists
   - If exists, read `design/solution-design.md` and `design/implementation-design.md`
   - Extract current version numbers from existing documents
   - **Set mode**: `CREATE` (no existing docs) or `UPDATE` (existing docs found)

3. **Read ALL outcome documents**:
   - `outcome_track.json` - Core outcome definition
   - `outcome-statement.md` - Human-readable outcome description
   - Any existing files in `reports/` or `evidence/` directories

4. **Parse user description text**:
   - Extract everything after outcome-directory-label as description
   - Identify: technologies mentioned, patterns suggested, constraints stated
   - This description AUGMENTS (not replaces) existing content

5. **Extract structured context** from outcome_track.json:
   ```
   - outcome.name, outcome.description, outcome.purpose
   - outcome.scope.included[], outcome.scope.excluded[]
   - outcome.observableEffects[] (Given-When-Then statements)
   - outcome.rationale.problemStatement
   - outcome.rationale.alternativesConsidered[]
   - outcome.rationale.constraints[]
   - outcome.rationale.risks[]
   - outcome.effort.complexityIndicators
   - outcome.capabilityContributions[]
   ```

## Phase 2: Determine Operation Mode

6. **If CREATE mode** (no existing design/):
   - Proceed to Phase 3 (Infer from scratch)
   - Will create new documents at version 1.0.0

7. **If UPDATE mode** (existing design/ found):
   - Parse existing solution-design.md into structured sections
   - Parse existing implementation-design.md into structured sections
   - Identify what user has manually edited (compare against template structure)
   - Mark manually-edited sections as PRESERVE
   - Proceed to Phase 3 with existing content as baseline

## Phase 3: Infer/Merge Design Content

8. **Auto-detect domain profile** from context signals:

   | Signal | Inferred Profile |
   |--------|------------------|
   | "API", "endpoint", "REST", "GraphQL" | REST API / Web Service |
   | "ETL", "pipeline", "transform", "sync" | Data Pipeline / ETL |
   | "model", "training", "inference", "ML" | ML/AI Service |
   | "GPIO", "sensor", "device", "firmware" | IoT / Hardware |
   | "UI", "component", "React", "frontend" | Mobile / Frontend |
   | "trading", "ledger", "transaction" | Finance / Trading |
   | "HIPAA", "patient", "clinical" | Healthcare |
   | "deploy", "infrastructure", "k8s" | Platform / Infra |
   | "video", "audio", "stream", "codec" | Media / Streaming |
   | "coordinates", "map", "location" | Geospatial |
   | None of above | Simple Utility/Script |

   In UPDATE mode: Preserve existing profile unless user description strongly suggests change

9. **For each design section**, apply merge strategy:

   **CREATE mode:**
   - Infer content from outcome context + user description

   **UPDATE mode:**
   - If section marked PRESERVE: Keep existing content, append new info if relevant
   - If section has placeholder text: Replace with inferred content
   - If section empty: Fill with inferred content
   - If user description mentions section topic: Merge new info into existing

10. **Solution Design sections to process:**
    - Problem Statement (from outcome.rationale.problemStatement)
    - Alternative Solutions (from outcome.rationale.alternativesConsidered)
    - Architecture (infer from scope + user description)
    - Public Interface (from observableEffects + user description)
    - Data Flow (trace from observable effects)
    - Success Criteria (from observableEffects)
    - Domain-Specific Sections (based on profile)
    - Key Design Decisions (from alternatives + constraints)

11. **Implementation sections to process:**
    - Technical Overview (from outcome + user description)
    - Module Structure (from user description + profile conventions)
    - Component Specifications (from scope + observable effects)
    - Dependencies (from user description + profile)
    - Requirement Traceability (map scope → components → tests)
    - Domain-Specific Sections (based on profile)

## Phase 4: Alignment Check

12. **Cross-reference solution and implementation documents**:

    | Solution Section | Must Align With Implementation |
    |------------------|-------------------------------|
    | Architecture components | Module Structure files |
    | Public Interface | Component Specifications signatures |
    | Data Flow steps | Module responsibilities |
    | Success Criteria | Requirement Traceability tests |
    | Key Design Decisions | Dependencies + Component choices |

13. **Detect misalignments**:
    - Component in architecture but no corresponding file in module structure
    - File in module structure not referenced in architecture
    - Interface in solution not matching function signatures in implementation
    - Success criteria with no corresponding test mapping
    - Dependency mentioned in solution but not in implementation dependencies

14. **Generate alignment report**:
    ```markdown
    ## Alignment Check

    ### Aligned ✓
    - [list of aligned items]

    ### Misalignments Found ⚠
    - [item]: Solution says X, Implementation says Y
    - [item]: Present in Solution, missing from Implementation
    - [item]: Present in Implementation, missing from Solution

    ### Recommended Fixes
    - [specific fix for each misalignment]
    ```

15. **Resolve misalignments**:
    - For each misalignment, determine authoritative source:
      - If solution has more detail → Update implementation
      - If implementation has more detail → Update solution
      - If conflicting → Present to user for decision
    - Apply fixes to maintain consistency

## Phase 5: Present Changes for Confirmation

16. **Present summary based on mode**:

    **CREATE mode:**
    ```markdown
    ## New Design for: [outcome-name]

    **Detected Profile**: [profile] (based on: [signals])

    ### Solution Design Summary
    - **Problem**: [inferred problem]
    - **Selected Approach**: [inferred solution]
    - **Key Components**: [list]

    ### Implementation Summary
    - **Files to Create**: [count] files
    - **Key Classes**: [list]
    - **Dependencies**: [list]

    ### Alignment Status: ✓ Clean (new documents)

    **Proceed with creation?**
    ```

    **UPDATE mode:**
    ```markdown
    ## Design Update for: [outcome-name]

    **Current Version**: [X.Y.0] → **New Version**: [X.Y+1.0]

    ### Preserved Sections (manual edits kept)
    - [list of sections not modified]

    ### Updated Sections
    - [section]: [what changed]

    ### New Content Added
    - [from user description]: [what was added]

    ### Alignment Status
    [alignment report from Phase 4]

    ### Alignment Fixes Applied
    - [list of fixes]

    **Proceed with update?**
    ```

17. **Collect user feedback**:
    - If user approves: proceed to generation
    - If user provides corrections: update and re-present
    - If user rejects alignment fix: mark as intentional divergence

## Phase 6: Generate/Update Documents

18. **Ensure design directory exists**:
    ```
    outcomes/[state]/[outcome-directory-label]/
    └── design/
        ├── solution-design.md
        └── implementation-design.md
    ```

19. **Generate/Update solution-design.md**:
    - Use template structure from @templates/design/solution_design.md
    - In UPDATE mode: Preserve manually-edited sections
    - Include ONLY sections for detected profile
    - Set version: CREATE → 1.0.0, UPDATE → increment minor version
    - Set status: Draft (or preserve existing status)
    - Update "Last Modified" timestamp

20. **Generate/Update implementation-design.md**:
    - Use template structure from @templates/design/implementation_design.md
    - In UPDATE mode: Preserve manually-edited sections
    - Include ONLY sections for detected profile
    - Match version number with solution-design.md
    - Link back to solution design

21. **Final alignment verification**:
    - Re-run alignment check on generated documents
    - If new misalignments introduced: fix before completing
    - Log alignment status in document footer

22. **Cross-link documents**:
    - Solution design → Implementation link
    - Implementation → Solution design link
    - Both → outcome_track.json reference
    - Add alignment verification timestamp

</process>

<idempotency_rules>

**Safe to re-run because:**

1. **Existing content detection** - Reads before writing
2. **Manual edit preservation** - Sections with non-template content are marked PRESERVE
3. **Merge not replace** - New description augments, doesn't overwrite
4. **Version tracking** - Each update increments version
5. **Alignment enforcement** - Always checks and fixes cross-document consistency

**How manual edits are detected:**
- Compare section content against template placeholders
- If content differs from `{{PLACEHOLDER}}` pattern → user edited
- If content matches inferred default exactly → safe to update
- If content has been expanded/modified → preserve and merge

**Version bump rules:**
- CREATE: 1.0.0
- UPDATE with content changes: increment minor (1.0.0 → 1.1.0)
- UPDATE with alignment fixes only: increment patch (1.1.0 → 1.1.1)
- Major version: reserved for profile change or major restructure

</idempotency_rules>

<alignment_rules>

**Documents must stay aligned on:**

1. **Components** - Every architecture component has a corresponding module/file
2. **Interfaces** - Public interface matches implementation signatures
3. **Data Flow** - Steps trace through actual modules
4. **Success Criteria** - Each criterion has a test in traceability matrix
5. **Dependencies** - All mentioned in both or neither
6. **Profile** - Same domain profile in both documents

**Alignment check runs:**
- Before presenting changes (Phase 4)
- After generating documents (Phase 6, step 21)
- Reports any remaining divergences in document footer

**Intentional divergence:**
- User can mark specific misalignments as "intentional"
- These are logged but not auto-fixed on subsequent runs
- Stored in document metadata section

</alignment_rules>

<inference_principles>

**Maximize inference, minimize questions:**

1. **Extract before asking** - Mine all available documents first
2. **User description augments** - Adds to existing, doesn't replace
3. **Preserve manual work** - Never discard user edits
4. **Pattern matching** - Use domain conventions to fill gaps
5. **Confidence scoring** - Know what you're sure about vs. guessing
6. **Batch confirmation** - Present everything at once, don't drip questions

**Information hierarchy (most to least authoritative):**
1. Existing document content (manual edits)
2. User's description text in $ARGUMENTS
3. outcome_track.json structured data
4. outcome-statement.md prose
5. Domain profile conventions
6. General software patterns

</inference_principles>

<success_criteria>
- Command is idempotent (safe to run multiple times)
- Existing manual edits are preserved
- New description text is merged appropriately
- Version number incremented on updates
- Solution and implementation documents are aligned
- Alignment report generated and issues resolved
- No {{PLACEHOLDER}} text in final documents
- Documents properly cross-linked
- Only profile-relevant sections included
</success_criteria>

<output>
**CREATE mode:**
- `outcomes/[state]/[outcome-directory-label]/design/solution-design.md` (v1.0.0)
- `outcomes/[state]/[outcome-directory-label]/design/implementation-design.md` (v1.0.0)

**UPDATE mode:**
- Updated `solution-design.md` (version incremented)
- Updated `implementation-design.md` (version incremented)
- Preserved sections marked in document
- Alignment fixes applied
</output>

<output_format>
## TOON Format (Subagent Returns)

For design document creation/update:

**CREATE mode:**
```toon
@type: CreateAction
actionStatus: CompletedActionStatus
@id: 001-jwt-authentication
result: Created design documents v1.0.0

filesCreated[2]: solution-design.md,implementation-design.md
x-profile: REST API / Web Service
x-alignmentStatus: clean
```

**UPDATE mode:**
```toon
@type: UpdateAction
actionStatus: CompletedActionStatus
@id: 001-jwt-authentication
result: Updated design documents to v1.1.0

filesUpdated[2]: solution-design.md,implementation-design.md
preservedSections[3]: Architecture,Public Interface,Dependencies
updatedSections[2]: Technical Overview,Module Structure
x-alignmentIssues: 2
x-alignmentFixed: 2
```

**Fields:**
- `@type`: CreateAction (new) or UpdateAction (update)
- `actionStatus`: CompletedActionStatus if successful
- `@id`: outcome directory label
- `result`: Summary with version
- `filesCreated[N]` or `filesUpdated[N]`: Inline array of design files
- `preservedSections[N]`: Sections with manual edits kept (UPDATE only)
- `updatedSections[N]`: Sections modified (UPDATE only)
- `x-profile`: Detected domain profile
- `x-alignmentStatus`: clean or issues-found
- `x-alignmentIssues`: Count of misalignments found
- `x-alignmentFixed`: Count of fixes applied
</output_format>

<verification>
Before completing, verify:
- [ ] Checked for existing design/ directory
- [ ] Mode determined (CREATE or UPDATE)
- [ ] outcome_track.json was read
- [ ] Existing documents parsed (if UPDATE mode)
- [ ] Manual edits identified and marked for preservation
- [ ] Domain profile detected/preserved
- [ ] Alignment check performed
- [ ] Misalignments resolved or marked intentional
- [ ] Changes presented to user
- [ ] User confirmed proceed
- [ ] Documents generated/updated
- [ ] Final alignment verification passed
- [ ] Version numbers match between documents
- [ ] Cross-links in place
</verification>
