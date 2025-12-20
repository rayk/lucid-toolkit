---
name: plan
description: Create a verified execution plan from technical specs and architectural constraints
argument-hint: <spec-path> <constraints-path> <output-dir>
allowed-tools: Task, Bash
---

<critical_behavior>
## MANDATORY: Sequential Subagent Execution

You ARE the orchestrator. Run subagents ONE AT A TIME, SEQUENTIALLY.

**WHY:** Parallel Task calls exhaust Node.js heap memory (16GB+). Sequential execution keeps peak memory at ~2-4GB.

**PROHIBITED ACTIONS:**
- DO NOT spawn multiple Tasks in one message (no parallel execution)
- DO NOT use the flutter-plan-orchestrator agent (deprecated)
- DO NOT read spec/constraint files yourself (delegate to analyzers)

**REQUIRED PATTERN:**
```
Task(agent-1) → wait → get result →
Task(agent-2) → wait → get result →
...
```

Each Task completes and returns BEFORE the next one starts. This ensures memory is released between calls.
</critical_behavior>

<arguments>
All three arguments are REQUIRED:

- `$1` — **Specification Path**: Path to technical specification (file or directory)
- `$2` — **Constraints Path**: Path to architectural constraints (file or directory)
- `$3` — **Output Directory**: Path where all outputs will be written
</arguments>

<workflow>
## Phase 0: Validate Inputs

```bash
test -e "$1" && test -e "$2" && echo "VALID" || echo "INVALID"
```

If output directory doesn't exist, create it:
```bash
mkdir -p "$3"
```

## Phase 1: Analyze Specifications (ONE Task)

```
Task(impl-flutter:plan-spec-analyzer, model: haiku)
Prompt: |
  Analyze specs at: $1
  Return structured summary (features, entities, criteria, API, UI).
  Max 500 tokens response.
```

**Wait for response. Store as `spec_summary`.**

## Phase 2: Analyze Constraints (ONE Task)

```
Task(impl-flutter:plan-constraint-analyzer, model: haiku)
Prompt: |
  Analyze constraints at: $2
  Return structured summary (layers, dependencies, naming, patterns, testing).
  Max 400 tokens response.
```

**Wait for response. Store as `constraint_summary`.**

## Phase 3: Explore Codebase (ONE Task)

```
Task(Explore, model: haiku)
Prompt: |
  Quick explore project at: {project-root}
  Return: structure, existing code patterns, conventions.
  Max 400 tokens response.
```

**Wait for response. Store as `codebase_summary`.**

## Phase 4: Get Capability Matrix (ONE Task)

```
Task(impl-flutter:plan-capability-mapper, model: haiku)
Prompt: |
  Return the capability matrix for Flutter implementation agents.
  Include: agent names (fully-qualified), what they can/cannot do, required inputs.
  Max 500 tokens response.
```

**Wait for response. Store as `capability_matrix`.**

## Phase 5: Synthesize and Decompose (YOU DO THIS)

From the 4 summaries above, build:
1. Feature list with requirements
2. Task decomposition with agent assignments
3. Dependency graph
4. Parallel groups

**Keep this synthesis in YOUR context. Do not spawn a Task for this.**

## Phase 6: Build Context Files (ONE Task)

```
Task(impl-flutter:plan-context-builder, model: haiku)
Prompt: |
  Create context files for tasks:
  {task-list from Phase 5}

  Spec summary: {spec_summary}
  Constraint summary: {constraint_summary}
  Output directory: $3

  Write files: $3/phase-{N}-task-{M}-context.md
```

**Wait for response. Get list of created files.**

## Phase 7: Validate Coverage (ONE Task)

```
Task(impl-flutter:plan-coverage-validator, model: sonnet)
Prompt: |
  Validate 100% spec coverage.

  Spec items: {from spec_summary}
  Tasks: {task-list from Phase 5}

  Return: coverage matrix, status (PASS/FAIL), missing items if any.
```

**Wait for response. If FAIL, report blockers and STOP.**

## Phase 8: Mental Simulation (ONE Task)

```
Task(impl-flutter:plan-simulator, model: sonnet)
Prompt: |
  Run mental simulation of execution plan.

  Tasks: {task-list from Phase 5}
  Dependencies: {dependency graph}

  Return: probability assessment, risks, status (PASS ≥95% / FAIL <95%).
```

**Wait for response. If FAIL, report blockers and STOP.**

## Phase 9: Write Plan (ONE Task)

```
Task(impl-flutter:plan-writer, model: sonnet)
Prompt: |
  Generate execution-plan.toon.

  Tasks: {task-list from Phase 5}
  Dependencies: {dependency graph}
  Project root: {pwd}
  Architecture ref: $2
  Output path: $3/execution-plan.toon

  Write the complete plan file.
```

**Wait for response. Confirm plan file created.**

## Phase 10: Report to User

Return:
- Plan location: `$3/execution-plan.toon`
- Task count and phases
- Success probability
- Any warnings
- Execute command: `/do $3/execution-plan.toon`
</workflow>

<memory_safety>
## Why Sequential Execution is Required

Claude Code runs all Tasks in a single Node.js process. Memory accumulates:

| Pattern | Peak Memory | Result |
|---------|-------------|--------|
| 4 parallel Tasks | 4x per-agent | OOM at 16GB |
| 8 nested Tasks | Cumulative | OOM at 16GB |
| Sequential Tasks | 1x per-agent | ~2-4GB, safe |

**NEVER parallelize Task calls in this command.**
</memory_safety>

<failure_modes>
## When to STOP

| Condition | Action |
|-----------|--------|
| Path validation fails | STOP, report which path is invalid |
| Analyzer returns empty | STOP, report analyzer failure |
| Coverage < 100% | STOP, report missing coverage |
| Probability < 95% | STOP, report simulation blockers |
| Any Task fails | STOP, report which phase failed |

Do not retry failed Tasks. Report the failure and let the user decide.
</failure_modes>

<output_format>
On success:
```
## Execution Plan Created

**Location:** $3/execution-plan.toon
**Phases:** {count}
**Tasks:** {count}
**Probability:** {X}%

Execute with: `/do $3/execution-plan.toon`
```

On failure:
```
## Planning Failed

**Phase:** {which phase failed}
**Reason:** {specific failure}
**Blockers:**
1. {blocker}

Recommendation: {what to fix}
```
</output_format>
