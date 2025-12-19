---
name: plan
description: Create a verified execution plan from technical specs and architectural constraints
argument-hint: <spec-path> <constraints-path>
allowed-tools: Task
---

<objective>
Generate a verified execution plan for Flutter implementation by analyzing technical specifications and architectural constraints.

This command invokes the flutter-impl-planner agent which:
- Analyzes specs at `$1` and constraints at `$2`
- Decomposes work into agent-sized tasks (≤75% context each)
- Plans parallel execution where dependencies allow
- Validates 100% spec coverage before probability assessment
- Produces execution-plan.toon with ≥95% success probability

The plan enables coordinated execution by flutter-coder, flutter-e2e-tester, flutter-ux-widget, flutter-debugger, and other implementation agents.
</objective>

<context>
Project root: !`pwd`
</context>

<process>
1. Validate that spec path `$1` exists
2. Validate that constraints path `$2` exists
3. Launch flutter-impl-planner subagent with both paths
4. Wait for planning to complete
5. Report plan location and summary

If either path is missing, stop and inform the user.
</process>

<agent_invocation>
Invoke the planner with this Task call:

```
Task(impl-flutter:flutter-impl-planner)
Prompt: |
  Create an execution plan for Flutter implementation.

  **Technical Specification Path:** $1
  **Architectural Constraints Path:** $2
  **Project Root:** {current working directory}

  Follow your complete workflow:
  1. Validate inputs exist
  2. Launch parallel analyzers (specs, constraints, codebase, agent capabilities)
  3. Synthesize summaries into implementation units
  4. Build dependency graph
  5. Decompose into context-sized tasks
  6. Validate 100% spec coverage
  7. Run mental simulation (up to 5 rounds)
  8. If ≥95% probability: write execution-plan.toon and context files
  9. If <95% probability: explain blockers

  Return the plan location and a summary of:
  - Total phases and tasks
  - Estimated tokens and models
  - Success probability
  - Any warnings or caveats
```
</agent_invocation>

<success_criteria>
- Both input paths validated as existing
- flutter-impl-planner agent successfully invoked
- Plan produced with ≥95% success probability, OR
- Clear explanation of why planning failed with recommendations
- Plan location reported to user
</success_criteria>

<output>
On success, the planner creates:
- `execution-plan.toon` — The verified implementation plan
- `phase-{N}-task-{M}-context.md` — Consolidated context files for each task

All files are saved in the same directory as the specification.
</output>
