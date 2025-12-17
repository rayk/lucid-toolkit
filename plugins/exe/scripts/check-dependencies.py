#!/usr/bin/env python3
"""
Check execution plan for dependency cycles and violations.

Validates:
- No circular dependencies in the dependency graph
- No dependencies on tasks in the same parallel group
- No dependencies on tasks that execute later
- All referenced tasks exist

Exit codes:
    0 - No dependency issues found
    1 - Dependency violations detected
    2 - Usage error or file not found
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import NamedTuple


class Task(NamedTuple):
    id: str
    parallel_group: int
    phase_order: int


class DependencyResult(NamedTuple):
    valid: bool
    errors: list[str]
    warnings: list[str]
    task_count: int
    dependency_count: int


def parse_execution_plan(content: str) -> tuple[dict[str, Task], list[tuple[str, str, str]]]:
    """
    Parse execution plan to extract tasks and dependencies.

    Returns:
        tasks: dict mapping task_id to Task info
        dependencies: list of (task_id, depends_on, reason) tuples
    """
    tasks = {}
    dependencies = []
    lines = content.split('\n')

    current_phase = None
    current_phase_order = 0
    in_tasks_block = False
    in_deps_block = False

    for line in lines:
        stripped = line.strip()

        # Detect phase blocks
        phase_match = re.match(r'^(phase-[\w-]+):', stripped)
        if phase_match:
            current_phase = phase_match.group(1)

        # Detect phase order
        order_match = re.match(r'^\s*order:\s*(\d+)', line)
        if order_match and current_phase:
            current_phase_order = int(order_match.group(1))

        # Detect tasks array header
        if re.match(r'^\s*tasks\[\d+,?\]', line):
            in_tasks_block = True
            in_deps_block = False
            continue

        # Detect dependencies array header
        if re.match(r'^\s*dependencies\[\d+,?\]', line):
            in_deps_block = True
            in_tasks_block = False
            continue

        # End blocks on new section
        if re.match(r'^\s*\w+\[.*?\]:', line) and 'tasks[' not in line and 'dependencies[' not in line:
            in_tasks_block = False
            in_deps_block = False

        # Parse task rows: Action,{task-id},{name},{type},{complexity},{model},{agent},{tokens},{%},{group},Status
        if in_tasks_block and stripped.startswith('Action,'):
            parts = stripped.split(',')
            if len(parts) >= 10:
                task_id = parts[1].strip()
                try:
                    parallel_group = int(parts[9].strip())
                except (ValueError, IndexError):
                    parallel_group = 0
                tasks[task_id] = Task(
                    id=task_id,
                    parallel_group=parallel_group,
                    phase_order=current_phase_order
                )

        # Parse dependency rows: {task-id},{dependency-task-id},{reason}
        if in_deps_block and ',' in stripped and not stripped.startswith('#'):
            parts = stripped.split(',', 2)
            if len(parts) >= 2:
                task_id = parts[0].strip()
                depends_on = parts[1].strip()
                reason = parts[2].strip() if len(parts) > 2 else ''
                if task_id and depends_on:
                    dependencies.append((task_id, depends_on, reason))

    return tasks, dependencies


def find_cycles(dependencies: list[tuple[str, str, str]]) -> list[list[str]]:
    """
    Find all cycles in the dependency graph using DFS.

    Returns list of cycles, where each cycle is a list of task IDs.
    """
    # Build adjacency list
    graph = defaultdict(list)
    for task_id, depends_on, _ in dependencies:
        graph[task_id].append(depends_on)

    # All nodes in the graph
    all_nodes = set(graph.keys())
    for task_id, depends_on, _ in dependencies:
        all_nodes.add(depends_on)

    cycles = []
    visited = set()
    rec_stack = set()
    path = []

    def dfs(node):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in rec_stack:
                # Found cycle - extract it from path
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                cycles.append(cycle)
                return True

        path.pop()
        rec_stack.remove(node)
        return False

    for node in all_nodes:
        if node not in visited:
            dfs(node)

    return cycles


def check_dependencies(content: str, filepath: str) -> DependencyResult:
    """Validate dependencies in an execution plan."""
    errors = []
    warnings = []

    tasks, dependencies = parse_execution_plan(content)

    if not tasks:
        return DependencyResult(False, ["No tasks found in execution plan"], [], 0, 0)

    # Check for cycles
    cycles = find_cycles(dependencies)
    for cycle in cycles:
        cycle_str = ' -> '.join(cycle)
        errors.append(f"Circular dependency detected: {cycle_str}")

    # Check each dependency
    for task_id, depends_on, reason in dependencies:
        # Check task exists
        if task_id not in tasks:
            errors.append(f"Unknown task in dependency: {task_id}")
            continue

        if depends_on not in tasks:
            errors.append(f"Dependency references unknown task: {depends_on}")
            continue

        task = tasks[task_id]
        dep_task = tasks[depends_on]

        # Check same parallel group violation
        if task.parallel_group != 0 and task.parallel_group == dep_task.parallel_group:
            errors.append(
                f"Task '{task_id}' depends on '{depends_on}' in same parallel group {task.parallel_group}"
            )

        # Check execution order (can't depend on later task)
        if dep_task.phase_order > task.phase_order:
            errors.append(
                f"Task '{task_id}' (phase {task.phase_order}) depends on '{depends_on}' "
                f"which executes later (phase {dep_task.phase_order})"
            )

    # Check for orphan tasks (no dependencies but not in first phase)
    first_phase_order = min((t.phase_order for t in tasks.values()), default=1)
    dependent_tasks = {task_id for task_id, _, _ in dependencies}

    for task_id, task in tasks.items():
        if task.phase_order > first_phase_order and task_id not in dependent_tasks:
            warnings.append(
                f"Task '{task_id}' in phase {task.phase_order} has no dependencies - "
                f"verify this is intentional"
            )

    return DependencyResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        task_count=len(tasks),
        dependency_count=len(dependencies)
    )


def main():
    parser = argparse.ArgumentParser(
        description='Check execution plan for dependency cycles and violations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s execution-plan.toon
    %(prog)s specs/auth-plan.toon --strict
    %(prog)s *.toon --quiet
        """
    )
    parser.add_argument('files', nargs='+', type=Path, help='Execution plan file(s) to check')
    parser.add_argument('--strict', action='store_true', help='Treat warnings as errors')
    parser.add_argument('--quiet', '-q', action='store_true', help='Only output on error')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show task and dependency counts')

    args = parser.parse_args()

    all_valid = True

    for filepath in args.files:
        if not filepath.exists():
            print(f"ERROR: File not found: {filepath}", file=sys.stderr)
            all_valid = False
            continue

        try:
            content = filepath.read_text(encoding='utf-8')
        except Exception as e:
            print(f"ERROR: Failed to read {filepath}: {e}", file=sys.stderr)
            all_valid = False
            continue

        result = check_dependencies(content, str(filepath))

        if args.strict and result.warnings:
            result = DependencyResult(
                False,
                result.errors + result.warnings,
                [],
                result.task_count,
                result.dependency_count
            )

        if not result.valid:
            all_valid = False
            print(f"INVALID: {filepath}", file=sys.stderr)
            for error in result.errors:
                print(f"  ERROR: {error}", file=sys.stderr)
            for warning in result.warnings:
                print(f"  WARNING: {warning}", file=sys.stderr)
        elif not args.quiet:
            print(f"VALID: {filepath}")
            if args.verbose:
                print(f"  Tasks: {result.task_count}, Dependencies: {result.dependency_count}")
            for warning in result.warnings:
                print(f"  WARNING: {warning}")

    sys.exit(0 if all_valid else 1)


if __name__ == '__main__':
    main()
