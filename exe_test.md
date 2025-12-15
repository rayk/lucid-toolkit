1. Analyze Request: break down the user's request and outline phases.
2. Create a Plan: Before writing any code, generate a detailed execution plan and save it as `.junie_plans/{timestamp}-{slug}.md`. The plan must outline:
* Files to create or modify.
* High-level changes per file.
* Tests to add or update.
* Acceptance criteria and verification commands.
3. Lock and Execute: Once the plan is approved, stick to it and execute in phases. If blocking issues arise, pause and request approval for any plan changes.
4. Plan Hierarchy & Anti-Drift Rule:
* Assign a stable Plan ID to the main plan for the task: `X` (e.g., `1`). All sub-plans must derive from this ID.
* Number sub-plans as `X.y` for step `y` of the main plan; deeper levels continue as `X.y.z` and so on.
* At the start of any sub-plan, record its parent path (breadcrumb) explicitly: `Parent: X` or `Parent: X.y`.
* After completing a sub-plan, immediately return to its parent plan and reconcile:
- Update the parent's status for the corresponding step.
- Verify the parent's acceptance criteria affected by the sub-plan.
- Ensure no sibling subtasks are left untracked.
* Never start a new top-level plan while `X` is active. If scope changes, request approval to revise `X` rather than creating a new top-level plan.
* In all status updates and PR descriptions, include the active path (e.g., `Active path: X -> X.2 -> X.2.1`).
* Close the main plan `X` only after all direct steps and sub-plans under its hierarchy are marked complete and verified.
