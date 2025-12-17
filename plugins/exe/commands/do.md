---
name: do
description: Execute an execution-plan.toon file, running tasks phase-by-phase with parallel groups, and output an execution-log.toon
argument-hint: <execution-plan-path>
---

<objective>
Execute the tasks defined in `$ARGUMENTS` (an execution-plan.toon file) following the dependency order and parallel group rules.

This transforms a validated execution plan into actual implementation, tracking progress, token usage, outputs, and errors in an execution-log.toon file.
</objective>

<context>
- Execution plan: @$ARGUMENTS
- Plan template: @plugins/exe/templates/execution-plan.toon
- Log template: @plugins/exe/templates/execution-log.toon
</context>

<process>
1. **Validate Input**
   - If `$ARGUMENTS` is empty, ask user for the execution plan path
   - Confirm plan file exists and has `status: Validated` or `status: Draft`
   - Extract plan metadata: phases, tasks, dependencies, executionOrder

2. **Initialize Execution Log**
   - Create `execution-log.toon` in same directory as the plan
   - Set `status: Running`, `dateStarted: {now}`, `planRef: $ARGUMENTS`
   - Initialize empty timeline, summary with zeros

3. **Execute Phase Loop**
   For each phase in order:

   a. **Log phase start**
      - Add timeline event: `phase-started`
      - Update phase status to `Running`
      - **Report to user:** `📦 Phase {order}/{total}: {phase-name} ({N} tasks)`

   b. **Execute tasks by parallel group**
      - Group tasks by `parallelGroup` value
      - For each group (ascending order):
        - **Report to user:** `  ├─ [Group {N}] Running {count} task(s)...`
        - Launch all tasks in the group **in parallel** using Task tool
        - Each task invocation: `Task({agent}): "{task prompt with inputs}"`
        - Wait for all tasks in group to complete
        - **Report each task completion immediately:**
          - Success: `  │  ├─ {task-name} ✅ ({tokensUsed} tokens)`
          - Failure: `  │  ├─ {task-name} ❌ {error-summary}`
        - Log each task completion/failure with metrics

   c. **Process task results**
      - Record taskOutputs (files created)
      - Record taskReturns (key-value data)
      - Update token counts and duration
      - If task failed: log error, check checkpoint.onFail action

   d. **Run checkpoint validation**
      - Execute validation criteria from `checkpoint.validation`
      - If PASS: log `checkpoint-passed`, continue to next phase
      - If FAIL:
        - If `onFail: pause` → stop execution, report to user
        - If `onFail: rollback` → restore to checkpoint.rollbackTo state

   e. **Create phase commit** (if configured)
      - Stage all taskOutputs from this phase
      - Commit with phase.commitSubject
      - Log commit SHA

   f. **Report phase summary** (1-2 lines)
      - **Report to user:**
        ```
        └─ Phase complete: {actual}/{estimated} tokens ({variance}%) | Returns: {key}={value}, {key}={value}
        ```
      - Include all non-trivial taskReturns (skip tokensConsumed, toolUseCount unless notable)
      - If no returns: `└─ Phase complete: {actual}/{estimated} tokens ({variance}%)`

4. **Finalize Execution**
   - Update log status: `Completed` or `Failed`
   - Set `dateCompleted: {now}`
   - Calculate final summary (totalTokensUsed, completedTasks, etc.)
   - Create final commit using plan's `commitMessage` template
   - Log `plan-completed` or `plan-failed` event

5. **Report Results**
   - Display execution summary: phases completed, tasks run, tokens used
   - List any failures or warnings
   - Provide path to execution-log.toon
</process>

<progress_reporting>
## Real-time Progress Reporting

Report progress to the user at each stage:

**Phase start:**
```
📦 Phase {order}/{total}: {phase-name} ({taskCount} tasks)
```

**Parallel group start:**
```
   ├─ [Group {N}] Running {count} task(s)...
```

**Task completion (report immediately after each subagent returns):**
```
   │  ├─ {task-name} ✅ ({tokensUsed} tokens)
   │  └─ {task-name} ❌ {brief-error}
```

**Checkpoint result:**
```
   ├─ ✅ Checkpoint passed
   ├─ ❌ Checkpoint failed: {reason}
```

**Phase commit (if applicable):**
```
   ├─ 📝 Commit: {short-sha}
```

**Phase summary (always, 1-2 lines max):**
```
   └─ Phase complete: {actual}/{estimated} tokens ({variance}%)
   └─ Phase complete: {actual}/{estimated} tokens ({variance}%) | Returns: {key}={value}, ...
```

Only include taskReturns that are meaningful to the user (e.g., testCoverage, testsPass, lintErrors). Omit internal metrics like tokensConsumed or toolUseCount unless they indicate a problem.
</progress_reporting>

<task_invocation_format>
When invoking tasks, use this pattern:

```
Task({agent}, model={model}):
"Execute task: {task-name}

**Objective:** {taskDetails.description}

**Inputs:**
{for each taskInput: load content or reference}

**Expected Outputs:**
{for each taskOutput: path and type}

**Acceptance Criteria:**
{taskDetails.acceptance}

**Token Budget:** {task.tokens} (variance: {task.variance}%)

Return structured result with:
- status: Completed | Failed
- outputs: list of files created
- returns: key-value data as specified
- tokensUsed: actual token count
- error: (if failed) error message"
```

**Parallel execution:** When multiple tasks share the same parallelGroup, invoke them in a single message with multiple Task tool calls.
</task_invocation_format>

<error_handling>
**Task Failure:**
- Log error in phase.errors array with timestamp, errorType, message
- Check if task has retry configuration
- If retries available: attempt retry, log in phase.retries
- If no retries or max retries exceeded: mark task as Failed

**Checkpoint Failure:**
- If `onFail: pause`: Stop execution, update log status to `Failed`, report blockers to user
- If `onFail: rollback`: Revert to rollbackTo state, attempt phase again (max 1 retry)

**Unrecoverable Failure:**
- Update log status to `Failed`
- Log `plan-failed` event with reason
- Report to user with failure details and recovery options
</error_handling>

<output>
Files created/modified:
- `{plan-dir}/execution-log.toon` - Detailed execution log following template structure
- Phase commits (if configured) - One commit per phase
- Final commit (on completion) - Squash commit with full commit message
</output>

<success_criteria>
- All phases executed in order
- All tasks executed respecting dependency order and parallel groups
- Execution log accurately reflects runtime: timestamps, tokens, outputs, errors
- Checkpoints validated between phases
- Final commit created (if plan completed successfully)
- Execution summary reported to user
</success_criteria>

<example>
User: `/exe:do specs/auth-system/execution-plan.toon`

Execution flow:
```
📋 Loading execution plan...
   Plan: auth-system
   Phases: 4
   Tasks: 12
   Estimated tokens: 245,000

🚀 Starting execution...

📦 Phase 1/4: Infrastructure (3 tasks)
   ├─ [Group 1] Running 2 tasks...
   │  ├─ Set up database schema ✅ (8,200 tokens)
   │  └─ Configure auth middleware ✅ (6,100 tokens)
   ├─ [Group 2] Running 1 task...
   │  └─ Create user model ✅ (4,800 tokens)
   ├─ ✅ Checkpoint passed
   ├─ 📝 Commit: a1b2c3d
   └─ Phase complete: 19,100/20,000 tokens (-4.5%)

📦 Phase 2/4: Core Authentication (4 tasks)
   ├─ [Group 1] Running 2 tasks...
   │  ├─ Implement login endpoint ✅ (12,400 tokens)
   │  └─ Implement register endpoint ✅ (11,200 tokens)
   ├─ [Group 2] Running 2 tasks...
   │  ├─ Add password hashing ✅ (5,600 tokens)
   │  └─ Create JWT utilities ✅ (7,300 tokens)
   ├─ ✅ Checkpoint passed
   ├─ 📝 Commit: d4e5f6g
   └─ Phase complete: 36,500/40,000 tokens (-8.8%) | Returns: jwtAlgorithm=RS256

📦 Phase 3/4: Session Management (3 tasks)
   ├─ [Group 1] Running 3 tasks...
   │  ├─ Create session store ✅ (9,800 tokens)
   │  ├─ Implement refresh tokens ✅ (11,100 tokens)
   │  └─ Add session middleware ✅ (7,200 tokens)
   ├─ ✅ Checkpoint passed
   ├─ 📝 Commit: e5f6g7h
   └─ Phase complete: 28,100/30,000 tokens (-6.3%) | Returns: sessionTTL=3600

📦 Phase 4/4: Testing & Validation (2 tasks)
   ├─ [Group 1] Running 2 tasks...
   │  ├─ Write auth unit tests ✅ (18,200 tokens)
   │  └─ Write integration tests ✅ (14,500 tokens)
   ├─ ✅ Checkpoint passed
   ├─ 📝 Commit: f6g7h8i
   └─ Phase complete: 32,700/35,000 tokens (-6.6%) | Returns: testCoverage=94.2%, testsPass=true

✅ Execution completed!

📊 Summary:
   Phases: 4/4 completed
   Tasks: 12/12 completed
   Tokens: 116,400/125,000 (-6.9% under budget)
   Duration: 4m 32s

📄 Log: specs/auth-system/execution-log.toon
📝 Final commit: h7i8j9k "feat(auth): implement user authentication system"
```
</example>
