#!/usr/bin/env python3
"""
Check coverage between a specification and an execution plan.

Extracts requirements/components from the spec and verifies each maps to
at least one task in the plan.

Exit codes:
    0 - Full coverage
    1 - Coverage gaps found
    2 - Usage error or file not found
"""

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple


class CoverageResult(NamedTuple):
    covered: list[str]
    uncovered: list[str]
    orphan_tasks: list[str]  # Tasks that don't map to any spec item


def extract_spec_items(content: str, filepath: Path) -> list[tuple[str, str]]:
    """
    Extract plannable items from a specification.

    Returns list of (item_id, item_description) tuples.
    """
    items = []

    # Pattern 1: TOON components
    # components.item[].name: ComponentName
    for match in re.finditer(r'components?\.item\[\d*\]\.name:\s*(.+)', content):
        items.append((f"component:{match.group(1).strip()}", match.group(1).strip()))

    # Pattern 2: TOON acceptance criteria
    # acceptanceCriteria.item[N].identifier: AC-1
    for match in re.finditer(r'acceptanceCriteria\.item\[\d*\]\.identifier:\s*(AC-\d+)', content):
        items.append((match.group(1), f"Acceptance Criteria {match.group(1)}"))

    # Pattern 3: Markdown components section
    # ## Components followed by ### ComponentName
    in_components = False
    for line in content.split('\n'):
        if re.match(r'^#{1,2}\s*components?\s*$', line, re.IGNORECASE):
            in_components = True
            continue
        if in_components and re.match(r'^#{1,2}\s+[^#]', line):
            # New H2 section, end components
            in_components = False
        if in_components:
            h3_match = re.match(r'^###\s+(\w+)', line)
            if h3_match:
                name = h3_match.group(1)
                items.append((f"component:{name}", name))

    # Pattern 4: Markdown acceptance criteria
    # ### AC-1: or **AC-1**:
    for match in re.finditer(r'(?:^###\s*|\*\*)(AC-\d+)(?:\*\*)?[:\s]', content, re.MULTILINE):
        ac_id = match.group(1)
        if (ac_id, f"Acceptance Criteria {ac_id}") not in items:
            items.append((ac_id, f"Acceptance Criteria {ac_id}"))

    # Pattern 5: TOON contracts
    # contracts.item[].component: + contracts.item[].method:
    for match in re.finditer(r'contracts\.item\[\d*\]\.component:\s*(\w+)', content):
        comp = match.group(1).strip()
        if (f"component:{comp}", comp) not in items:
            items.append((f"component:{comp}", comp))

    # Pattern 6: TOON types
    # types.item[].name: TypeName
    for match in re.finditer(r'types\.item\[\d*\]\.name:\s*(\w+)', content):
        items.append((f"type:{match.group(1).strip()}", f"Type: {match.group(1).strip()}"))

    # Pattern 7: TOON file structure items
    # fileStructure.items[].path:
    for match in re.finditer(r'fileStructure\.items?\[\d*\]\.path:\s*(.+)', content):
        path = match.group(1).strip()
        items.append((f"file:{path}", f"File: {path}"))

    # Deduplicate
    seen = set()
    unique_items = []
    for item_id, desc in items:
        if item_id not in seen:
            seen.add(item_id)
            unique_items.append((item_id, desc))

    return unique_items


def extract_plan_coverage(content: str) -> list[tuple[str, str]]:
    """
    Extract task coverage info from a plan.

    Returns list of (task_id, task_description) tuples.
    """
    tasks = []

    # Parse taskDetails for descriptions
    # taskDetails[N,]{taskId,description,acceptance}:
    in_details = False
    for line in content.split('\n'):
        if re.match(r'^\s*taskDetails\[', line):
            in_details = True
            continue
        if in_details and re.match(r'^\s*\w+\[', line):
            in_details = False

        if in_details:
            stripped = line.strip()
            if ',' in stripped and not stripped.startswith('#'):
                parts = stripped.split(',', 2)
                if len(parts) >= 2:
                    task_id = parts[0].strip()
                    desc = parts[1].strip()
                    tasks.append((task_id, desc))

    return tasks


def check_coverage(spec_items: list[tuple[str, str]],
                   plan_tasks: list[tuple[str, str]]) -> CoverageResult:
    """
    Check if plan tasks cover spec items.

    Uses fuzzy matching - task description should mention component/type names.
    """
    covered = []
    uncovered = []
    task_matches = {task_id: False for task_id, _ in plan_tasks}

    for item_id, item_desc in spec_items:
        # Extract the key term to search for
        if item_id.startswith('component:'):
            search_term = item_id.split(':')[1].lower()
        elif item_id.startswith('type:'):
            search_term = item_id.split(':')[1].lower()
        elif item_id.startswith('file:'):
            search_term = Path(item_id.split(':')[1]).stem.lower()
        else:
            search_term = item_desc.lower()

        # Search for match in any task
        found = False
        for task_id, task_desc in plan_tasks:
            if search_term in task_desc.lower() or search_term in task_id.lower():
                found = True
                task_matches[task_id] = True
                break

        if found:
            covered.append(item_id)
        else:
            uncovered.append(item_id)

    # Find orphan tasks (don't match any spec item)
    orphans = [task_id for task_id, matched in task_matches.items() if not matched]

    return CoverageResult(covered=covered, uncovered=uncovered, orphan_tasks=orphans)


def main():
    parser = argparse.ArgumentParser(
        description='Check coverage between specification and execution plan',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Extracts from spec:
    - Components (TOON or markdown)
    - Acceptance criteria (AC-N)
    - Types
    - File structure items

Checks that each spec item maps to at least one plan task.

Examples:
    %(prog)s spec.md plan.toon
    %(prog)s spec.toon plan.toon --verbose
        """
    )
    parser.add_argument('spec', type=Path, help='Specification file (.md or .toon)')
    parser.add_argument('plan', type=Path, help='Execution plan file (.toon)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show coverage details')
    parser.add_argument('--orphans-ok', action='store_true',
                        help='Don\'t warn about tasks without spec mapping')

    args = parser.parse_args()

    # Read spec
    if not args.spec.exists():
        print(f"ERROR: Spec not found: {args.spec}", file=sys.stderr)
        sys.exit(2)

    try:
        spec_content = args.spec.read_text(encoding='utf-8')
    except Exception as e:
        print(f"ERROR: Failed to read spec: {e}", file=sys.stderr)
        sys.exit(2)

    # Read plan
    if not args.plan.exists():
        print(f"ERROR: Plan not found: {args.plan}", file=sys.stderr)
        sys.exit(2)

    try:
        plan_content = args.plan.read_text(encoding='utf-8')
    except Exception as e:
        print(f"ERROR: Failed to read plan: {e}", file=sys.stderr)
        sys.exit(2)

    # Extract items
    spec_items = extract_spec_items(spec_content, args.spec)
    plan_tasks = extract_plan_coverage(plan_content)

    if not spec_items:
        print("WARNING: No plannable items found in spec", file=sys.stderr)
        print("  (Looking for: components, acceptance criteria, types, files)")

    if not plan_tasks:
        print("ERROR: No tasks found in plan", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print(f"Spec items: {len(spec_items)}")
        print(f"Plan tasks: {len(plan_tasks)}")

    # Check coverage
    result = check_coverage(spec_items, plan_tasks)

    coverage_pct = (len(result.covered) / len(spec_items) * 100) if spec_items else 100

    if result.uncovered:
        print(f"COVERAGE GAP: {len(result.uncovered)}/{len(spec_items)} items uncovered ({coverage_pct:.0f}%)")
        for item_id in result.uncovered:
            print(f"  MISSING: {item_id}")
        sys.exit(1)
    else:
        print(f"FULL COVERAGE: {len(result.covered)} spec items mapped to tasks")

    if result.orphan_tasks and not args.orphans_ok:
        print(f"WARNING: {len(result.orphan_tasks)} tasks don't map to spec items")
        if args.verbose:
            for task_id in result.orphan_tasks:
                print(f"  ORPHAN: {task_id}")

    if args.verbose and result.covered:
        print("Covered items:")
        for item_id in result.covered:
            print(f"  ✓ {item_id}")

    sys.exit(0)


if __name__ == '__main__':
    main()
