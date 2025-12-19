---
name: plan
description: Create a verified execution plan from technical specs and architectural constraints
argument-hint: <spec-path> <constraints-path>
allowed-tools: Task
---

<objective>
Generate a verified execution plan for Flutter implementation by analyzing technical specifications and architectural constraints.

**Target Execution Agents (FULLY-QUALIFIED NAMES):**
Plans produced by this command assign tasks to ONLY these agents:

| Agent | Fully-Qualified Name | Use For | Model | Pre-Flight |
|-------|---------------------|---------|-------|------------|
| flutter-coder | `impl-flutter:flutter-coder` | Domain, application, simple widgets, unit/widget tests | sonnet | `--dry-run` |
| flutter-ux-widget | `impl-flutter:flutter-ux-widget` | Visual widgets, animations, custom paint, a11y | opus | `--dry-run` |
| flutter-e2e-tester | `impl-flutter:flutter-e2e-tester` | E2E tests, integration tests, user flow testing | opus | `--dry-run` |
| flutter-verifier | `impl-flutter:flutter-verifier` | Code review, architecture compliance verification | opus | `--dry-run` |
| Explore | `Explore` | Codebase exploration, finding files/patterns | haiku | N/A |
| general-purpose | `general-purpose` | Multi-step research, complex searches | sonnet | N/A |

**Planning Subagents (internal):**
- plan-spec-analyzer (haiku) — Analyzes specs, returns structured summary
- plan-constraint-analyzer (haiku) — Analyzes constraints, returns rules
- plan-capability-mapper (haiku) — Maps agent capabilities for all 4 Flutter agents
- plan-context-builder (haiku) — Creates consolidated context files
- plan-coverage-validator (sonnet) — Validates 100% spec coverage + agent validity
- plan-simulator (opus) — Runs mental simulation for probability
- plan-writer (sonnet) — Generates execution-plan.toon

The orchestrator delegates ALL heavy work to subagents, protecting its context.
</objective>

<context>
Project root: !`pwd`
</context>

<agent_knowledge>
## Agent Capabilities, Required Inputs & Pre-Flight

All Flutter agents support `--dry-run` pre-flight validation. Before assigning a task, the orchestrator
or simulator can invoke an agent with `--dry-run` to verify it can complete the task.

### impl-flutter:flutter-coder (sonnet, 15-25K tokens)

**Capabilities:**
- Domain layer: entities, repositories, use cases
- Application layer: providers, notifiers, services
- Simple widgets: forms, lists, CRUD screens
- Unit/widget tests: TDD methodology

**Stack:** fpdart 1.2, Riverpod 3.0, Freezed, mocktail, fast_immutable_collections

**TDD Workflow:** RED → GREEN → VERIFY (0/0/0 analyzer)

**Required agentInputs:**
- `projectRoot` — Absolute path to project/package
- `targetPaths` — Where to create files
- `architectureRef` — Path to ADRs/constraints
- `spec` — Behavioral specification

**Pre-Flight Invocation:**
```
Task(impl-flutter:flutter-coder)
Prompt: |
  --dry-run
  Can you implement this?

  projectRoot: {path}
  targetPaths: {paths}
  architectureRef: {adr-path}
  spec: {specification}
```

**Pre-Flight Response:** DRY RUN: READY or DRY RUN: NOT READY with blockers

---

### impl-flutter:flutter-ux-widget (opus, 25-40K tokens)

**Capabilities:**
- Visual widgets: animations, transitions, custom painters
- Custom rendering: RenderObject, CustomPaint, shaders
- Performance: 60fps optimization, RepaintBoundary
- Accessibility: semantics, contrast, touch targets ≥48px
- Theming: design system, Material 3, dark mode

**TDD Workflow:** Widget tests first, RED → GREEN → VERIFY (0/0/0 analyzer)

**Required agentInputs:**
- `projectRoot` — Absolute path to project/package
- `targetPaths` — Where to create widget files
- `architectureRef` — Path to design system docs
- `designSpec` — Visual specification (mockup, Figma, description)
- `spec` — Behavioral spec (states, interactions, animations)

**Pre-Flight Invocation:**
```
Task(impl-flutter:flutter-ux-widget)
Prompt: |
  --dry-run
  Can you implement this widget?

  projectRoot: {path}
  targetPaths: {paths}
  architectureRef: {design-system-path}
  designSpec: {visual-spec}
  spec: {behavioral-spec}
```

**Pre-Flight Response:** DRY RUN: READY with patterns found, or NOT READY with blockers

---

### impl-flutter:flutter-e2e-tester (opus, 25-40K tokens)

**Capabilities:**
- E2E tests from user flow specifications
- Integration tests for complete user journeys
- Robot pattern / page object implementation
- Golden tests for visual regression
- Performance profiling tests

**TDD Workflow:** Write E2E test first → expect FAIL → implementation → expect PASS

**Required agentInputs:**
- `projectRoot` — Absolute path to project/package
- `userFlowSpec` — User flow specification (steps, preconditions, acceptance criteria)
- `targetPaths` — Where to create test files (integration_test/)

**Pre-Flight Invocation:**
```
Task(impl-flutter:flutter-e2e-tester)
Prompt: |
  --dry-run
  Can you write E2E tests for this user flow?

  projectRoot: {path}
  userFlowSpec: |
    ## Login Flow
    Steps:
    1. User opens app → sees login screen
    2. User enters credentials
    3. User taps Sign In
    4. User sees home screen

    Acceptance Criteria:
    - Email validation
    - Error messages
  targetPaths: integration_test/flows/
```

**Pre-Flight Response:** DRY RUN: READY with screens/robots identified, or NOT READY with blockers

---

### impl-flutter:flutter-verifier (opus, 25-40K tokens)

**Capabilities:**
- Verify code against architectural constraints (ADRs)
- Review implementations from flutter-coder/flutter-ux-widget
- Static analysis and anti-pattern detection
- Architecture compliance (layer boundaries, patterns)
- Test coverage verification

**Methodology:** Read-only verification, never modifies files

**Required agentInputs:**
- `architectureRef` — Path to ADRs/constraints (REQUIRED)
- `filePaths` — Files to review (REQUIRED)
- `projectRoot` — Absolute path to project/package

**Pre-Flight Invocation:**
```
Task(impl-flutter:flutter-verifier)
Prompt: |
  --dry-run
  Can you verify these files?

  architectureRef: docs/adr/
  filePaths:
    - lib/features/auth/domain/auth_repository.dart
    - lib/features/auth/application/auth_provider.dart
  projectRoot: {path}
```

**Pre-Flight Response:** DRY RUN: READY with architecture docs found, or NOT READY with blockers

---

## Task Assignment Decision Tree

When assigning tasks, use this decision tree:

```
1. Is it E2E/integration testing?
   → impl-flutter:flutter-e2e-tester (requires userFlowSpec)

2. Is it code verification/review?
   → impl-flutter:flutter-verifier (requires architectureRef + filePaths)

3. Does it involve animation, custom paint, or 60fps requirement?
   → impl-flutter:flutter-ux-widget (requires designSpec)

4. Is it a design system component or accessibility-focused?
   → impl-flutter:flutter-ux-widget

5. Is it a simple form, list, or CRUD screen?
   → impl-flutter:flutter-coder

6. Is it domain/application layer (entities, repos, providers)?
   → impl-flutter:flutter-coder

7. Is it primarily business logic with minimal UI?
   → impl-flutter:flutter-coder
```

## Pre-Flight Validation in Plans

The plan-simulator should invoke `--dry-run` on agents for complex or uncertain tasks:

```
# During mental simulation, validate task assignment:
Task(impl-flutter:flutter-coder, --dry-run)
  "Can you implement {task-description}?"
  Required inputs: {inputs}

# If NOT READY, either:
# 1. Reassign to different agent
# 2. Add missing inputs to task context
# 3. Split task into smaller units
```
</agent_knowledge>

<process>
1. Validate that spec path `$1` exists
2. Validate that constraints path `$2` exists
3. Launch flutter-plan-orchestrator with both paths
4. Orchestrator launches parallel analyzers (Phase 1)
5. Orchestrator synthesizes and decomposes (Phases 2-4)
6. Coverage validation gate (must be 100% + valid agents + complete agentInputs)
7. Mental simulation gate (must be ≥95%)
8. Plan written to disk with:
   - Fully-qualified agent names (impl-flutter:flutter-coder, not flutter-coder)
   - agentInputs for each Flutter agent task
   - projectRoot and architectureRef at plan level
9. Report location and summary

If either path is missing, stop and inform the user.
</process>

<agent_invocation>
Invoke the orchestrator with this Task call:

```
Task(impl-flutter:flutter-plan-orchestrator)
Prompt: |
  Create an execution plan for Flutter implementation.

  **Technical Specification Path:** $1
  **Architectural Constraints Path:** $2
  **Project Root:** {current working directory}

  Follow your workflow:
  1. Validate inputs exist
  2. Launch parallel analyzers (specs, constraints, codebase, capabilities)
  3. Synthesize summaries into implementation units
  4. Build dependency graph
  5. Decompose into context-sized tasks with agentInputs
  6. Launch context consolidation
  7. Validate 100% spec coverage + valid agents + complete agentInputs
  8. Run mental simulation (up to 5 rounds)
  9. If ≥95% probability: write execution-plan.toon
  10. Report results

  Return the plan location and a summary of:
  - Total phases and tasks
  - Estimated tokens and models
  - Success probability
  - Agent distribution (fully-qualified names)
  - Any warnings or caveats
```
</agent_invocation>

<success_criteria>
- Both input paths validated as existing
- Orchestrator successfully invoked
- All subagents complete their phases
- Coverage validation passes (100%)
- Agent validation passes (all fully-qualified names)
- agentInputs validation passes (all required inputs present)
- Simulation passes (≥95% probability)
- Plan produced with execution-plan.toon written containing:
  - projectRoot and architectureRef at plan level
  - All agent names fully-qualified
  - agentInputs for each Flutter agent task
- All tasks assigned to valid agents only:
  - impl-flutter:flutter-coder (domain, application, simple widgets, unit/widget tests)
  - impl-flutter:flutter-ux-widget (visual widgets, animations, custom paint, a11y)
  - impl-flutter:flutter-e2e-tester (E2E tests, integration tests, user flow testing)
  - impl-flutter:flutter-verifier (code review, architecture compliance)
  - Explore (builtin)
  - general-purpose (builtin)
- All task assignments include required agentInputs for the agent:
  - impl-flutter:flutter-coder: projectRoot, targetPaths, architectureRef, spec
  - impl-flutter:flutter-ux-widget: projectRoot, targetPaths, architectureRef, designSpec, spec
  - impl-flutter:flutter-e2e-tester: projectRoot, userFlowSpec, targetPaths
  - impl-flutter:flutter-verifier: architectureRef, filePaths, projectRoot
- Pre-flight validation passes for complex tasks (--dry-run returns READY)
- OR: Clear explanation of why planning failed with recommendations
</success_criteria>

<output>
On success, the orchestrator creates:
- `execution-plan.toon` — The verified implementation plan
- `phase-{N}-task-{M}-context.md` — Consolidated context files for each task

All files are saved in the same directory as the specification.

The plan is ready for execution via:
```
/do {spec-directory}/execution-plan.toon
```
</output>
