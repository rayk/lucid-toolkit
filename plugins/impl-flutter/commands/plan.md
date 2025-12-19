---
name: plan
description: Create a verified execution plan from technical specs and architectural constraints
argument-hint: <spec-path> <constraints-path>
allowed-tools: Task
---

<objective>
Generate a verified execution plan for Flutter implementation by analyzing technical specifications and architectural constraints.

This command invokes the flutter-plan-orchestrator which coordinates specialized subagents:
- plan-spec-analyzer (haiku) — Analyzes specs, returns structured summary
- plan-constraint-analyzer (haiku) — Analyzes constraints, returns rules
- plan-capability-mapper (haiku) — Maps agent capabilities
- plan-context-builder (haiku) — Creates consolidated context files
- plan-coverage-validator (sonnet) — Validates 100% spec coverage
- plan-simulator (opus) — Runs mental simulation for probability
- plan-writer (sonnet) — Generates execution-plan.toon

The orchestrator delegates ALL heavy work to subagents, protecting its context.
</objective>

<context>
Project root: !`pwd`
</context>

<process>
1. Validate that spec path `$1` exists
2. Validate that constraints path `$2` exists
3. Launch flutter-plan-orchestrator with both paths
4. Orchestrator launches parallel analyzers (Phase 1)
5. Orchestrator synthesizes and decomposes (Phases 2-4)
6. Coverage validation gate (must be 100%)
7. Mental simulation gate (must be ≥95%)
8. Plan written to disk
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
  5. Decompose into context-sized tasks
  6. Launch context consolidation
  7. Validate 100% spec coverage
  8. Run mental simulation (up to 5 rounds)
  9. If ≥95% probability: write execution-plan.toon
  10. Report results

  Return the plan location and a summary of:
  - Total phases and tasks
  - Estimated tokens and models
  - Success probability
  - Any warnings or caveats
```
</agent_invocation>

<success_criteria>
- Both input paths validated as existing
- Orchestrator successfully invoked
- All subagents complete their phases
- Coverage validation passes (100%)
- Simulation passes (≥95% probability)
- Plan produced with execution-plan.toon written
- OR: Clear explanation of why planning failed with recommendations
</success_criteria>

<output>
On success, the orchestrator creates:
- `execution-plan.toon` — The verified implementation plan
- `phase-{N}-task-{M}-context.md` — Consolidated context files for each task

All files are saved in the same directory as the specification.
</output>
