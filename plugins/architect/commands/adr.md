---
description: Create a new Architecture Decision Record (ADR) following LCA conventions. Captures context, options, and explicit trade-offs.
argument-hint: <decision-title>
allowed-tools:
  - Read
  - Write
  - Glob
  - Task
  - Skill
  - AskUserQuestion
---

<objective>
Create a new Architecture Decision Record that captures the context, considered options, and explicit trade-offs of an architectural decision. ADRs are append-only documents that preserve decision history.
</objective>

<phase_1_context>
**Gather decision context:**

If `$ARGUMENTS` provided, use as decision title seed.

Use AskUserQuestion to gather context:

Question 1: "What type of architectural decision is this?"

Options:
1. **Boundary decision** - Where Conduits go, API versioning, protocols
2. **Composition decision** - How to decompose, what orchestrates what
3. **Data strategy decision** - Schema.org types, internal models, mapping
4. **Technology choice** - Library, framework, or tool selection
5. **Performance decision** - When to optimize, what approach
6. **Other** - Describe the decision type

Question 2: "What problem or situation triggered this decision?"

(Free text input expected)
</phase_1_context>

<phase_2_numbering>
**Determine ADR number:**

1. Search for existing ADRs:
   ```
   Glob: **/adr/adr-*.md
   Glob: **/adr-*.md
   ```

2. Extract highest number from filenames

3. Increment for new ADR:
   - If none exist: `001`
   - If highest is `005`: `006`
   - Always 3-digit format with leading zeros

4. Generate slug from title:
   - Lowercase
   - Replace spaces with hyphens
   - Remove special characters
   - Max 50 characters

Example: "Use Protocol Buffers for Service Communication" → `use-protocol-buffers-for-service-communication`

Final filename: `adr-{NNN}-{slug}.md`
</phase_2_numbering>

<phase_3_options>
**Gather considered options:**

Ask user: "What options have you considered? (I'll help analyze trade-offs)"

Minimum 2 options required. For each option, gather:
- Name/description
- Key advantages
- Key disadvantages

If user provides only one option, prompt:
"LCA requires documenting alternatives. What other approaches were considered, even if rejected early?"
</phase_3_options>

<phase_4_drivers>
**Identify decision drivers:**

Based on decision type, suggest relevant drivers:

**Boundary decisions:**
- Deployment independence
- Version compatibility
- Protocol standardization
- Team ownership boundaries

**Composition decisions:**
- Testability requirements
- Reusability needs
- Dependency management
- Change isolation

**Data decisions:**
- AI/LLM interoperability
- External consumer needs
- Internal optimization
- Schema evolution

**Technology decisions:**
- Team expertise
- Community support
- Performance characteristics
- Licensing/cost

**Performance decisions:**
- Profiling evidence
- Latency requirements
- Throughput needs
- Resource constraints

Ask user to confirm or modify drivers for their specific case.
</phase_4_drivers>

<phase_5_draft>
**Generate ADR draft:**

Use Task tool with adr-writer agent:

```
Create ADR for:
Title: {title}
Type: {decision type}
Context: {problem statement}
Options: {list of options with pros/cons}
Drivers: {prioritized list}
Next number: {NNN}

Follow LCA ADR conventions. Ensure negative consequences are specific.
```

Present draft to user for review.
</phase_5_draft>

<phase_6_save>
**Confirm and save:**

Present the draft ADR and ask:

"Here's the draft ADR. Where should I save it?"

Options:
1. **Project root** - Save to `./adr/adr-{NNN}-{slug}.md`
2. **Architecture docs** - Save alongside ARCHITECTURE.md
3. **Custom location** - Specify path
4. **Edit first** - Let me modify before saving

After saving:
- Create `adr/` directory if needed
- Update ADR index if it exists
- Suggest linking from ARCHITECTURE.md
</phase_6_save>

<phase_7_validate>
**Post-creation validation (using adr-curator):**

After saving the ADR, run validation:

1. Use Task tool with `adr-curator` agent:
   ```
   Validate the newly created ADR at {path}.
   Run adr-audit.py on the adr directory.
   Fix any issues found (stale dates, missing sections, cross-refs).
   Update README index if it exists.
   ```

2. Curator will:
   - Run `adr-audit.py` to detect issues
   - Auto-fix mechanical issues (review dates, formatting)
   - Report any issues requiring user input

3. If superseding another ADR:
   - Curator verifies bidirectional references
   - Old ADR updated with "Superseded by ADR-{NNN}"
   - New ADR has "Supersedes ADR-{XXX}"
</phase_7_validate>

<success_criteria>
- ADR follows LCA template structure
- Context explains WHY the decision is needed
- At least 2 options documented
- Both positive AND negative consequences explicit
- Proper numbering (no gaps, no duplicates)
- Saved to appropriate location
- User informed about linking to ARCHITECTURE.md
- **Validation passed** (adr-curator reports clean)
- **README updated** (if index exists)
- **Cross-references bidirectional** (if superseding)
</success_criteria>
