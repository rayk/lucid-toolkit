#!/usr/bin/env python3
"""
Validate @ references in .claude/ instruction files.
Usage: python3 scripts/validate_refs.py [--fix]
"""

import os
import re
import sys
from pathlib import Path


def find_at_references(content: str) -> list[tuple[int, str]]:
    """Find all @path references in content with line numbers."""
    refs = []

    # Schema.org vocabulary keywords to ignore (used in structured prompts)
    schema_keywords = {
        'type', 'return', 'constraints', 'context', 'about',
        'task', 'param', 'example', 'note', 'see', 'deprecated',
        'author', 'since', 'version', 'throws', 'property'
    }

    for i, line in enumerate(content.split('\n'), 1):
        # Skip lines inside code blocks (basic heuristic)
        stripped = line.strip()
        if stripped.startswith('```') or stripped.startswith('#'):
            continue

        # Match @path patterns - must contain a slash to be a file reference
        # or end with a file extension
        matches = re.findall(r'@([a-zA-Z0-9_./-]+)', line)
        for match in matches:
            # Skip schema.org vocabulary keywords
            if match.lower() in schema_keywords:
                continue

            # Skip email-like patterns
            if match.endswith('.com') or match.endswith('.org'):
                continue

            # Skip single word without slash (likely annotation, not file ref)
            # Also skip single filenames without path (like @package.json in docs)
            if '/' not in match:
                continue

            # Skip patterns that start with - (like @-something)
            if match.startswith('-'):
                continue

            refs.append((i, match))
    return refs


def resolve_reference(ref: str, base_dir: Path) -> Path | None:
    """Resolve @ reference to actual file path."""
    # Normalize the reference path - only strip leading ./ not .
    if ref.startswith('./'):
        ref = ref[2:]

    # Build list of candidate paths to check
    candidates = []

    # Handle various reference formats
    if ref.startswith('.claude/'):
        # Already has .claude/ prefix
        candidates.append(base_dir / ref)
    elif ref.startswith('skills/') or ref.startswith('commands/') or ref.startswith('agents/'):
        # Direct path within .claude/
        candidates.append(base_dir / '.claude' / ref)
    elif ref.startswith('status/') or ref.startswith('research/') or ref.startswith('capabilities/') or ref.startswith('outcomes/'):
        # Workspace root level directories
        candidates.append(base_dir / ref)
    elif ref == 'project_map.json' or ref.endswith('.json') and '/' not in ref:
        # Root-level files
        candidates.append(base_dir / ref)
    else:
        # Try multiple locations
        candidates.extend([
            base_dir / ref,  # Try workspace root first
            base_dir / '.claude' / ref,
            base_dir / '.claude' / 'skills' / ref,
            base_dir / '.claude' / 'commands' / ref,
            base_dir / '.claude' / 'agents' / ref,
        ])

    # Also check if it's a directory reference (for skills)
    for candidate in candidates.copy():
        if not candidate.suffix:  # No file extension
            candidates.append(candidate / 'SKILL.md')
            candidates.append(candidate / 'README.md')

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def validate_file(file_path: Path, base_dir: Path) -> list[dict]:
    """Validate all @ references in a file."""
    issues = []
    try:
        content = file_path.read_text()
    except Exception as e:
        issues.append({
            'file': str(file_path.relative_to(base_dir)),
            'line': 0,
            'reference': '',
            'status': 'ERROR',
            'message': str(e)
        })
        return issues

    refs = find_at_references(content)

    for line_num, ref in refs:
        resolved = resolve_reference(ref, base_dir)
        if resolved is None:
            issues.append({
                'file': str(file_path.relative_to(base_dir)),
                'line': line_num,
                'reference': ref,
                'status': 'BROKEN'
            })
    return issues


def main():
    base_dir = Path.cwd()
    claude_dir = base_dir / '.claude'

    if not claude_dir.exists():
        print("ERROR: .claude/ directory not found")
        sys.exit(1)

    all_issues = []
    files_checked = 0

    # Check agents
    agents_dir = claude_dir / 'agents'
    if agents_dir.exists():
        for agent_file in agents_dir.glob('*.md'):
            files_checked += 1
            all_issues.extend(validate_file(agent_file, base_dir))

    # Check skills
    skills_dir = claude_dir / 'skills'
    if skills_dir.exists():
        for skill_file in skills_dir.glob('*/SKILL.md'):
            files_checked += 1
            all_issues.extend(validate_file(skill_file, base_dir))
        # Also check reference files
        for ref_file in skills_dir.glob('*/references/*.md'):
            files_checked += 1
            all_issues.extend(validate_file(ref_file, base_dir))

    # Check commands
    commands_dir = claude_dir / 'commands'
    if commands_dir.exists():
        for cmd_file in commands_dir.glob('**/*.md'):
            files_checked += 1
            all_issues.extend(validate_file(cmd_file, base_dir))

    # Report
    print(f"Checked {files_checked} files")
    print()

    if all_issues:
        print(f"Found {len(all_issues)} broken references:\n")
        for issue in all_issues:
            if issue['status'] == 'ERROR':
                print(f"  ERROR: {issue['file']} - {issue['message']}")
            else:
                print(f"  {issue['file']}:{issue['line']} - @{issue['reference']}")
        sys.exit(1)
    else:
        print("All @ references valid")
        sys.exit(0)


if __name__ == '__main__':
    main()
