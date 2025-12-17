#!/usr/bin/env python3
"""
Validate technical specification files for execution planning.

Supports both markdown (.md) and TOON (.toon) specification formats.
Checks for required sections that execution planners need.

Exit codes:
    0 - Valid specification
    1 - Invalid or incomplete specification
    2 - Usage error or file not found
"""

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple


class ValidationResult(NamedTuple):
    valid: bool
    errors: list[str]
    warnings: list[str]
    sections_found: list[str]


# Required sections for a plannable spec (at least one from each group)
REQUIRED_SECTION_GROUPS = {
    'identity': {
        'patterns': [
            r'@id:\s*\S+',                    # TOON @id
            r'@type:\s*\S+',                  # TOON @type
            r'^#\s+.+',                       # Markdown H1 title
            r'^title:\s*.+',                  # YAML frontmatter title
        ],
        'description': 'Document identity (@id, @type, or title)',
    },
    'components': {
        'patterns': [
            r'components?[@\.]',              # TOON components
            r'^#{1,3}\s*components?\b',       # Markdown ## Components
            r'component.*summary',            # Component summary section
        ],
        'description': 'Components definition',
    },
    'scope_or_requirements': {
        'patterns': [
            r'scope[@\.]',                    # TOON scope
            r'^#{1,3}\s*scope\b',             # Markdown ## Scope
            r'acceptanceCriteria',            # TOON acceptance criteria
            r'^#{1,3}\s*acceptance\s*criteria', # Markdown ## Acceptance Criteria
            r'^#{1,3}\s*requirements?\b',     # Markdown ## Requirements
            r'inScope\[\]',                   # TOON inScope
        ],
        'description': 'Scope or requirements definition',
    },
}

# Optional but recommended sections
RECOMMENDED_SECTIONS = {
    'dependencies': [
        r'dependencies[@\.]',
        r'^#{1,3}\s*dependenc',
        r'dependsOn',
    ],
    'contracts': [
        r'contracts[@\.]',
        r'^#{1,3}\s*contracts?\b',
        r'given.*when.*then',
    ],
    'file_structure': [
        r'fileStructure[@\.]',
        r'^#{1,3}\s*file\s*structure',
        r'^#{1,3}\s*project\s*structure',
    ],
}


def validate_spec(content: str, filepath: Path) -> ValidationResult:
    """Validate specification content for execution planning."""
    errors = []
    warnings = []
    sections_found = []

    lines = content.split('\n')
    full_content_lower = content.lower()

    # Check file is not empty
    if not content.strip():
        return ValidationResult(False, ["File is empty"], [], [])

    # Check file has reasonable content
    if len(content) < 100:
        errors.append(f"File too short ({len(content)} chars) - likely incomplete")

    # Check required section groups
    for group_name, group_info in REQUIRED_SECTION_GROUPS.items():
        found = False
        for pattern in group_info['patterns']:
            if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                found = True
                sections_found.append(group_name)
                break

        if not found:
            errors.append(f"Missing required: {group_info['description']}")

    # Check recommended sections
    for section_name, patterns in RECOMMENDED_SECTIONS.items():
        found = False
        for pattern in patterns:
            if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                found = True
                sections_found.append(section_name)
                break

        if not found:
            warnings.append(f"Missing recommended section: {section_name}")

    # Format-specific validation
    if filepath.suffix == '.toon':
        # TOON-specific checks
        if '@type:' not in content:
            errors.append("TOON file missing @type declaration")
        if '@id:' not in content:
            errors.append("TOON file missing @id declaration")

    elif filepath.suffix == '.md':
        # Markdown-specific checks
        h1_count = len(re.findall(r'^#\s+', content, re.MULTILINE))
        if h1_count == 0:
            warnings.append("Markdown file has no H1 heading")
        elif h1_count > 1:
            warnings.append(f"Markdown file has {h1_count} H1 headings (expected 1)")

        # Check for YAML frontmatter
        if content.startswith('---'):
            frontmatter_end = content.find('---', 3)
            if frontmatter_end == -1:
                errors.append("Unclosed YAML frontmatter")

    # Check for plannable content indicators
    plannable_indicators = [
        (r'implementation', "implementation details"),
        (r'task|todo|step', "actionable items"),
        (r'type|class|interface|function|method', "code structure"),
    ]

    indicators_found = 0
    for pattern, desc in plannable_indicators:
        if re.search(pattern, full_content_lower):
            indicators_found += 1

    if indicators_found == 0:
        warnings.append("No implementation-related content detected - may not be plannable")

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        sections_found=sections_found
    )


def validate_file(filepath: Path) -> ValidationResult:
    """Validate a specification file."""
    if not filepath.exists():
        return ValidationResult(False, [f"File not found: {filepath}"], [], [])

    if filepath.suffix not in ('.md', '.toon'):
        return ValidationResult(
            False,
            [f"Unsupported file type: {filepath.suffix} (expected .md or .toon)"],
            [],
            []
        )

    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        return ValidationResult(False, [f"Failed to read file: {e}"], [], [])

    return validate_spec(content, filepath)


def main():
    parser = argparse.ArgumentParser(
        description='Validate technical specification files for execution planning',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Supported formats:
    .md   - Markdown specifications
    .toon - TOON structured specifications

Examples:
    %(prog)s specs/auth-system.md
    %(prog)s specs/auth-system.toon --strict
    %(prog)s *.md --quiet
        """
    )
    parser.add_argument('files', nargs='+', type=Path, help='Specification file(s) to validate')
    parser.add_argument('--strict', action='store_true', help='Treat warnings as errors')
    parser.add_argument('--quiet', '-q', action='store_true', help='Only output on error')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show sections found')

    args = parser.parse_args()

    all_valid = True

    for filepath in args.files:
        result = validate_file(filepath)

        if args.strict and result.warnings:
            result = ValidationResult(
                False,
                result.errors + result.warnings,
                [],
                result.sections_found
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
            if args.verbose and result.sections_found:
                print(f"  Sections: {', '.join(result.sections_found)}")
            for warning in result.warnings:
                print(f"  WARNING: {warning}")

    sys.exit(0 if all_valid else 1)


if __name__ == '__main__':
    main()
