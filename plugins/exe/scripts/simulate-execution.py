#!/usr/bin/env python3
"""
Simulate execution of a plan to identify problems before actual execution.

Walks through the execution order and checks:
- Each task has all required inputs available at execution time
- Dependencies are satisfied before task runs
- Outputs are produced before they're consumed
- No circular waits or deadlocks

Exit codes:
    0 - Simulation passed
    1 - Problems detected
    2 - Usage error or file not found
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import NamedTuple


class TaskInfo(NamedTuple):
    id: str
    name: str
    agent: str
    parallel_group: int
    phase: str
    inputs: list[tuple[str, str, str]]  # (taskId, source, ref)
    outputs: list[tuple[str, str, str]]  # (taskId, path, type)
    returns: list[tuple[str, str, str, str]]  # (taskId, key, valueType, description)


class SimulationProblem(NamedTuple):
    task_id: str
    severity: str  # ERROR, WARNING
    category: str  # INPUT_MISSING, OUTPUT_UNUSED, DEPENDENCY_LATE, etc.
    message: str


def parse_plan(content: str) -> tuple[list[TaskInfo], list[str], dict[str, list[str]]]:
    """
    Parse execution plan to extract tasks, execution order, and dependencies.

    Returns:
        tasks: list of TaskInfo
        execution_order: list of task IDs in execution sequence
        dependencies: dict mapping task_id -> list of dependency task_ids
    """
    tasks = []
    execution_order = []
    dependencies = defaultdict(list)

    lines = content.split('\n')

    current_phase = None
    in_tasks = False
    in_task_inputs = False
    in_task_outputs = False
    in_task_returns = False
    in_deps = False
    in_exec_order = False

    task_map = {}  # task_id -> index in tasks list
    task_inputs = defaultdict(list)
    task_outputs = defaultdict(list)
    task_returns = defaultdict(list)

    for line in lines:
        stripped = line.strip()

        # Track current phase
        phase_match = re.match(r'^(phase-[\w-]+):', stripped)
        if phase_match:
            current_phase = phase_match.group(1)
            in_tasks = False
            in_task_inputs = False
            in_task_outputs = False
            in_task_returns = False

        # Detect section headers
        if re.match(r'^\s*tasks\[\d+', line):
            in_tasks = True
            in_task_inputs = False
            in_task_outputs = False
            in_task_returns = False
            continue
        if re.match(r'^\s*taskInputs\[', line):
            in_tasks = False
            in_task_inputs = True
            in_task_outputs = False
            in_task_returns = False
            continue
        if re.match(r'^\s*taskOutputs\[', line):
            in_tasks = False
            in_task_inputs = False
            in_task_outputs = True
            in_task_returns = False
            continue
        if re.match(r'^\s*taskReturns\[', line):
            in_tasks = False
            in_task_inputs = False
            in_task_outputs = False
            in_task_returns = True
            continue
        if re.match(r'^\s*dependencies\[\d+', line):
            in_deps = True
            in_tasks = False
            in_task_inputs = False
            in_task_outputs = False
            in_task_returns = False
            continue
        if re.match(r'^\s*executionOrder\[', line):
            in_exec_order = True
            in_deps = False
            # Parse inline execution order
            order_match = re.search(r'executionOrder\[\d+\]:\s*(.+)', line)
            if order_match:
                execution_order = [t.strip() for t in order_match.group(1).split(',')]
            continue

        # End sections on new major section
        if re.match(r'^[a-zA-Z]', stripped) and ':' in stripped:
            if not stripped.startswith('Action,'):
                in_tasks = False
                in_task_inputs = False
                in_task_outputs = False
                in_task_returns = False
                in_deps = False

        # Parse task rows
        if in_tasks and stripped.startswith('Action,'):
            parts = stripped.split(',')
            if len(parts) >= 10:
                task_id = parts[1].strip()
                task_name = parts[2].strip()
                agent = parts[6].strip()
                try:
                    parallel_group = int(parts[9].strip())
                except (ValueError, IndexError):
                    parallel_group = 0

                task_map[task_id] = len(tasks)
                tasks.append(TaskInfo(
                    id=task_id,
                    name=task_name,
                    agent=agent,
                    parallel_group=parallel_group,
                    phase=current_phase or 'unknown',
                    inputs=[],
                    outputs=[],
                    returns=[]
                ))

        # Parse task inputs: taskId,source,ref
        if in_task_inputs and ',' in stripped and not stripped.startswith('#'):
            parts = stripped.split(',', 2)
            if len(parts) >= 3:
                task_id = parts[0].strip()
                source = parts[1].strip()
                ref = parts[2].strip()
                task_inputs[task_id].append((task_id, source, ref))

        # Parse task outputs: taskId,path,type
        if in_task_outputs and ',' in stripped and not stripped.startswith('#'):
            parts = stripped.split(',', 2)
            if len(parts) >= 3:
                task_id = parts[0].strip()
                path = parts[1].strip()
                out_type = parts[2].strip()
                task_outputs[task_id].append((task_id, path, out_type))

        # Parse task returns: taskId,key,valueType,description
        if in_task_returns and ',' in stripped and not stripped.startswith('#'):
            parts = stripped.split(',', 3)
            if len(parts) >= 3:
                task_id = parts[0].strip()
                key = parts[1].strip()
                value_type = parts[2].strip()
                desc = parts[3].strip() if len(parts) > 3 else ''
                task_returns[task_id].append((task_id, key, value_type, desc))

        # Parse dependencies: taskId,dependsOn,reason
        if in_deps and ',' in stripped and not stripped.startswith('#'):
            parts = stripped.split(',', 2)
            if len(parts) >= 2:
                task_id = parts[0].strip()
                depends_on = parts[1].strip()
                if task_id and depends_on:
                    dependencies[task_id].append(depends_on)

    # Attach inputs/outputs/returns to tasks
    final_tasks = []
    for task in tasks:
        final_tasks.append(TaskInfo(
            id=task.id,
            name=task.name,
            agent=task.agent,
            parallel_group=task.parallel_group,
            phase=task.phase,
            inputs=task_inputs.get(task.id, []),
            outputs=task_outputs.get(task.id, []),
            returns=task_returns.get(task.id, [])
        ))

    return final_tasks, execution_order, dict(dependencies)


def simulate_execution(tasks: list[TaskInfo], execution_order: list[str],
                       dependencies: dict[str, list[str]]) -> list[SimulationProblem]:
    """
    Simulate plan execution and identify problems.
    """
    problems = []

    task_by_id = {t.id: t for t in tasks}

    # Track state during simulation
    completed_tasks = set()
    available_outputs = {}  # task_id.outputs.path -> True
    available_returns = {}  # task_id.returns.key -> True

    # Check execution order covers all tasks
    order_set = set(execution_order)
    all_task_ids = set(task_by_id.keys())

    missing_from_order = all_task_ids - order_set
    for task_id in missing_from_order:
        problems.append(SimulationProblem(
            task_id=task_id,
            severity='ERROR',
            category='MISSING_FROM_ORDER',
            message=f"Task not in executionOrder"
        ))

    extra_in_order = order_set - all_task_ids
    for task_id in extra_in_order:
        problems.append(SimulationProblem(
            task_id=task_id,
            severity='ERROR',
            category='UNKNOWN_TASK',
            message=f"Task in executionOrder but not defined"
        ))

    # Simulate execution
    for task_id in execution_order:
        if task_id not in task_by_id:
            continue

        task = task_by_id[task_id]

        # Check dependencies are satisfied
        for dep_id in dependencies.get(task_id, []):
            if dep_id not in completed_tasks:
                problems.append(SimulationProblem(
                    task_id=task_id,
                    severity='ERROR',
                    category='DEPENDENCY_NOT_MET',
                    message=f"Depends on '{dep_id}' which hasn't completed yet"
                ))

        # Check inputs are available
        for _, source, ref in task.inputs:
            if source == 'static':
                # Static inputs should exist in filesystem - can't check here
                pass
            elif source == 'output':
                # Format: taskId.outputs.path
                if ref not in available_outputs:
                    # Parse the ref to find source task
                    ref_match = re.match(r'(\w+[-\w]*)\.outputs\.(.+)', ref)
                    if ref_match:
                        source_task = ref_match.group(1)
                        if source_task not in completed_tasks:
                            problems.append(SimulationProblem(
                                task_id=task_id,
                                severity='ERROR',
                                category='INPUT_NOT_AVAILABLE',
                                message=f"Input '{ref}' not available - source task '{source_task}' not completed"
                            ))
            elif source == 'return':
                # Format: taskId.returns.key
                if ref not in available_returns:
                    ref_match = re.match(r'(\w+[-\w]*)\.returns\.(.+)', ref)
                    if ref_match:
                        source_task = ref_match.group(1)
                        if source_task not in completed_tasks:
                            problems.append(SimulationProblem(
                                task_id=task_id,
                                severity='ERROR',
                                category='INPUT_NOT_AVAILABLE',
                                message=f"Return value '{ref}' not available - source task '{source_task}' not completed"
                            ))

        # Mark task complete and register outputs/returns
        completed_tasks.add(task_id)

        for _, path, _ in task.outputs:
            available_outputs[f"{task_id}.outputs.{path}"] = True

        for _, key, _, _ in task.returns:
            available_returns[f"{task_id}.returns.{key}"] = True

    # Check for unused outputs (warning only)
    all_input_refs = set()
    for task in tasks:
        for _, source, ref in task.inputs:
            if source in ('output', 'return'):
                all_input_refs.add(ref)

    for task in tasks:
        for _, path, _ in task.outputs:
            output_ref = f"{task.id}.outputs.{path}"
            if output_ref not in all_input_refs:
                # Check if it's a final deliverable (last phase)
                problems.append(SimulationProblem(
                    task_id=task.id,
                    severity='WARNING',
                    category='OUTPUT_UNUSED',
                    message=f"Output '{path}' is never consumed by another task"
                ))

    return problems


def main():
    parser = argparse.ArgumentParser(
        description='Simulate execution of an execution plan to find problems',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Checks performed:
    - All tasks are in execution order
    - Dependencies are met before task runs
    - Inputs (outputs/returns from other tasks) are available
    - No orphan outputs (warnings only)

Examples:
    %(prog)s execution-plan.toon
    %(prog)s specs/auth-plan.toon --verbose
        """
    )
    parser.add_argument('file', type=Path, help='Execution plan file to simulate')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show simulation progress')
    parser.add_argument('--warnings-as-errors', '-W', action='store_true',
                        help='Treat warnings as errors')

    args = parser.parse_args()

    if not args.file.exists():
        print(f"ERROR: File not found: {args.file}", file=sys.stderr)
        sys.exit(2)

    try:
        content = args.file.read_text(encoding='utf-8')
    except Exception as e:
        print(f"ERROR: Failed to read {args.file}: {e}", file=sys.stderr)
        sys.exit(2)

    tasks, execution_order, dependencies = parse_plan(content)

    if args.verbose:
        print(f"Parsed: {len(tasks)} tasks, {len(execution_order)} in order, {len(dependencies)} with deps")

    if not tasks:
        print("ERROR: No tasks found in plan", file=sys.stderr)
        sys.exit(1)

    problems = simulate_execution(tasks, execution_order, dependencies)

    errors = [p for p in problems if p.severity == 'ERROR']
    warnings = [p for p in problems if p.severity == 'WARNING']

    if args.warnings_as_errors:
        errors.extend(warnings)
        warnings = []

    if errors:
        print(f"SIMULATION FAILED: {len(errors)} errors", file=sys.stderr)
        for p in errors:
            print(f"  [{p.category}] {p.task_id}: {p.message}", file=sys.stderr)

    if warnings:
        print(f"WARNINGS: {len(warnings)}")
        for p in warnings:
            print(f"  [{p.category}] {p.task_id}: {p.message}")

    if not errors:
        print(f"SIMULATION PASSED: {len(tasks)} tasks validated")
        if args.verbose:
            print(f"  Execution order: {' -> '.join(execution_order[:5])}{'...' if len(execution_order) > 5 else ''}")

    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
