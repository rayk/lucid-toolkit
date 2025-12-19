---
name: plan
description: Create a verified execution plan from technical specs and architectural constraints
argument-hint: <spec-path> <constraints-path> <output-dir>
allowed-tools: Task
---

<critical_behavior>
## MANDATORY: Delegate to Orchestrator

This command MUST delegate ALL work to the orchestrator. You are a thin dispatcher.

**PROHIBITED ACTIONS:**
- DO NOT use Read tool to examine specs or constraints
- DO NOT use Glob or Grep to explore the codebase
- DO NOT use Write tool to create the plan yourself
- DO NOT use Bash except for the path validation below
- DO NOT analyze, synthesize, or decompose tasks yourself

**REQUIRED ACTION:**
1. Validate all three paths exist (single Bash call)
2. Invoke Task(impl-flutter:flutter-plan-orchestrator) with the paths
3. Report the orchestrator's result

If you find yourself reading files or writing plans directly, STOP. You are violating this command's design.
</critical_behavior>

<arguments>
All three arguments are REQUIRED:

- `$1` — **Specification Path**: Path to technical specification (file or directory)
- `$2` — **Constraints Path**: Path to architectural constraints (file or directory)
- `$3` — **Output Directory**: Path where all outputs will be written:
  - `execution-plan.toon` — The verified implementation plan
  - `execution-log.toon` — Execution log (created by /do command)
  - `phase-{N}-task-{M}-context.md` — Consolidated context files for each task
</arguments>

<validation>
Before invoking the orchestrator, validate ALL THREE paths:

```bash
test -e "$1" && test -e "$2" && test -d "$3" && echo "VALID" || echo "INVALID"
```

If INVALID:
- Check which path is missing or invalid
- For output directory ($3): create it if it doesn't exist, or inform user
- Stop and report the specific issue to the user
</validation>

<invocation>
After validation passes, invoke the orchestrator with a SINGLE Task call:

```
Task(impl-flutter:flutter-plan-orchestrator)
Prompt: |
  Create an execution plan for Flutter implementation.

  Specification Path: $1
  Constraints Path: $2
  Output Directory: $3
  Project Root: {pwd}

  All outputs go to Output Directory:
  - execution-plan.toon
  - phase-*-task-*-context.md files

  Execute your full workflow:
  1. Validate inputs
  2. Launch parallel analyzers
  3. Synthesize and decompose
  4. Validate coverage (100% gate)
  5. Run mental simulation (95% gate)
  6. Write execution-plan.toon to output directory

  Return: plan location, task count, phases, probability, warnings
```

Wait for the orchestrator to complete, then report its summary to the user.
</invocation>

<output>
Report the orchestrator's result:
- Plan file location (`$3/execution-plan.toon`)
- Number of phases and tasks
- Success probability
- Any warnings or recommendations
- Command to execute: `/do $3/execution-plan.toon`
</output>
