---
name: tech-spec
description: Build a technical specification document following the TOON template structure
argument-hint: <output-path>
allowed-tools: [Read, Write, AskUserQuestion, Task]
---

<objective>
Generate a comprehensive technical specification document and save it to `$ARGUMENTS`.

If no output path provided, default to `docs/specs/{spec-name}.md` based on the specification title.

Technical specifications define implementation details for system components, enabling:
- LLM-assisted development (structured for AI comprehension)
- Parallel implementation (dependency graphs)
- Objective validation (acceptance criteria with evidence)
</objective>

<context>
Template structure: @plugins/architect/templates/tech-spec/technical-specification.toon
Template guide: @plugins/architect/templates/tech-spec/technical-specification-guide.md
</context>

<process>

## Phase 1: Identity & Scope

Use AskUserQuestion to gather identity and scope information:

| Question | Populates |
|----------|-----------|
| What is this specification about? (1 sentence) | Title, Purpose |
| What's IN scope? (list) | Scope Boundaries |
| What's OUT of scope? (list) | Scope Boundaries |
| What does this supersede/replace? | Supersedes section |
| What does this integrate with? | Dependencies |

## Phase 2: Problem Definition

Gather problem context through targeted questions:

| Question | Populates |
|----------|-----------|
| What is the current state? (systems, patterns) | Problem Statement |
| What's wrong with it? (concrete issues, not opinions) | Problem Evidence |
| Why does solving this matter? (consequences of not solving) | Motivation |
| What evidence demonstrates the problem? (before examples) | Evidence section |

## Phase 3: Solution Definition

Define the solution structure:

| Question | Populates |
|----------|-----------|
| What is the solution? (1-3 sentences) | Solution Summary |
| What are the core components? (name + 1-sentence responsibility) | Component Summary |
| What are the dependencies between components? | Dependency Graph |
| What are the public interfaces? (methods/properties per component) | API Specification |

## Phase 4: Contracts & Verification

Establish testable contracts:

| Question | Populates |
|----------|-----------|
| For each public method: Given X, When Y, Then Z? | Testable Contracts |
| What are the error cases? (input → expected behavior) | Error Cases |
| How do you verify it works? (after examples) | Evidence section |

## Phase 5: Usage Patterns

Capture usage patterns for quick reference:

| Question | Populates |
|----------|-----------|
| What imports are required? | Quick Reference |
| What are the 3-5 most common tasks? | Task-based Navigation |
| What are common mistakes and their fixes? | Anti-patterns |

## Phase 6: Build Document Structure

Create the specification document with these required sections:

### Document Metadata
- Unique identifier (spec/{name})
- Version (start at 0.1.0 for draft)
- Classification and status

### Acceptance Criteria
- Each criterion: ID, name, description, status (PENDING), verification method
- Minimum 3 criteria, maximum 7

### Scope Boundaries
- In-scope items (what this covers)
- Out-of-scope items (explicit exclusions)

### Problem Statement
- Problem name and description
- Current state analysis (system, purpose, issue)
- Impact of not solving

### Solution Overview
- Solution name and description
- Key capabilities provided

### Component Summary (if applicable)
- Component name, responsibility, public interface, dependencies
- Section anchor for detailed specification

### Component Dependencies (if applicable)
- Leaf nodes (no dependencies)
- Dependency declarations
- Parallel implementation groups

### Testable Contracts
- Given/When/Then for key behaviors
- Error cases with expected behavior

### Quick Reference
- Required imports (production and test)
- Common task patterns
- Anti-patterns to avoid

### Implementation Guide
- Core generation principles
- Task protocols with examples
- Disambiguation protocol
- Verification checklist

## Phase 7: Write and Save

1. Generate the specification in markdown format
2. Include all required sections from the TOON template
3. Use proper anchor links for navigation
4. Save to the path specified in $ARGUMENTS

</process>

<verification>
Before saving, verify the specification includes:
- [ ] Document metadata with unique @id
- [ ] At least 3 acceptance criteria with verification methods
- [ ] Clear scope boundaries (in/out of scope)
- [ ] Problem statement with impact
- [ ] Solution overview with capabilities
- [ ] Testable contracts (Given/When/Then)
- [ ] Quick reference section
- [ ] Implementation guide for LLM code generators

After saving, verify file creation:
- [ ] File exists at output path
- [ ] File is readable and contains expected sections
</verification>

<output>
File created: `$ARGUMENTS`
- Complete technical specification document
- Markdown format following TOON structure
- Ready for implementation or review
</output>

<success_criteria>
- Specification saved to provided path
- All required sections present and populated
- Acceptance criteria are measurable and verifiable
- Scope boundaries are explicit
- Testable contracts enable TDD approach
- Quick reference enables copy-paste usage
</success_criteria>
