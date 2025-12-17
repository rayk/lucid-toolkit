---
document: Technical Specification Template Guide
version: 1.0.0
created: 2025-12-17
classification: documentation
status: approved
---

# Technical Specification Template Guide

This guide explains the fields in `technical-specification.toon` and how to use them effectively when creating technical specifications.

## Purpose

The template provides a structured format for technical specifications that:

1. **Ensures completeness** - All critical sections are prompted
2. **Enables LLM comprehension** - Structure optimized for AI-assisted development
3. **Supports parallel implementation** - Dependency graphs enable concurrent work
4. **Facilitates validation** - Acceptance criteria and testable contracts enable verification

---

## Field Reference

### Document Metadata

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `@context` | URI | Yes | Schema vocabulary (always `https://schema.org`) |
| `@type` | String | Yes | Schema type (use `TechArticle` for specifications) |
| `@id` | String | Yes | Unique identifier (format: `spec/{name}`) |
| `dateCreated` | Date | Yes | Initial creation date (ISO 8601) |
| `dateModified` | Date | Yes | Last modification date (ISO 8601) |
| `version` | String | Yes | Semantic version (e.g., `1.0.0`) |

**document.*** fields:

| Field | Required | Description |
|-------|----------|-------------|
| `document.name` | Yes | Human-readable title |
| `document.description` | Yes | One-line summary (used in indexes) |
| `document.classification` | Yes | Document type category |
| `document.status` | Yes | Lifecycle state |

**Classification Values:**
- `technical-specification` - Implementation details for a system component
- `design-specification` - High-level design without implementation details
- `api-specification` - External interface contracts (OpenAPI, etc.)
- `integration-specification` - How systems connect

**Status Values:**
- `draft` - Work in progress, not ready for review
- `review` - Ready for stakeholder feedback
- `approved` - Accepted, ready for implementation
- `deprecated` - Superseded but still referenced
- `superseded` - Replaced, use successor document

**Why needed:** Metadata enables document discovery, version tracking, and lifecycle management. LLMs use this to understand document authority and currency.

---

### Document Relationships

| Field | Required | Description |
|-------|----------|-------------|
| `companionAdr.name` | No | Title of related Architecture Decision Record |
| `companionAdr.url` | No | Relative path to ADR |
| `supersedes.itemListElement[]` | No | Paths to documents this replaces |
| `integrations.itemListElement[].name` | No | Related document title |
| `integrations.itemListElement[].url` | No | Relative path |
| `integrations.itemListElement[].purpose` | No | Why the integration exists |

**Why needed:** Specifications don't exist in isolation. Relationships enable:
- Tracing decisions (ADR) to implementations (spec)
- Understanding what this spec replaces (migration context)
- Finding related specifications (system coherence)

---

### Acceptance Criteria

| Field | Required | Description |
|-------|----------|-------------|
| `acceptanceCriteria.numberOfItems` | Yes | Total count of criteria |
| `item[N].identifier` | Yes | Unique ID (format: `AC-{N}`) |
| `item[N].name` | Yes | Short descriptive name |
| `item[N].description` | Yes | What must be true to pass |
| `item[N].status` | Yes | Current evaluation state |
| `item[N].verificationMethod` | Yes | How to verify (link to evidence) |
| `item[N].notes` | No | Additional context |

**Status Values:**
- `PASS` - Criterion fully satisfied
- `PARTIAL` - Partially satisfied, with documented gaps
- `FAIL` - Not satisfied
- `PENDING` - Not yet evaluated

**Why needed:** Acceptance criteria define "done." They:
- Prevent scope creep (if it's not a criterion, it's not required)
- Enable objective review (pass/fail, not opinion)
- Create traceability to evidence (proof it works)

**Best Practice:** Write criteria as testable assertions. Bad: "System should be fast." Good: "Response time < 100ms for 95th percentile."

---

### Scope Boundaries

| Field | Required | Description |
|-------|----------|-------------|
| `scope.inScope[]` | Yes | What this specification covers |
| `scope.outOfScope[]` | Yes | What this specification explicitly excludes |

**Why needed:** Scope boundaries prevent:
- **Scope creep** during implementation
- **Confusion** about what belongs here vs. elsewhere
- **Gold-plating** (adding features not required)

**Best Practice:** Be explicit about exclusions. If something seems related but isn't covered, list it in `outOfScope` with brief rationale.

---

### Document Navigation

| Field | Required | Description |
|-------|----------|-------------|
| `navigation.byTask[].task` | Yes | User intent (e.g., "Add widget with semantic key") |
| `navigation.byTask[].section` | Yes | Anchor link to relevant section |
| `navigation.byComponent[].component` | Yes | Component name |
| `navigation.byComponent[].section` | Yes | Anchor link |
| `navigation.byAudience[].audience` | Yes | Reader role |
| `navigation.byAudience[].startSection` | Yes | Where this audience should start |

**Audience Values:**
- `code-generator` - LLMs generating code (Claude Code, Copilot)
- `human-reader` - Developers understanding the system
- `implementer` - Developers building this specification
- `reviewer` - People validating the specification
- `architect` - People ensuring principle compliance

**Why needed:** Navigation enables **single-hop lookup**. An LLM should go from query to answer in one step, not by scanning the entire document. This is critical for:
- Context efficiency (LLMs have limited context windows)
- Response accuracy (less searching = less confusion)
- Task completion speed

**Best Practice:** Add navigation entries for every task users commonly perform. Test by asking: "If I want to X, can I find it in one lookup?"

---

### Problem Statement

| Field | Required | Description |
|-------|----------|-------------|
| `problem.name` | Yes | Problem title |
| `problem.description` | Yes | What problem this solves |
| `problem.currentState.itemListElement[].system` | Yes | System/component affected |
| `problem.currentState.itemListElement[].purpose` | Yes | What the system does |
| `problem.currentState.itemListElement[].issue` | Yes | What's wrong |
| `problem.impact[]` | Yes | Consequences of not solving |

**Why needed:** Problem statements justify the specification's existence. They:
- **Prevent solutions seeking problems** - If you can't articulate the problem, maybe there isn't one
- **Enable impact assessment** - Stakeholders can evaluate if the problem is worth solving
- **Guide solution design** - Solutions should address stated problems, nothing more

**Best Practice:** Quantify impact where possible. "Tests fail silently" is weaker than "30% of test failures go undetected until production."

---

### Solution Overview

| Field | Required | Description |
|-------|----------|-------------|
| `solution.name` | Yes | Solution title |
| `solution.description` | Yes | One-paragraph summary |
| `solution.capabilities.itemListElement[]` | Yes | What the solution provides |

**Why needed:** The solution overview provides:
- **Quick comprehension** - Readers understand the approach before diving into details
- **Scope alignment** - Capabilities should map to problems
- **Evaluation criteria** - Does the solution deliver these capabilities?

**Best Practice:** Each capability should trace to a problem statement item. If a capability doesn't address a stated problem, question whether it belongs.

---

### Evidence

| Field | Required | Description |
|-------|----------|-------------|
| `evidence.numberOfItems` | Yes | Total evidence count |
| `item[N].identifier` | Yes | Unique ID (format: `E-{N}`) |
| `item[N].name` | Yes | Evidence title |
| `item[N].problemDemonstrated` | Yes | Which problem this proves |
| `item[N].beforePattern` | Yes | Code/behavior showing problem |
| `item[N].afterPattern` | Yes | Code/behavior showing solution |
| `item[N].verification` | Yes | How to reproduce/verify |

**Why needed:** Evidence proves claims. Without evidence:
- Problems might be theoretical, not real
- Solutions might not actually work
- Reviewers must trust rather than verify

**Best Practice:** Include runnable examples. "Before" should fail visibly; "after" should succeed. Link evidence IDs to acceptance criteria verification methods.

---

### Principle Compliance

| Field | Required | Description |
|-------|----------|-------------|
| `item[].specSection` | Yes | Section anchor |
| `item[].principle` | Yes | Principle ID and name |
| `item[].status` | Yes | Compliance state |
| `item[].notes` | No | Compliance notes or exception justification |

**Status Values:**
- `COMPLIANT` - Fully adheres to principle
- `PARTIAL` - Adheres with documented limitations
- `EXCEPTION` - Intentionally deviates (must justify)

**Why needed:** Specifications must align with architectural principles. The compliance matrix:
- **Prevents architectural drift** - Specs can't ignore principles
- **Documents exceptions** - When deviation is necessary, it's explicit
- **Enables auditing** - Reviewers can check compliance systematically

**Best Practice:** If a principle seems irrelevant, still list it with status `COMPLIANT` and note "Not applicable - [reason]." This proves you considered it.

---

### Component Summary

| Field | Required | Description |
|-------|----------|-------------|
| `components.numberOfItems` | Yes | Total component count |
| `item[].name` | Yes | Component name |
| `item[].responsibility` | Yes | Single sentence - what it does |
| `item[].publicInterface` | Yes | Methods/properties exposed |
| `item[].dependencies` | Yes | Other components required |
| `item[].specSection` | Yes | Detailed section anchor |

**Why needed:** The component summary enables:
- **Quick orientation** - What are all the pieces?
- **Implementation planning** - What depends on what?
- **Work distribution** - Different people can work on different components

**Best Practice:**
- Responsibilities must be one sentence. If you need more, the component is too complex.
- List actual method names in `publicInterface`, not vague descriptions.
- `dependencies` should name other components from this spec, not external libraries.

---

### Component Dependencies

| Field | Required | Description |
|-------|----------|-------------|
| `dependencies.leafNodes[]` | Yes | Components with no dependencies (start here) |
| `dependencies.requires[].component` | Yes | Component name |
| `dependencies.requires[].dependsOn[]` | Yes | Required component names |
| `dependencies.parallelGroups[].phase` | Yes | Phase number |
| `dependencies.parallelGroups[].components[]` | Yes | Components in this phase |
| `dependencies.parallelGroups[].prerequisite` | Yes | Phase that must complete first |

**Why needed:** Dependency graphs enable:
- **Parallel implementation** - Independent components can be built concurrently
- **Correct ordering** - Build foundations before things that depend on them
- **Subagent distribution** - LLM orchestrators can assign parallel tasks

**Best Practice:**
- Leaf nodes should be pure, side-effect-free components
- If you have circular dependencies, refactor the design
- Phase numbers should be sequential (1, 2, 3...)

---

### Testable Contracts

| Field | Required | Description |
|-------|----------|-------------|
| `contracts.item[].component` | Yes | Component name |
| `contracts.item[].method` | Yes | Method/property being specified |
| `contracts.item[].given` | Yes | Precondition state |
| `contracts.item[].when` | Yes | Action performed |
| `contracts.item[].then` | Yes | Expected outcome |
| `contracts.errorCases[].component` | Yes | Component name |
| `contracts.errorCases[].scenario` | Yes | Error scenario name |
| `contracts.errorCases[].input` | Yes | Input causing error |
| `contracts.errorCases[].expected` | Yes | Expected error behavior |

**Why needed:** Testable contracts enable:
- **Test-driven implementation** - Write tests before code
- **Unambiguous behavior** - No interpretation needed
- **Subagent autonomy** - LLMs can implement without clarification

**Best Practice:**
- Every public method needs at least one contract
- Error cases are mandatory, not optional
- `then` should be verifiable (return value, state change, exception type)

---

### Quick Reference

| Field | Required | Description |
|-------|----------|-------------|
| `quickReference.imports[].context` | Yes | `production` or `test` |
| `quickReference.imports[].statement` | Yes | Full import statement |
| `quickReference.patterns[].task` | Yes | What to accomplish |
| `quickReference.patterns[].pattern` | Yes | Code pattern |
| `quickReference.mistakes[].wrong` | Yes | Incorrect pattern |
| `quickReference.mistakes[].correct` | Yes | Correct pattern |
| `quickReference.mistakes[].why` | Yes | Explanation |

**Why needed:** Quick reference optimizes for LLM code generation:
- **Copy-paste ready** - No modification needed
- **Anti-patterns documented** - LLMs learn what NOT to do
- **Task-oriented** - Maps user intent to code

**Best Practice:**
- Imports must be complete (package path, not just file name)
- Patterns should be minimal but complete examples
- Include the 3-5 most common mistakes

---

### File Structure

| Field | Required | Description |
|-------|----------|-------------|
| `fileStructure.root` | Yes | Root directory path |
| `fileStructure.items[].path` | Yes | Relative file path |
| `fileStructure.items[].purpose` | Yes | What this file contains |

**Why needed:** File structure enables:
- **Navigation** - Where to find/put things
- **Naming conventions** - Patterns for new files
- **Scope verification** - All files should map to components

---

### Implementation Guide

| Field | Required | Description |
|-------|----------|-------------|
| `implementationGuide.targetAudience` | Yes | Who this guide is for |
| `implementationGuide.principles[]` | Yes | Core generation principles |
| `implementationGuide.protocols[].task` | Yes | Task name |
| `implementationGuide.protocols[].steps[]` | Yes | Step-by-step instructions |
| `implementationGuide.protocols[].example` | Yes | Code example |
| `implementationGuide.disambiguation.trigger` | Yes | When to invoke |
| `implementationGuide.disambiguation.steps[]` | Yes | Resolution steps |
| `implementationGuide.verification[]` | Yes | Checklist items |

**Why needed:** The implementation guide is specifically for LLM code generators. It:
- **Constrains generation** - LLMs follow explicit rules
- **Handles ambiguity** - Tells LLMs when and how to ask
- **Enables verification** - LLMs can self-check

**Best Practice:**
- Protocols should be mechanical (no judgment required)
- Disambiguation should result in asking the user, not guessing
- Verification checklist should be exhaustive

---

### Architecture Diagrams

| Field | Required | Description |
|-------|----------|-------------|
| `diagrams.item[].name` | No | Diagram title |
| `diagrams.item[].type` | No | Diagram category |
| `diagrams.item[].format` | No | Rendering format |
| `diagrams.item[].section` | No | Section anchor |

**Diagram Types:**
- `flowchart` - Process flows, decision trees
- `sequence` - Interaction sequences
- `class` - Type relationships
- `component` - System components
- `layer` - Architectural layers

**Why needed:** Diagrams communicate structure that's hard to express in prose. They're optional but recommended for complex systems.

---

### Core Types

| Field | Required | Description |
|-------|----------|-------------|
| `types.item[].name` | Yes | Type name |
| `types.item[].kind` | Yes | Type category |
| `types.item[].purpose` | Yes | What this type represents |
| `types.item[].file` | Yes | Source file path |
| `types.item[].specSection` | Yes | Detailed section anchor |

**Kind Values:**
- `extension-type` - Dart 3 extension types (zero-cost wrappers)
- `class` - Standard class
- `interface` - Abstract interface
- `enum` - Enumeration
- `typedef` - Type alias

---

### Testing Utilities

| Field | Required | Description |
|-------|----------|-------------|
| `testing.utilities[].name` | Yes | Utility name |
| `testing.utilities[].purpose` | Yes | What it helps test |
| `testing.utilities[].usage` | Yes | Brief usage example |
| `testing.patterns[].name` | Yes | Pattern name |
| `testing.patterns[].description` | Yes | Pattern description |
| `testing.patterns[].example` | Yes | Code example |

**Why needed:** Testing utilities are part of the specification's deliverables. They:
- **Enable adoption** - Easy testing increases usage
- **Standardize patterns** - Consistent test structure
- **Document intent** - Tests show how things should be used

---

### CI/CD Enforcement

| Field | Required | Description |
|-------|----------|-------------|
| `enforcement.checks[].name` | No | Check name |
| `enforcement.checks[].type` | No | Check category |
| `enforcement.checks[].description` | No | What it checks |
| `enforcement.checks[].failureAction` | No | What happens on failure |

**Type Values:**
- `lint` - Code style/pattern checks
- `test` - Automated tests
- `static-analysis` - Type/flow analysis
- `pre-commit` - Git hooks

**Failure Actions:**
- `block` - Prevent merge/deploy
- `warn` - Report but allow

**Why needed:** Enforcement ensures specifications aren't bypassed. Without automation:
- Developers forget rules
- Reviews miss violations
- Technical debt accumulates

---

### Migration Notes

| Field | Required | Description |
|-------|----------|-------------|
| `migration.from` | No | What is being migrated from |
| `migration.steps[]` | No | Migration steps |
| `migration.fallbackPattern` | No | Temporary pattern during migration |

**Why needed:** When specifications supersede others, migration guidance:
- **Reduces friction** - Developers know what to do
- **Enables incremental adoption** - Not everything changes at once
- **Documents fallbacks** - Temporary patterns are explicit

---

## Usage Guidelines

### Creating a New Specification

1. Copy `technical-specification.toon`
2. Fill in all **Required** fields
3. Delete unused optional sections (don't leave empty templates)
4. Convert to markdown for the actual specification document
5. Use TOON as the structural source of truth

### Converting to Markdown

The TOON template defines structure. The markdown specification expands it:

```
TOON                          Markdown
─────                         ────────
acceptanceCriteria.item[0]    ### AC-1: {name}
  .identifier: AC-1
  .name: ...                  {description}
  .description: ...
  .status: PASS               **Status**: PASS
  .verificationMethod: ...    **Verification**: See [E-1](#e1-...)
```

### Validation Checklist

Before considering a specification complete:

- [ ] All required fields populated
- [ ] Every acceptance criterion has evidence
- [ ] Every component has testable contracts
- [ ] Dependency graph has no cycles
- [ ] Quick reference covers common tasks
- [ ] Implementation guide handles ambiguity
- [ ] File structure maps to components

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-17 | Initial template derived from semantic-foundation spec |
