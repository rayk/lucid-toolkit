---
name: execution-prompt-generator
description: Analyze design documents and generate autonomous execution prompts for TDD implementation. Use when generating execution prompts from design docs, planning autonomous TDD implementation, or creating phased implementation plans with cost tracking.
---

<overview>

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

**HAIKU** (prioritize for cost savings):
- Creating stubs, directory structures, boilerplate
- Updating export files (`__init__.py`, `index.ts`)
- Running command-based checks (lint, coverage, style)
- Generating re-export statements
- Any task that follows a template without decisions

**SONNET**:
- Writing tests and implementation (TDD cycles)
- Standard refactoring with code understanding
- Reasoning-based checks (architecture, requirements, documentation)
- Cross-module verification requiring import resolution

**OPUS**:
- Debugging persistent failures
- Architectural decisions
- Complex refactoring requiring deep analysis

**Subtask Splitting**: Within phases, split mechanical subtasks to Haiku. Example: Phase 5 Integration splits export updates (haiku) from verification (sonnet).

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

1. **Dependency Analysis** - Categorized list (external, pre-existing, created)
2. **Validation Results** - Pass/fail for each check
3. **Execution Estimates** - Tokens, duration, model distribution by phase
4. **Exit Criteria** - Explicit and implicit
5. **Complete Execution Prompt** - If all validations pass

</overview>

<output_format>

All structured output from this skill uses TOON (Token-Optimized Object Notation) for maximum efficiency. Use these templates for each output type:

## 1. Dependency Analysis

Use for categorizing and validating dependencies before execution begins.

```toon
@type: ItemList
name: dependencies

external[N]{name,version,actionStatus}:
pytest,8.0.0,CompletedActionStatus
pydantic,2.5.0,FailedActionStatus

preExisting[N]{name,path,actionStatus}:
BaseService,src/base.py,CompletedActionStatus
AuthHandler,src/auth.py,FailedActionStatus

created[N]{name,x-phase,x-requiredBy}:
UserService,phase_3_core,phase_4_features
DataLoader,phase_2_foundation,phase_3_core
```

**Fields**:
- `external` - Third-party libraries with version and installation status
- `preExisting` - Internal dependencies that MUST exist before execution
- `created` - Internal dependencies that will be created during execution
- `x-phase` - The phase that creates this dependency
- `x-requiredBy` - The phase(s) that depend on this component

**ActionStatus Values**:
- `CompletedActionStatus` - Dependency verified/available
- `FailedActionStatus` - Dependency missing or incompatible
- `PotentialActionStatus` - Not yet created (for `created` array)

## 2. Phase Status Tracking

Use for real-time execution progress tracking across all phases.

```toon
@type: Action
name: execution-progress
actionStatus: ActiveActionStatus
x-currentPhase: phase_3_core

phase[9]{name,actionStatus,x-model,x-timeout,x-tokens}:
phase_0_setup,CompletedActionStatus,orchestrator,2m,1000
phase_1_scaffolding,CompletedActionStatus,haiku,3m,5000
phase_2_foundation,CompletedActionStatus,sonnet,15m,20000
phase_3_core,ActiveActionStatus,sonnet,20m,30000
phase_4_features,PotentialActionStatus,sonnet,15m,25000
phase_5_integration,PotentialActionStatus,sonnet,5m,5000
phase_6_verification,PotentialActionStatus,orchestrator,5m,8000
phase_7_debug,PotentialActionStatus,opus,10m,-
phase_8_crosscheck,PotentialActionStatus,sonnet+opus,30m,15000
```

**Fields**:
- `x-currentPhase` - The phase currently executing
- `name` - Phase identifier (phase_N_name)
- `actionStatus` - Phase completion state
- `x-model` - Claude model assigned (haiku/sonnet/opus/orchestrator)
- `x-timeout` - Maximum duration for this phase
- `x-tokens` - Estimated token consumption (- if unknown)

**Phase ActionStatus Values**:
- `PotentialActionStatus` - Not yet started
- `ActiveActionStatus` - Currently executing
- `CompletedActionStatus` - Successfully completed
- `FailedActionStatus` - Failed (triggers phase_7_debug)

## 3. Model Usage Report

Use for cost tracking and optimization analysis after execution completes.

```toon
@type: ItemList
name: model-usage

model[3]{name,x-inputTokens,x-outputTokens,x-calls,x-costUSD}:
haiku,5000,2000,3,0.0038
sonnet,80000,25000,15,0.615
opus,15000,5000,2,0.60
```

**Fields**:
- `name` - Model identifier (haiku/sonnet/opus)
- `x-inputTokens` - Total input tokens consumed
- `x-outputTokens` - Total output tokens generated
- `x-calls` - Number of API calls made
- `x-costUSD` - Total cost in USD

**Cost Formulas** (as of 2025):
- Haiku: ($0.25 input + $1.25 output) per 1M tokens
- Sonnet: ($3 input + $15 output) per 1M tokens
- Opus: ($15 input + $75 output) per 1M tokens

## 4. Cross-Check Results

Use for reporting final validation results across all quality checks.

```toon
@type: Action
name: cross-check-results
actionStatus: FailedActionStatus
x-passed: 5
x-failed: 2
x-skipped: 1

check[8]{name,actionStatus,x-detail}:
lint,CompletedActionStatus,-
coverage,CompletedActionStatus,85%
style,FailedActionStatus,3 errors
architecture,CompletedActionStatus,-
requirements,CompletedActionStatus,-
acceptance,PotentialActionStatus,skipped
documentation,FailedActionStatus,5 missing
custom,CompletedActionStatus,-
```

**Fields**:
- `x-passed` - Count of successful checks
- `x-failed` - Count of failed checks
- `x-skipped` - Count of skipped checks
- `check[N]` - Individual check results
- `x-detail` - Additional context (percentage, error count, reason)

**Check ActionStatus Values**:
- `CompletedActionStatus` - Check passed
- `FailedActionStatus` - Check failed (blocks completion)
- `PotentialActionStatus` - Check skipped (with reason in x-detail)

**Standard Checks**:
1. `lint` - Linter validation
2. `coverage` - Test coverage percentage (80% minimum)
3. `style` - Code style compliance
4. `architecture` - Architecture pattern compliance
5. `requirements` - Requirements verification
6. `acceptance` - Acceptance criteria validation
7. `documentation` - Documentation completeness
8. `custom` - Design-specific exit criteria

## 5. Checkpoint Format

Use for saving execution state for recovery/resumption.

```toon
@type: Action
name: checkpoint
x-version: 1.0
x-system: auth-service
x-lastCompleted: phase_3_core
x-nextPhase: phase_4_features

completed[4]{name,endTime}:
phase_0_setup,2025-11-29T10:00:00Z
phase_1_scaffolding,2025-11-29T10:03:00Z
phase_2_foundation,2025-11-29T10:18:00Z
phase_3_core,2025-11-29T10:38:00Z

pending[5]: phase_4_features,phase_5_integration,phase_6_verification,phase_7_debug,phase_8_crosscheck
```

**Fields**:
- `x-version` - Checkpoint format version (1.0)
- `x-system` - System/module being implemented
- `x-lastCompleted` - Most recently completed phase
- `x-nextPhase` - Next phase to execute on resume
- `completed[N]` - Completed phases with timestamps
- `pending[N]` - Remaining phases (inline array)

**Usage**:
- Save after each phase completion
- Load on crash recovery
- Use for parallel execution coordination

## Integration with Payload Store

For large execution outputs (>500 tokens), combine TOON with the payload-store skill:

```toon
@stored: shared/payloads/plan-exec/20251129-auth-service.md

summary{metric,value}:
totalPhases,9
completed,4
failed,0
tokensUsed,56000
costUSD,0.625

result: Execution checkpoint saved after phase_3_core completion
confidence: High
tokens_stored: 4500
```

This allows the main context to receive a compact summary while preserving full execution details externally.

</output_format>

<templates>

## Templates

Use `templates/execution-prompt.md` for the output structure.

## Examples

See `examples/` for complete generation examples.
