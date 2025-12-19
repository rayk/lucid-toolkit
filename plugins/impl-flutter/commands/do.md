---
name: do
description: Execute an execution-plan.toon file, running Flutter implementation tasks phase-by-phase with parallel groups
argument-hint: <execution-plan-path> [--resume <resume-point-path>]
allowed-tools: Task
---

<critical_behavior>
## MANDATORY: Delegate ALL Operations

This command MUST delegate ALL work to subagents. You are a thin dispatcher.

**TOKEN COUNTING MODEL:**
- Only tokens RETURNED from subagents count against YOUR context
- Subagents work in isolated contexts - their internal token usage doesn't affect you
- Your context budget is for: receiving summaries, deciding next action, dispatching
- The plan must complete within 85% of YOUR context (based on returned tokens only)

**PROHIBITED ACTIONS:**
- DO NOT use Read tool to read the plan file yourself
- DO NOT use Write tool to write execution-log.toon yourself
- DO NOT use Bash for git operations yourself
- DO NOT use Edit or Glob for any purpose
- DO NOT analyze task outputs yourself
- DO NOT read any file contents into your context

**REQUIRED PATTERN:**
Every operation is a Task call to a subagent:
1. `Task(impl-flutter:do-plan-reader)` → returns plan summary (phases, tasks, tokens)
2. For each phase: `Task({agent})` → returns task result summary
3. `Task(impl-flutter:do-log-writer)` → writes log entry, returns confirmation
4. `Task(impl-flutter:do-git-ops)` → commits, returns sha
5. `Task(impl-flutter:do-checkpoint-validator)` → validates, returns pass/fail

If you find yourself reading files or writing directly, STOP. You are violating the design.
</critical_behavior>

<arguments>
- `$1` — Path to execution-plan.toon file
- `--resume $2` — (Optional) Path to resume-continuation-point.md
</arguments>

<token_budget>
## Context Budget Model

**Your budget (orchestrator):**
- Plan summary reception: ~500 tokens
- Per-task result reception: ~100-200 tokens each
- Log write confirmations: ~50 tokens each
- Git confirmations: ~50 tokens each
- Decision overhead: ~50 tokens per phase

**Example 20-task plan:**
- Plan summary: 500 tokens
- Task results: 20 × 150 = 3,000 tokens
- Log writes: 20 × 50 = 1,000 tokens
- Git ops: 5 × 50 = 250 tokens
- Decisions: 5 × 50 = 250 tokens
- **Total: ~5,000 tokens** (orchestrator context)

The actual implementation work (potentially 500K+ tokens) happens in subagent contexts.

**85% Rule:**
If your context reaches 85%, STOP and create resume point via:
`Task(impl-flutter:do-resume-writer)`
</token_budget>

<execution_flow>
## Execution Flow (All Via Task Calls)

### 1. Load Plan
```
Task(impl-flutter:do-plan-reader):
  "Read plan at: $1
   Return: phases[], tasks[], dependencies, totalTokens, checkpoints"
```
Receive: Structured summary (NOT file contents)

### 2. Handle Resume (if --resume)
```
Task(impl-flutter:do-resume-reader):
  "Read resume point at: $2
   Return: lastCompletedPhase, lastCompletedTask, gitState"
```
Receive: Resume state summary

### 3. Initialize Log
```
Task(impl-flutter:do-log-writer):
  "Initialize log at: {plan-directory}/execution-log.toon
   Plan: {plan-summary}
   Status: Running
   Return: confirmation"
```

### 4. Execute Phases
For each phase (from startPhase):

**a. Context Check**
Estimate tokens for phase results. If approaching 85%:
```
Task(impl-flutter:do-resume-writer):
  "Create resume point at: {plan-directory}/
   State: {current-state}
   Return: resume-point-path"
```
Then STOP.

**b. Execute Tasks (parallel groups)**
For each parallel group, launch ALL tasks in ONE message:
```
Task(impl-flutter:flutter-coder): "Implement: {task-1}..."
Task(impl-flutter:flutter-coder): "Implement: {task-2}..."
Task(impl-flutter:flutter-ux-widget): "Implement: {task-3}..."
```
Receive: Result summaries (status, tokensUsed, filesCreated)

**c. Record Results**
```
Task(impl-flutter:do-log-writer):
  "Update log: {plan-directory}/execution-log.toon
   Phase: {phase-id}
   Tasks: {task-results}
   Return: confirmation"
```

**d. Validate Checkpoint**
```
Task(impl-flutter:do-checkpoint-validator):
  "Validate checkpoint for phase: {phase-id}
   Criteria: {checkpoint-criteria}
   Return: pass/fail, details"
```

**e. Git Commit**
```
Task(impl-flutter:do-git-ops):
  "Commit phase: {phase-id}
   Files: {output-paths}
   Message: {commit-subject}
   Return: sha, success"
```

### 5. Finalize
```
Task(impl-flutter:do-log-writer):
  "Finalize log: {plan-directory}/execution-log.toon
   Status: Completed
   Summary: {totals}
   Return: confirmation"

Task(impl-flutter:do-git-ops):
  "Final commit
   Message: {plan-commit-message}
   Return: sha"
```
</execution_flow>

<helper_agents>
## Helper Agents (for orchestrator operations)

| Agent | Purpose | Returns |
|-------|---------|---------|
| impl-flutter:do-plan-reader | Read and parse plan | Structured summary |
| impl-flutter:do-log-writer | Write execution log | Confirmation |
| impl-flutter:do-git-ops | Git commit/rollback | SHA, status |
| impl-flutter:do-checkpoint-validator | Validate checkpoints | Pass/fail |
| impl-flutter:do-resume-writer | Create resume point | Path |
| impl-flutter:do-resume-reader | Read resume point | State |

These agents do the actual I/O. You only receive summaries.
</helper_agents>

<implementation_agents>
## Implementation Agents (for actual work)

| Agent | Use For | Model |
|-------|---------|-------|
| impl-flutter:flutter-coder | Domain, application, widgets, tests | sonnet |
| impl-flutter:flutter-ux-widget | Visual widgets, animations, a11y | opus |
| impl-flutter:flutter-e2e-tester | E2E tests, integration tests | opus |
| impl-flutter:flutter-verifier | Code review, compliance | opus |
| Explore | Codebase exploration | haiku |
| general-purpose | Multi-step research | sonnet |
</implementation_agents>

<task_prompts>
## Task Prompt Construction

When dispatching implementation tasks, construct prompts from plan data:

### impl-flutter:flutter-coder
```
Task(impl-flutter:flutter-coder):
"Implement: {task.name}

Required Inputs:
- projectRoot: {agentInputs.projectRoot}
- targetPaths: {agentInputs.targetPaths}
- architectureRef: {agentInputs.architectureRef}
- spec: {agentInputs.spec}

Acceptance Criteria:
{taskDetails.acceptance}

Token Budget: {task.tokens}

Return: status, filesCreated, testsPassed, analyzerClean, tokensUsed, error"
```

### impl-flutter:flutter-ux-widget
```
Task(impl-flutter:flutter-ux-widget):
"Implement widget: {task.name}

Required Inputs:
- projectRoot: {agentInputs.projectRoot}
- targetPaths: {agentInputs.targetPaths}
- architectureRef: {agentInputs.architectureRef}
- designSpec: {agentInputs.designSpec}
- spec: {agentInputs.spec}

Acceptance Criteria:
{taskDetails.acceptance}

Token Budget: {task.tokens}

Return: status, filesCreated, testsPassed, analyzerClean, tokensUsed, error"
```

### impl-flutter:flutter-e2e-tester
```
Task(impl-flutter:flutter-e2e-tester):
"Write E2E tests: {task.name}

Required Inputs:
- projectRoot: {agentInputs.projectRoot}
- userFlowSpec: {agentInputs.userFlowSpec}
- targetPaths: {agentInputs.targetPaths}

Acceptance Criteria:
{taskDetails.acceptance}

Token Budget: {task.tokens}

Return: status, filesCreated, testsWritten, tokensUsed, error"
```

### impl-flutter:flutter-verifier
```
Task(impl-flutter:flutter-verifier):
"Verify: {task.name}

Required Inputs:
- projectRoot: {agentInputs.projectRoot}
- architectureRef: {agentInputs.architectureRef}
- filePaths: {agentInputs.filePaths}

Verification Criteria:
{taskDetails.acceptance}

Token Budget: {task.tokens}

Return: status, violations, compliant, tokensUsed, error"
```
</task_prompts>

<progress_reporting>
## Progress Output

Report based on subagent return summaries:

**Start:** `🚀 Executing: {plan-name} | {phases} phases, {tasks} tasks`
**Phase:** `🔷 Phase {N}/{total}: {name}`
**Task:** `✅ {task-name} ({tokens} tokens)` or `❌ {task-name}: {error}`
**Checkpoint:** `✓ Checkpoint passed` or `✗ Checkpoint failed`
**Commit:** `💾 Commit: {sha}`
**Pause:** `⏸️ Context at 85%, resume point saved`
**Complete:** `✅ Complete! {tasks} tasks, {tokens} tokens`
</progress_reporting>

<failure_handling>
## Failure Handling

**Task Failure:** Record via do-log-writer, continue to checkpoint
**Checkpoint Failure:** Based on onFail: pause/rollback/continue
**Context Limit:** Create resume point via do-resume-writer, STOP
**Unrecoverable:** Log failure, create resume point, report
</failure_handling>

<success_criteria>
- ALL operations delegated to subagents (no direct tool use)
- Only return summaries in orchestrator context
- Plan completes within 85% context OR resume point saved
- Execution log accurately tracks progress
- Git commits per phase
- Clean progress reporting
</success_criteria>
