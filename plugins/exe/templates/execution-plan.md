# Execution Plan Template

> **Template:** [`execution-plan.toon`](execution-plan.toon) ← read template first

Supplementary field documentation. Consult only when field details needed.

## Overview

An execution plan transforms a technical specification into executable tasks organized in sequential phases.

## Plan Structure

```
execution-plan
├── header (type, id, name, status, log path)
├── source (spec reference with version)
├── metadata (counts, tokens, probability)
├── commitMessage (assembled on success)
├── phases[P] (sequential list)
│   └── {phase-id} (repeat for each)
│       ├── tasks[N]
│       ├── taskDetails[N]
│       ├── taskInputs[I]
│       ├── taskOutputs[O]
│       ├── taskReturns[R]
│       └── checkpoint
├── dependencies[D]
└── executionOrder[N]
```

## Status Values

| Status | Description |
|--------|-------------|
| `Draft` | Plan being created, not yet validated |
| `Ready` | Validated and approved for execution |
| `Running` | Execution in progress |
| `Completed` | All phases and tasks finished successfully |
| `Failed` | Execution stopped due to unrecoverable error |

## Phase Fields

| Field | Description |
|-------|-------------|
| `order` | Position in sequence (1..P) |
| `category` | `infrastructure` \| `component` \| `integration` \| `verification` |
| `commitSubject` | Single-line summary for squash commit |
| `estimatedTokens` | Total tokens for all tasks in phase |
| `varianceBudget` | Buffer % for retries/errors (e.g., 15 = 15%) |

## Task Fields

| Field | Values |
|-------|--------|
| `type` | `infrastructure` \| `configuration` \| `behaviour` \| `integration` \| `verification` |
| `complexity` | `trivial` \| `standard` \| `complex` |
| `model` | `haiku` \| `sonnet` \| `opus` |
| `agent` | `general-purpose` \| `Explore` \| `Plan` \| `{plugin}:{agent}` |
| `tokens` | Estimated token consumption |
| `variance` | Buffer % for retries/errors |
| `parallelGroup` | Execution group (0 = sequential) |
| `status` | `PotentialActionStatus` \| `ActiveActionStatus` \| `CompletedActionStatus` \| `FailedActionStatus` |

## Parallel Execution

Tasks with the same `parallelGroup` run concurrently. Groups execute sequentially.

```
parallelGroup: 1,1,1,2,0

task-a (1) ─┬─→ task-d (2) → task-e (0)
task-b (1) ─┤
task-c (1) ─┘
```

## Task Inputs

Three source types:

| Source | Format | Description |
|--------|--------|-------------|
| `static` | `{path}` | Existing file in project |
| `output` | `{taskId}.outputs.{path}` | Path produced by previous task |
| `return` | `{taskId}.returns.{key}` | Value returned by previous task |

### Dependency Rules

**Violations = plan error:**
- ✗ Cannot depend on task in same `parallelGroup`
- ✗ Cannot depend on task that executes later
- ✓ Can depend on earlier groups or previous phases

## Task Outputs

| Type | Description |
|------|-------------|
| `doc` | Documentation |
| `source` | Source code |
| `test` | Test files |
| `config` | Configuration |
| `asset` | Images, fonts, resources |
| `other` | Any other artifact |

## Task Returns (Optional)

Key-value data returned for executor consumption. Not mandatory.

Common examples:
- `testCoverage` (number) - Coverage percentage
- `tokensConsumed` (number) - Actual tokens used
- `toolUseCount` (number) - Tool invocations
- `testsPass` (boolean) - All tests green
- `lintErrors` (number) - Remaining lint issues

Value types: `string` | `number` | `boolean` | `path` | `list`

## Checkpoint

Final step in phase - executes only after ALL tasks complete.

| Field | Values |
|-------|--------|
| `onPass` | `continue` \| `commit` \| `notify` |
| `onFail` | `rollback` \| `pause` \| `fail` |

## Commit Message

Assembled on successful completion from phase `commitSubject` lines.

Types: `feat` | `fix` | `refactor` | `docs` | `test` | `chore` | `perf` | `build`

```
{type}({scope}): {description}

- {phase-1-commitSubject}
- {phase-2-commitSubject}
- {phase-N-commitSubject}

Refs: {spec-id}
```

## Examples

### Minimal (3 phases)

```toon
phases[3]: phase-infrastructure,phase-auth,phase-verification
```

### Complex (6 phases)

```toon
phases[6]: phase-infrastructure,phase-user-mgmt,phase-billing,phase-notifications,phase-integration,phase-verification
```

Execution: `Infrastructure → User Mgmt → Billing → Notifications → Integration → Verification`
