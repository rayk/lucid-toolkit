---
name: plan
description: Generate an execution-plan.toon file from a tech specification, decomposing requirements into agent-executable tasks with validated dependencies
argument-hint: <spec-path>
allowed-tools: Task
---

<objective>
Generate a validated execution plan from the tech specification at `$ARGUMENTS`.

The plan will be validated for structural correctness and agent availability. Success probability is estimated based on validation checks passed.
</objective>

<process>
1. **Validate Input**
   - If `$ARGUMENTS` is empty, ask user for spec path
   - Confirm spec file exists at `$ARGUMENTS`
   - File must be `.md` (markdown) or `.toon` format
   - Run validation script:
     ```bash
     python3 plugins/exe/scripts/validate-spec.py "$ARGUMENTS"
     ```
   - If validation fails (exit code 1), report errors and stop

2. **Delegate to Execution Planner**
   Invoke the execution-planner agent with the spec path:
   ```
   Task(exe:execution-planner):
   "Generate an execution plan from the tech specification.

   Specification: $ARGUMENTS

   Output the plan to {spec-dir}/execution-plan.toon

   Return SUCCESS with plan location and metrics, or FAILURE with specific blockers."
   ```

3. **Report Result**
   - On SUCCESS: Report plan location and summary metrics
   - On FAILURE: Report blockers and ask user for clarification
</process>

<success_criteria>
- Spec file validated
- execution-planner agent invoked with correct spec path
- Plan file written to spec directory
- Result reported to user with metrics or blockers
</success_criteria>

<example>
User: `/plan specs/auth-system.toon`

Assistant invokes:
```
Task(exe:execution-planner):
"Generate an execution plan from the tech specification.

Specification: specs/auth-system.toon

Output the plan to specs/execution-plan.toon

Return SUCCESS with plan location and metrics, or FAILURE with specific blockers."
```

Result:
```
✅ Execution plan generated

Location: specs/execution-plan.toon
Tasks: 12
Phases: 4
Estimated tokens: 245,000
Success probability: 0.96
```
</example>
