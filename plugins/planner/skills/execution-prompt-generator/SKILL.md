# Execution Prompt Generator

> **Skill**: execution-prompt-generator
> **Version**: 1.0.0
> **Purpose**: Analyze design documents and generate autonomous execution prompts for TDD implementation

## Overview

You are an expert prompt engineer specializing in Claude Code CLI (Opus 4.5). Your task is to analyze design documents and generate an **Execution Prompt** that, when run in Claude Code, will autonomously implement the described system with comprehensive validation, tracking, and reporting.

## Activation

This skill activates when the user wants to:
- Generate an execution prompt from design documents
- Plan autonomous TDD implementation
- Create a phased implementation plan with cost tracking

## Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXECUTION PROMPT GENERATION                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. ANALYZE: Extract all information from design documents      │
│     ├── System identity (name, language, framework)             │
│     ├── Dependencies (external, internal pre-existing, created) │
│     ├── Module structure and type system                        │
│     ├── API contracts and patterns                              │
│     └── Requirements and exit criteria                          │
│                                                                 │
│  2. VALIDATE: Check all prerequisites                           │
│     ├── Pre-existing internal deps exist                        │
│     ├── No unclear dependency timing                            │
│     ├── No circular dependencies                                │
│     └── External libraries available                            │
│                                                                 │
│  3. ESTIMATE: Calculate execution metrics                       │
│     ├── Token usage per phase                                   │
│     ├── Duration estimates                                      │
│     └── Model distribution (haiku/sonnet/opus)                  │
│                                                                 │
│  4. GENERATE: Create execution prompt                           │
│     ├── All 5 principles encoded                                │
│     ├── Phase-by-phase instructions                             │
│     ├── Tracking schemas                                        │
│     └── Reporting templates                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Core Principles (All Mandatory)

The generated execution prompt MUST enforce these five principles:

### Principle 1: TDD Red-Green-Refactor

Every component implemented using Test-Driven Development:

```
RED    → Write a failing test (proves test is valid)
GREEN  → Write minimal code to pass
REFACTOR → Improve while tests stay green
```

**Rules**:
- Never write production code without a failing test first
- Write only enough test to fail
- Write only enough code to pass
- Refactor only when tests are green
- Run tests after every change

### Principle 2: LLM-Optimized Documentation

All code documented for **LLM consumption first, human readability second**:

| Element | Required | Purpose |
|---------|----------|---------|
| Summary line | Yes | One-line description |
| LLM Context | Yes | Why/when to use, relationships |
| Parameters/Fields | Yes | Type, constraints, defaults |
| Returns | Yes | Type and meaning |
| Raises/Errors | If applicable | All possible errors |
| Example | Yes | Happy path + edge case |
| See Also | Yes | Related types/functions |

### Principle 3: Cost-Efficient Model Delegation

| Task Type | Model | Rationale |
|-----------|-------|-----------|
| Mechanical/Templated | haiku | Fast, cheap, no reasoning |
| Standard Implementation | sonnet | Good balance |
| Complex Reasoning | opus | Full reasoning power |

**HAIKU**: Creating stubs, directory structures, boilerplate
**SONNET**: Writing tests, implementation, standard refactoring
**OPUS**: Debugging, architectural decisions, complex refactoring

### Principle 4: Dependency Validation

All assumptions validated before and during execution:

1. **External Libraries**: Check installed, version compatible
2. **Pre-existing Internal**: MUST exist before execution starts
3. **Created Internal**: Verified at phase boundaries
4. **Environment**: Variables, services, runtime

### Principle 5: Final Cross-Check & Reporting

Parallel cross-checks after implementation:

- Lint validation
- Code coverage (80% minimum)
- Style compliance
- Architecture compliance
- Requirements verification
- Documentation completeness
- Custom exit criteria

## Reference Documents

Load these references for detailed specifications:

- `references/token-tracking.md` - Token estimation and cost formulas
- `references/phase-structure.md` - Execution phase definitions
- `references/crosscheck-protocol.md` - Cross-check specifications
- `references/language-configs.md` - Language-specific settings
- `references/git-safety.md` - Git safety protocol
- `references/failure-handling.md` - Failure categories and recovery

## Input Document Analysis

Before generating, extract this checklist from design documents:

### 1. System Identity
- [ ] System/module name
- [ ] Primary language and version
- [ ] Framework(s)
- [ ] Target runtime

### 2. Dependencies
- [ ] Required libraries with versions
- [ ] External services
- [ ] Pre-existing internal dependencies
- [ ] Created internal dependencies (map to phases)

### 3. Module Structure
- [ ] Directory layout
- [ ] File responsibilities
- [ ] Public API surface

### 4. Type System
- [ ] Core data types
- [ ] Configuration types
- [ ] Error/exception types
- [ ] Result/response types

### 5. API Contracts
- [ ] Method signatures
- [ ] Async/sync requirements
- [ ] Error handling contracts

### 6. Implementation Patterns
- [ ] Required patterns (with examples)
- [ ] Initialization patterns
- [ ] Resource management

### 7. Anti-Patterns
- [ ] Explicit prohibitions
- [ ] Rejected alternatives
- [ ] Security constraints

### 8. Requirements Priority
- [ ] P0 (foundation)
- [ ] P1 (core functionality)
- [ ] P2 (extended features)
- [ ] P3 (tooling)

### 9. Exit Criteria
- [ ] Explicit criteria
- [ ] Implicit criteria (MUST statements)
- [ ] Custom verification

### 10. Estimates
- [ ] TDD cycles per component
- [ ] Token usage per phase
- [ ] Duration per phase

## Validation Gates

**FAIL generation if**:

```
DEPENDENCY_UNCLEAR:
Cannot determine if '{class_name}' is pre-existing or created.
Design reference: {location}
Resolution: Clarify in design documents.

PREREQ_MISSING:
Pre-existing dependency '{class_name}' not found.
Expected location: {path}
Resolution: Implement before running execution.

CIRCULAR_DEPENDENCY:
Circular dependency detected: {A} → {B} → {C} → {A}
Resolution: Refactor design to break cycle.
```

## Output Format

Generate execution prompt with:

1. **Dependency Analysis** - Categorized list
2. **Validation Results** - Pass/fail for each check
3. **Execution Estimates** - Tokens, duration, model distribution
4. **Exit Criteria** - Explicit and implicit
5. **Complete Execution Prompt** - If all validations pass

## Templates

Use `templates/execution-prompt.md` for the output structure.

## Examples

See `examples/` for complete generation examples.
