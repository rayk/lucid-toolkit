---
name: do
description: Execute an execution-plan.toon file, running Flutter implementation tasks phase-by-phase with parallel groups
argument-hint: <execution-plan-path>
allowed-tools: Task, Read, Write, Edit, Bash, Glob
---

<objective>
Execute the tasks defined in `$ARGUMENTS` (an execution-plan.toon file) following dependency order and parallel group rules.

This transforms a validated execution plan into actual Flutter implementation by:
- Dispatching tasks to specialized agents via prompts (flutter-coder, flutter-e2e-tester, etc.)
- Respecting parallel groups for concurrent execution
- Validating checkpoints between phases
- Tracking progress in execution-log.toon
- Managing git commits and rollbacks
- **Protecting context by stopping at 85% usage with resume point**
</objective>

<orchestrator_boundaries>
## What This Orchestrator Does (ONLY These)

1. **Prompt Writing** — Construct and dispatch prompts to subagents via Task tool
2. **Log Updates** — Write to execution-log.toon after each task completes
3. **Git Operations** — Commits after phases, rollbacks on checkpoint failure
4. **Context Monitoring** — Check context before phases, stop at 85%
5. **Resume Points** — Save continuation state when stopping

## What This Orchestrator Does NOT Do

- Read task output files (subagents write to filesystem, next subagent reads)
- Analyze or debug subagent failures (record error, mark failed, continue)
- Make implementation decisions (plans specify everything)
- Modify code files (only subagents modify code)
- Read large context into memory (paths only, not contents)

**Principle:** The orchestrator is a dispatcher and bookkeeper, not a worker.
</orchestrator_boundaries>

<context>
- Execution plan: @$ARGUMENTS
- Plan template: @plugins/impl-flutter/templates/execution-plan.toon
</context>

<context_protection>
## Context Monitoring Protocol

Before starting each phase, check remaining context capacity.

**Decision Rule:**
```
estimatedPhaseTokens = phase.estimatedTokens * 0.1  # Orchestrator overhead only
currentUsage = check context (via /context or estimate)

IF currentUsage >= 85%:
  → STOP execution
  → Write resume-continuation-point.md
  → Report to user with resume instructions
```

**Why 85%?** Leaves buffer for:
- Writing the resume file
- Final log update
- User communication
- Safety margin

**Orchestrator Token Budget Per Phase:**
- Read plan section: ~200 tokens
- Construct prompts: ~300 tokens per task
- Log updates: ~100 tokens per task
- Git operations: ~200 tokens
- Total per phase: ~1000-2000 tokens (NOT the task execution cost)

Subagent execution happens in isolated contexts—their token costs don't affect the orchestrator.
</context_protection>

<resume_capability>
## Resume Point Structure

When stopping at 85% context, create `resume-continuation-point.md` in plan directory:

```markdown
# Execution Resume Point

## Plan Reference
- Plan: {path-to-execution-plan.toon}
- Log: {path-to-execution-log.toon}

## Execution State
- Status: Paused (context limit)
- Last Completed Phase: {phase-number} - {phase-name}
- Last Completed Task: {task-id}
- Next Phase: {phase-number} - {phase-name}

## Completed Work
Phases completed: {list}
Tasks completed: {count}/{total}
Tokens used: {actual}/{estimated}

## Remaining Work
Phases remaining: {list with task counts}
Estimated tokens: {remaining-estimate}

## Git State
- Last commit: {sha} "{subject}"
- Branch: {branch-name}

## Resume Instructions

To continue execution, run:
```
/do {plan-path} --resume {this-file-path}
```

The orchestrator will:
1. Read this resume point
2. Skip completed phases
3. Continue from phase {next-phase-number}
4. Append to existing execution-log.toon
```

## Resuming Execution

When `--resume` flag is present:
1. Read the resume-continuation-point.md
2. Verify git state matches (warn if not)
3. Read execution-log.toon to confirm state
4. Skip to the next incomplete phase
5. Continue normal execution from there
</resume_capability>

<process>
## Execution Process

### 1. Parse Arguments
```
planPath = $ARGUMENTS[0]
resumePath = $ARGUMENTS[--resume] if present
```

### 2. Load and Validate Plan
- Read plan from `planPath`
- Confirm plan has `successProbability >= 0.95`
- Extract: phases, tasks, dependencies, executionOrder, taskInputs, taskReturns
- Report plan summary to user

### 3. Handle Resume (if --resume)
- Read resume-continuation-point.md
- Verify git state
- Set startPhase to next incomplete phase
- Report resume state to user

### 4. Initialize Execution
- Create or append to `execution-log.toon` in same directory as plan
- Set status: Running, dateStarted: now (or dateResumed)
- Report execution start

### 5. Execute Phases
For each phase starting from startPhase:

a. **Context Check** (CRITICAL)
   - Estimate orchestrator overhead for this phase
   - If context usage >= 85%: STOP and write resume point
   - Report: `⚠️ Context at {X}%, saving resume point...`

b. **Start Phase**
   - Report: `🔷 Phase {N}/{total}: {name}`
   - Log phase start event

c. **Execute Parallel Groups**
   For each parallelGroup (in order):
   - Report: `  Running {count} task(s) in parallel...`
   - Launch ALL tasks in group simultaneously using Task tool
   - Each task uses the agent specified in plan
   - Wait for all to complete
   - Report each result as it completes

d. **Record Task Results** (immediately after each completes)
   - Update execution-log.toon with:
     - status: Completed | Failed
     - tokensUsed (from subagent return)
     - filesCreated (paths only, NOT contents)
     - error (if failed, brief message only)
   - Do NOT read output files into orchestrator context

e. **Validate Checkpoint**
   - Run checkpoint.validation criteria
   - Pass: `  ✓ Checkpoint passed`
   - Fail: Handle per checkpoint.onFail

f. **Git Commit** (if checkpoint passed)
   - Stage files from taskOutputs paths
   - Commit with phase's commitSubject
   - Report: `  💾 Commit: {short-sha}`

g. **Phase Summary**
   - Report: `📊 {actual}/{estimated} tokens | {completed}/{total} tasks`

### 6. Finalize (on completion)
- Update log: status=Completed, dateCompleted
- Create final commit using plan's commitMessage
- Report completion summary

### 7. Handle Failure (on unrecoverable error)
- Update log: status=Failed
- Write resume-continuation-point.md
- Report failure with recovery instructions
</process>

<task_invocation>
## Invoking Tasks

### Reading agentInputs from Plan

The execution plan includes an `agentInputs` section for each phase that provides required inputs per task:

```toon
agentInputs[{A},]{taskId,inputKey,inputValue}:
  task-1-1,projectRoot,/path/to/project
  task-1-1,targetPaths,lib/domain/entities/
  task-1-1,architectureRef,docs/adr/
  task-1-1,spec,Create User entity with id, email, name
```

The executor reads these and constructs the prompt using them directly.

### Prompt Construction Rules

1. **Read agentInputs from plan** — Use the values directly; they are pre-validated
2. **Never include file contents** — Only paths; subagent reads files itself
3. **Include acceptance criteria** — From taskDetails
4. **Include token budget** — From task.tokens
5. **Agent name from plan** — Use the fully-qualified name in task.agent column

### Agent Dispatch Table

Plans use fully-qualified agent names. The executor dispatches directly:

| Agent (fully-qualified) | Model | Use For |
|------------------------|-------|---------|
| impl-flutter:flutter-coder | sonnet | Domain, application, simple widgets, tests |
| impl-flutter:flutter-ux-widget | opus | Visual widgets, animations, a11y |
| impl-flutter:flutter-e2e-tester | opus | E2E tests, integration tests |
| impl-flutter:flutter-verifier | opus | Code review, architecture compliance |
| Explore | haiku | Codebase exploration (builtin) |
| general-purpose | sonnet | Multi-step research (builtin) |

### impl-flutter:flutter-coder Prompt Template

```
Task({task.agent}, model: {task.model}):
"Implement: {task.name}

Objective: {taskDetails.description}

**Required Inputs (from agentInputs):**
- projectRoot: {agentInputs[task-id].projectRoot}
- targetPaths: {agentInputs[task-id].targetPaths}
- architectureRef: {agentInputs[task-id].architectureRef}
- spec: {agentInputs[task-id].spec}

Context (read these paths for patterns):
{list taskInputs paths}

Expected Outputs:
{list taskOutputs with paths}

Acceptance Criteria:
{taskDetails.acceptance}

Codegen Required: {yes/no based on taskDetails}

**Non-negotiable behaviors:**
1. TDD required — Write tests BEFORE implementation
2. Use mcp__dart__run_tests — NOT Bash flutter test
3. Use mcp__dart__analyze_files — Must achieve 0 errors, 0 warnings, 0 info
4. If codegen needed — build_runner MUST run before final test
5. Complete or FAIL — No 'pending verification'
6. Read architectureRef FIRST for patterns and constraints

Token Budget: {task.tokens} tokens

Return:
- status: Completed | Failed
- filesCreated: [paths]
- testsPassed: true | false
- analyzerClean: true | false
- tokensUsed: {actual}
- error: {if failed}"
```

### impl-flutter:flutter-ux-widget Prompt Template

```
Task({task.agent}, model: {task.model}):
"Implement widget: {task.name}

Objective: {taskDetails.description}

**Required Inputs (from agentInputs):**
- projectRoot: {agentInputs[task-id].projectRoot}
- targetPaths: {agentInputs[task-id].targetPaths}
- architectureRef: {agentInputs[task-id].architectureRef}
- designSpec: {agentInputs[task-id].designSpec}
- spec: {agentInputs[task-id].spec}

Context (read these paths for patterns):
{list taskInputs paths}

Expected Outputs:
{list taskOutputs with paths}

Acceptance Criteria:
{taskDetails.acceptance}

**Non-negotiable behaviors:**
1. Widget tests BEFORE implementation
2. 0/0/0 analyzer compliance
3. 60fps performance target
4. Touch targets ≥48px

Token Budget: {task.tokens} tokens

Return:
- status: Completed | Failed
- filesCreated: [paths]
- testsPassed: true | false
- analyzerClean: true | false
- tokensUsed: {actual}
- error: {if failed}"
```

### impl-flutter:flutter-e2e-tester Prompt Template

```
Task({task.agent}, model: {task.model}):
"Write E2E tests: {task.name}

Objective: {taskDetails.description}

**Required Inputs (from agentInputs):**
- projectRoot: {agentInputs[task-id].projectRoot}
- userFlowSpec: {agentInputs[task-id].userFlowSpec}
- targetPaths: {agentInputs[task-id].targetPaths}

Expected Outputs:
{list taskOutputs with paths}

Acceptance Criteria:
{taskDetails.acceptance}

Token Budget: {task.tokens} tokens

Return:
- status: Completed | Failed
- filesCreated: [paths]
- testsWritten: {count}
- tokensUsed: {actual}
- error: {if failed}"
```

### impl-flutter:flutter-verifier Prompt Template

```
Task({task.agent}, model: {task.model}):
"Verify: {task.name}

Objective: {taskDetails.description}

**Required Inputs (from agentInputs):**
- projectRoot: {agentInputs[task-id].projectRoot}
- architectureRef: {agentInputs[task-id].architectureRef}
- filePaths: {agentInputs[task-id].filePaths}

Verification Criteria:
{taskDetails.acceptance}

Token Budget: {task.tokens} tokens

Return:
- status: Completed | Failed
- violations: [{path, rule, severity}]
- compliant: true | false
- tokensUsed: {actual}
- error: {if failed}"
```

### Builtin Agent Prompt Template (Explore, general-purpose)

```
Task({task.agent}, model: {task.model}):
"Execute: {task.name}

Objective: {taskDetails.description}

Context:
{list taskInputs paths}

Expected Outputs:
{list taskOutputs with paths}

Acceptance Criteria:
{taskDetails.acceptance}

Token Budget: {task.tokens} tokens

Return:
- status: Completed | Failed
- filesCreated: [paths]
- {keys from taskReturns}: {values}
- tokensUsed: {actual}
- error: {if failed}"
```

### Parallel Execution

When tasks share the same parallelGroup, launch them in a SINGLE message with multiple Task tool calls:

```
# Phase 2, Parallel Group 1: tasks A, B, C
Task(impl-flutter:flutter-coder): "Implement: Task A..."
Task(impl-flutter:flutter-coder): "Implement: Task B..."
Task(impl-flutter:flutter-ux-widget): "Implement: Task C..."
```

All Task calls in a single message execute concurrently.
</task_invocation>

<failure_handling>
## Failure Handling

### Subagent Failure (task returns status: Failed)

1. **Record immediately** — Write to execution-log.toon:
   ```
   {task-id}:
     status: Failed
     error: {brief error from subagent return}
     tokensUsed: {actual}
   ```

2. **Do NOT investigate** — The orchestrator doesn't debug failures
   - Don't read the files the subagent created
   - Don't analyze what went wrong
   - Don't attempt to fix

3. **Continue to checkpoint** — Let checkpoint validation decide next step

### Checkpoint Failure

Based on `checkpoint.onFail`:

- **pause**: Stop execution, save resume point, report to user
- **rollback**:
  1. `git reset --hard {checkpoint.rollbackTo-commit}`
  2. Retry the phase once
  3. If fails again: pause
- **continue**: Log warning, proceed to next phase

### Context Exhaustion (85% reached)

1. Stop immediately (don't start new phase)
2. Write resume-continuation-point.md
3. Commit any pending work
4. Report to user:
   ```
   ⚠️ Context limit reached (85%)

   Progress saved to: {resume-point-path}

   To continue:
   /do {plan-path} --resume {resume-point-path}
   ```

### Unrecoverable Failure

- Git command failures
- Plan file corruption
- Missing required files

Response:
1. Set log status: Failed
2. Write resume-continuation-point.md with error details
3. Report failure and manual recovery steps
</failure_handling>

<progress_reporting>
## Progress Output Format

**Execution Start:**
```
🚀 Executing: {plan-name}
   {totalPhases} phases, {totalTasks} tasks, ~{estimatedTokens} tokens
```

**Resume Start:**
```
🔄 Resuming: {plan-name}
   From phase {N}/{total}, {remainingTasks} tasks remaining
```

**Phase Start:**
```
🔷 Phase {N}/{total}: {phase-name}
```

**Parallel Group:**
```
   Running {count} task(s) in parallel...
```

**Task Results:**
```
   ✅ {task-name} ({tokensUsed} tokens)
   ❌ {task-name}: {brief-error}
```

**Checkpoint:**
```
   ✓ Checkpoint passed
   ✗ Checkpoint failed: {reason}
```

**Phase Summary:**
```
   📊 {actual}/{estimated} tokens | {completed}/{total} tasks
   💾 Commit: {short-sha}
```

**Context Warning:**
```
   ⚠️ Context at {X}%, saving resume point...
```

**Execution Complete:**
```
✅ Execution complete!

📊 Summary
   Phases: {completed}/{total}
   Tasks: {completed}/{total}
   Tokens: {actual}/{estimated} ({variance}%)

📄 Log: {path-to-execution-log.toon}
💾 Commit: {sha} "{commit-subject}"
```

**Execution Paused (context limit):**
```
⏸️ Execution paused (context limit)

📊 Progress
   Phases: {completed}/{total}
   Tasks: {completed}/{total}

📄 Resume: {path-to-resume-point}

To continue:
/do {plan-path} --resume {resume-point-path}
```

**Execution Failed:**
```
❌ Execution failed at Phase {N}: {phase-name}

📊 Progress
   Phases: {completed}/{total}
   Tasks: {completed}/{total}

🔴 Failure: {error-description}

📄 Log: {path-to-execution-log.toon}
📄 Resume: {path-to-resume-point}
```
</progress_reporting>

<execution_log_format>
## Execution Log Structure

The execution-log.toon is updated after EACH task (not batched):

```
@type: ItemList
@id: execution-log-{plan-id}
name: Execution Log
status: Running | Completed | Failed | Paused
dateStarted: {iso-datetime}
dateCompleted: {iso-datetime}
dateResumed: {iso-datetime}  # if resumed

summary:
  phasesCompleted: {N}
  tasksCompleted: {N}
  tasksFailed: {N}
  tokensUsed: {total}
  tokensEstimated: {from-plan}

phases[]:
  {phase-id}:
    status: Completed | Failed | InProgress | Pending
    dateStarted: {iso-datetime}
    dateCompleted: {iso-datetime}
    commit: {sha}
    tokensUsed: {actual}

    tasks[]:
      {task-id}:
        status: Completed | Failed | InProgress | Pending
        dateStarted: {iso-datetime}
        dateCompleted: {iso-datetime}
        tokensUsed: {actual}
        filesCreated: [paths]
        returns: {key-value pairs from taskReturns}
        error: {if failed}

events[]:
  - timestamp: {iso-datetime}
    type: PhaseStart | PhaseEnd | TaskStart | TaskEnd | Checkpoint | Commit | Error | Pause | Resume
    details: {relevant info}
```
</execution_log_format>

<success_criteria>
- Plan loaded and validated (≥95% probability)
- All phases executed in dependency order (or paused with resume point)
- Parallel groups executed concurrently
- All checkpoints validated
- Execution log accurately tracks: times, tokens, outputs, errors
- Git commits created per phase
- Context stayed under 85% OR resume point saved
- Clean progress reporting throughout
- Orchestrator context protected (paths only, no file contents)
</success_criteria>

<example>
```
/do specs/user-auth/execution-plan.toon

🚀 Executing: user-auth-implementation
   4 phases, 12 tasks, ~125,000 tokens

🔷 Phase 1/4: Domain Layer
   Running 2 task(s) in parallel...
   ✅ Create User entity (4,200 tokens)
   ✅ Create AuthToken entity (3,800 tokens)
   Running 1 task(s) in parallel...
   ✅ Create UserRepository interface (2,900 tokens)
   ✓ Checkpoint passed
   💾 Commit: a1b2c3d
   📊 10,900/12,000 tokens | 3/3 tasks

🔷 Phase 2/4: Application Layer
   Running 2 task(s) in parallel...
   ✅ Create LoginUseCase (8,400 tokens)
   ✅ Create RegisterUseCase (7,200 tokens)
   Running 1 task(s) in parallel...
   ✅ Create AuthNotifier provider (5,100 tokens)
   ✓ Checkpoint passed
   💾 Commit: b2c3d4e
   📊 20,700/22,000 tokens | 3/3 tasks

⚠️ Context at 87%, saving resume point...

⏸️ Execution paused (context limit)

📊 Progress
   Phases: 2/4
   Tasks: 6/12

📄 Resume: specs/user-auth/resume-continuation-point.md

To continue:
/do specs/user-auth/execution-plan.toon --resume specs/user-auth/resume-continuation-point.md
```

**Then in a new session:**
```
/do specs/user-auth/execution-plan.toon --resume specs/user-auth/resume-continuation-point.md

🔄 Resuming: user-auth-implementation
   From phase 3/4, 6 tasks remaining

🔷 Phase 3/4: Infrastructure Layer
   Running 2 task(s) in parallel...
   ✅ Implement FirebaseAuthRepository (9,800 tokens)
   ✅ Create SecureStorageService (6,200 tokens)
   ✓ Checkpoint passed
   💾 Commit: c3d4e5f
   📊 16,000/18,000 tokens | 2/2 tasks

🔷 Phase 4/4: Testing
   Running 4 task(s) in parallel...
   ✅ User entity tests (3,200 tokens)
   ✅ Repository tests (4,800 tokens)
   ✅ UseCase tests (6,100 tokens)
   ✅ Provider tests (5,400 tokens)
   ✓ Checkpoint passed
   💾 Commit: d4e5f6g
   📊 19,500/20,000 tokens | 4/4 tasks

✅ Execution complete!

📊 Summary
   Phases: 4/4
   Tasks: 12/12
   Tokens: 67,100/72,000 (-6.8%)

📄 Log: specs/user-auth/execution-log.toon
💾 Commit: e5f6g7h "feat(auth): implement user authentication system"
```
</example>
