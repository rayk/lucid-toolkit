---
name: do
description: Execute an execution-plan.toon file, running Flutter implementation tasks phase-by-phase with parallel groups
argument-hint: <execution-plan-path>
---

<objective>
Execute the tasks defined in `$ARGUMENTS` (an execution-plan.toon file) following dependency order and parallel group rules.

This transforms a validated execution plan into actual Flutter implementation by:
- Running tasks through specialized agents (flutter-coder, flutter-e2e-tester, etc.)
- Respecting parallel groups for concurrent execution
- Validating checkpoints between phases
- Tracking progress and token usage
- Producing an execution-log.toon with full audit trail

The plan must have been created by flutter-impl-planner with ≥95% success probability.
</objective>

<context>
- Execution plan: @$ARGUMENTS
- Plan template: @plugins/impl-flutter/templates/execution-plan.toon
</context>

<process>
1. **Load and Validate Plan**
   - Read plan from `$ARGUMENTS`
   - Confirm plan has `successProbability >= 0.95`
   - Extract: phases, tasks, dependencies, executionOrder, taskInputs, taskReturns
   - Report plan summary to user

2. **Initialize Execution**
   - Create `execution-log.toon` in same directory as plan
   - Set status: Running, dateStarted: now
   - Report execution start

3. **Execute Phases**
   For each phase in order:

   a. **Start Phase**
      - Report: `🔷 Phase {N}/{total}: {name}`
      - Log phase start event

   b. **Execute Parallel Groups**
      For each parallelGroup (in order):
      - Report: `  Running {count} task(s) in parallel...`
      - Launch ALL tasks in group simultaneously using Task tool
      - Each task uses the agent specified in plan
      - Wait for all to complete
      - Report each result as it completes

   c. **Report Task Results**
      For each completed task:
      - Success: `  ✅ {task-name} ({tokens} tokens)`
      - Failure: `  ❌ {task-name}: {error-summary}`
      - Record outputs and returns in log

   d. **Validate Checkpoint**
      - Run checkpoint.validation criteria
      - Pass: `  ✓ Checkpoint passed`
      - Fail: Handle per checkpoint.onFail (pause or rollback)

   e. **Phase Summary**
      - Report: `  📊 {actual}/{estimated} tokens | {completed}/{total} tasks`
      - Include meaningful taskReturns (testsPassed, coverage, etc.)

4. **Finalize**
   - Update log: status, dateCompleted, summary totals
   - Create final commit using plan's commitMessage
   - Report completion summary

5. **Report Results**
   - Total phases, tasks, tokens
   - Success rate
   - Path to execution-log.toon
   - Final commit reference
</process>

<task_invocation>
## Invoking Tasks

For each task, invoke the specified agent:

```
Task(impl-flutter:{agent}, model: {model}):
"Execute: {task-name}

Objective: {taskDetails.description}

Context:
{Read each file in taskInputs and include relevant content}

Expected Outputs:
{List taskOutputs with paths}

Acceptance Criteria:
{taskDetails.acceptance}

Token Budget: {task.tokens} tokens (variance: {task.variance}%)

When complete, return:
- status: Completed | Failed
- filesCreated: [paths]
- {each key from taskReturns}: {value}
- tokensUsed: {actual}
- error: {if failed, brief description}"
```

**Parallel Execution:**
When tasks share the same parallelGroup, launch them in a SINGLE message with multiple Task tool calls. This runs them concurrently.
</task_invocation>

<progress_reporting>
## Clean Progress Reporting

Use clean, scannable output without tree characters:

**Execution Start:**
```
🚀 Executing: {plan-name}
   {totalPhases} phases, {totalTasks} tasks, ~{estimatedTokens} tokens
```

**Phase Start:**
```
🔷 Phase {N}/{total}: {phase-name}
```

**Parallel Group:**
```
   Running {count} task(s) in parallel...
```

**Task Results (report immediately as each completes):**
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
   📊 {actual}/{estimated} tokens | Returns: testsPassed=true, coverage=94%
```

**Commit (if applicable):**
```
   💾 Commit: {short-sha}
```

**Execution Complete:**
```
✅ Execution complete!

📊 Summary
   Phases: {completed}/{total}
   Tasks: {completed}/{total}
   Tokens: {actual}/{estimated} ({variance}%)
   Duration: {time}

📄 Log: {path-to-execution-log.toon}
💾 Commit: {sha} "{commit-subject}"
```

**Execution Failed:**
```
❌ Execution failed at Phase {N}: {phase-name}

📊 Progress
   Phases: {completed}/{total}
   Tasks: {completed}/{total}

🔴 Failure: {error-description}

📄 Log: {path-to-execution-log.toon}
```
</progress_reporting>

<error_handling>
## Error Handling

**Task Failure:**
1. Log error with timestamp, task ID, error type, message
2. Mark task as Failed in log
3. Continue to checkpoint validation

**Checkpoint Failure:**
- `onFail: pause` → Stop execution, report to user, set log status to Paused
- `onFail: rollback` → Revert changes, retry phase once
- `onFail: continue` → Log warning, proceed to next phase

**Unrecoverable Failure:**
- Set log status to Failed
- Report failure details and recovery suggestions
- Preserve partial progress in log
</error_handling>

<orchestrator_context>
## Protecting Orchestrator Context

Remember: Each subagent runs in isolated context. The orchestrator (this command execution) only grows by taskReturns.

**Keep orchestrator lean:**
- Don't read task output files into orchestrator context
- Record file paths in log, not file contents
- taskReturns should be ≤500 tokens each
- Total orchestrator context should stay under 10K tokens

**Data flows through file system:**
- Task 1 writes file → Task 2 reads file directly
- Orchestrator only tracks: paths, status, metrics
</orchestrator_context>

<output>
Files created/modified:
- `{plan-dir}/execution-log.toon` - Execution audit trail
- Task output files as specified in taskOutputs
- Git commits per phase (if configured)
- Final commit on completion
</output>

<success_criteria>
- Plan loaded and validated (≥95% probability)
- All phases executed in dependency order
- Parallel groups executed concurrently
- All checkpoints validated
- Execution log accurately tracks: times, tokens, outputs, errors
- Final commit created on success
- Clean progress reporting throughout
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
   📊 19,500/20,000 tokens | Returns: testsPassed=true, coverage=96%

✅ Execution complete!

📊 Summary
   Phases: 4/4
   Tasks: 12/12
   Tokens: 67,100/72,000 (-6.8%)
   Duration: 3m 42s

📄 Log: specs/user-auth/execution-log.toon
💾 Commit: e5f6g7h "feat(auth): implement user authentication system"
```
</example>
