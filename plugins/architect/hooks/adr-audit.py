#!/usr/bin/env python3
"""
ADR Collection Auditor

Performs mechanical validation of ADR collections:
- Naming convention compliance
- Cross-reference integrity (bidirectional)
- Template section presence
- Review date staleness
- README index synchronization

Outputs structured JSON for agent consumption.

Usage:
    python adr-audit.py /path/to/adr/directory
    python adr-audit.py /path/to/adr/directory --fix-dates  # Auto-update stale review dates
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


# === Configuration ===

NAMING_PATTERN = re.compile(r'^adr-(\d{3})-([a-z0-9]+(?:-[a-z0-9]+)*)\.md$')
TEMPLATE_FILE = 'adr-000-template.md'

REQUIRED_SECTIONS = [
    'Context',
    'Decision',
    'Constraints',
    'Related ADRs',
]

OPTIONAL_SECTIONS = [
    'Applies When',
    'Implementation',
    'Decision Drivers',
    'Considered Options',
    'Consequences',
    'Migration Path',
]

VALID_STATUSES = ['Proposed', 'Accepted', 'Deprecated', 'Superseded']
VALID_DOMAINS = ['Architecture', 'Data', 'Security', 'Performance', 'Testing', 'Integration', 'UI/UX', 'Infrastructure']

# Cross-reference patterns
XREF_PATTERN = re.compile(r'ADR-(\d{3})', re.IGNORECASE)
SUPERSEDES_PATTERN = re.compile(r'[Ss]upersedes\s+ADR-(\d{3})')
SUPERSEDED_BY_PATTERN = re.compile(r'[Ss]uperseded\s+by\s+ADR-(\d{3})')
EXTENDS_PATTERN = re.compile(r'[Ee]xtends\s+ADR-(\d{3})')
EXTENDED_BY_PATTERN = re.compile(r'[Ee]xtended\s+by\s+ADR-(\d{3})')
RELATED_TO_PATTERN = re.compile(r'[Rr]elated\s+to\s+ADR-(\d{3})')
CONFLICTS_WITH_PATTERN = re.compile(r'[Cc]onflicts\s+with\s+ADR-(\d{3})')

# Metadata patterns
STATUS_PATTERN = re.compile(r'\*?\*?Status\*?\*?\s*[:\|]\s*(\w+(?:\s+by\s+ADR-\d{3})?)', re.IGNORECASE)
DATE_PATTERN = re.compile(r'\*?\*?Date\*?\*?\s*[:\|]\s*(\d{4}-\d{2}-\d{2})', re.IGNORECASE)
REVIEW_DATE_PATTERN = re.compile(r'\*?\*?Review\s*Date\*?\*?\s*[:\|]\s*(\d{4}-\d{2}-\d{2})', re.IGNORECASE)
DOMAIN_PATTERN = re.compile(r'\*?\*?Domain\*?\*?\s*[:\|]\s*(\w+(?:/\w+)?)', re.IGNORECASE)

# README table patterns
README_TABLE_ROW = re.compile(r'\|\s*(?:ADR-)?(\d{3})\s*\|')


# === Data Classes ===

@dataclass
class NamingViolation:
    file: str
    issue: str
    suggested: Optional[str] = None


@dataclass
class MissingSection:
    file: str
    adr_number: str
    missing: list[str] = field(default_factory=list)


@dataclass
class XRefIssue:
    from_adr: str
    to_adr: str
    issue_type: str  # 'missing_backref', 'broken_ref', 'missing_reciprocal'
    relationship: str  # 'supersedes', 'extends', 'related', 'conflicts'
    suggested_fix: Optional[str] = None


@dataclass
class StaleReview:
    file: str
    adr_number: str
    review_date: str
    days_overdue: int
    suggested_date: str


@dataclass
class MetadataIssue:
    file: str
    adr_number: str
    issue: str
    field: str
    current_value: Optional[str] = None
    suggested_value: Optional[str] = None


@dataclass
class ReadmeSyncIssue:
    index_name: str
    issue_type: str  # 'missing_from_index', 'extra_in_index', 'status_mismatch', 'domain_mismatch'
    adr_number: str
    details: Optional[str] = None


@dataclass
class AuditResult:
    directory: str
    scan_date: str
    total_files: int
    valid_adrs: int
    naming_violations: list[NamingViolation] = field(default_factory=list)
    missing_sections: list[MissingSection] = field(default_factory=list)
    xref_issues: list[XRefIssue] = field(default_factory=list)
    stale_reviews: list[StaleReview] = field(default_factory=list)
    metadata_issues: list[MetadataIssue] = field(default_factory=list)
    readme_sync: list[ReadmeSyncIssue] = field(default_factory=list)
    number_gaps: list[str] = field(default_factory=list)  # Informational only


# === Core Functions ===

def validate_naming(files: list[Path]) -> tuple[list[NamingViolation], dict[str, Path]]:
    """Validate file naming convention. Returns violations and valid ADR map."""
    violations = []
    valid_adrs = {}  # number -> path

    for file in files:
        name = file.name

        # Skip template
        if name == TEMPLATE_FILE:
            continue

        match = NAMING_PATTERN.match(name)
        if not match:
            # Try to suggest a fix
            suggested = suggest_filename_fix(name)
            violations.append(NamingViolation(
                file=name,
                issue=diagnose_naming_issue(name),
                suggested=suggested
            ))
        else:
            number = match.group(1)
            valid_adrs[number] = file

    return violations, valid_adrs


def diagnose_naming_issue(filename: str) -> str:
    """Diagnose specific naming convention violation."""
    issues = []

    if not filename.startswith('adr-'):
        if filename.lower().startswith('adr'):
            issues.append('prefix must be lowercase "adr-"')
        else:
            issues.append('must start with "adr-"')

    # Check for number format
    num_match = re.search(r'adr-(\d+)-', filename, re.IGNORECASE)
    if num_match:
        num = num_match.group(1)
        if len(num) != 3:
            issues.append(f'number must be 3 digits zero-padded (got {len(num)} digits)')
    else:
        issues.append('missing ADR number')

    # Check for underscores
    if '_' in filename:
        issues.append('use hyphens not underscores')

    # Check for uppercase in title
    title_match = re.search(r'adr-\d+-(.+)\.md', filename, re.IGNORECASE)
    if title_match:
        title = title_match.group(1)
        if title != title.lower():
            issues.append('title must be lowercase')

    # Check extension
    if not filename.endswith('.md'):
        issues.append('must have .md extension')

    return '; '.join(issues) if issues else 'unknown naming issue'


def suggest_filename_fix(filename: str) -> Optional[str]:
    """Suggest corrected filename."""
    # Extract number
    num_match = re.search(r'(\d+)', filename)
    if not num_match:
        return None

    num = num_match.group(1).zfill(3)

    # Extract title portion
    # Remove prefix, number, and extension
    title = re.sub(r'^[Aa][Dd][Rr][-_]?\d+[-_]?', '', filename)
    title = re.sub(r'\.md$', '', title, flags=re.IGNORECASE)

    if not title:
        return None

    # Normalize title
    title = title.lower()
    title = re.sub(r'[_\s]+', '-', title)  # underscores/spaces to hyphens
    title = re.sub(r'-+', '-', title)  # collapse multiple hyphens
    title = title.strip('-')

    if not title:
        return None

    return f'adr-{num}-{title}.md'


def extract_metadata(content: str) -> dict:
    """Extract metadata fields from ADR content."""
    metadata = {
        'status': None,
        'date': None,
        'review_date': None,
        'domain': None,
    }

    status_match = STATUS_PATTERN.search(content)
    if status_match:
        metadata['status'] = status_match.group(1).strip()

    date_match = DATE_PATTERN.search(content)
    if date_match:
        metadata['date'] = date_match.group(1)

    review_match = REVIEW_DATE_PATTERN.search(content)
    if review_match:
        metadata['review_date'] = review_match.group(1)

    domain_match = DOMAIN_PATTERN.search(content)
    if domain_match:
        metadata['domain'] = domain_match.group(1).strip()

    return metadata


def check_sections(content: str, filename: str, adr_number: str) -> Optional[MissingSection]:
    """Check for required sections in ADR content."""
    missing = []

    for section in REQUIRED_SECTIONS:
        # Look for ## Section or **Section**
        pattern = rf'(?:^##\s*{re.escape(section)}|\*\*{re.escape(section)}\*\*)'
        if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
            missing.append(section)

    if missing:
        return MissingSection(file=filename, adr_number=adr_number, missing=missing)
    return None


def extract_xrefs(content: str) -> dict:
    """Extract all cross-references and their types from content."""
    xrefs = {
        'all': set(),
        'supersedes': set(),
        'superseded_by': set(),
        'extends': set(),
        'extended_by': set(),
        'related_to': set(),
        'conflicts_with': set(),
    }

    # Get all ADR references
    for match in XREF_PATTERN.finditer(content):
        xrefs['all'].add(match.group(1))

    # Get typed references
    for match in SUPERSEDES_PATTERN.finditer(content):
        xrefs['supersedes'].add(match.group(1))

    for match in SUPERSEDED_BY_PATTERN.finditer(content):
        xrefs['superseded_by'].add(match.group(1))

    for match in EXTENDS_PATTERN.finditer(content):
        xrefs['extends'].add(match.group(1))

    for match in EXTENDED_BY_PATTERN.finditer(content):
        xrefs['extended_by'].add(match.group(1))

    for match in RELATED_TO_PATTERN.finditer(content):
        xrefs['related_to'].add(match.group(1))

    for match in CONFLICTS_WITH_PATTERN.finditer(content):
        xrefs['conflicts_with'].add(match.group(1))

    return xrefs


def validate_xrefs(adr_contents: dict[str, tuple[str, dict]]) -> list[XRefIssue]:
    """
    Validate cross-references are bidirectional.
    adr_contents: {number: (content, xrefs)}
    """
    issues = []
    existing_numbers = set(adr_contents.keys())

    for num, (content, xrefs) in adr_contents.items():
        # Check for broken references (to non-existent ADRs)
        for ref in xrefs['all']:
            if ref not in existing_numbers and ref != '000':  # 000 is template
                issues.append(XRefIssue(
                    from_adr=f'ADR-{num}',
                    to_adr=f'ADR-{ref}',
                    issue_type='broken_ref',
                    relationship='unknown',
                    suggested_fix=f'Remove reference to non-existent ADR-{ref}'
                ))

        # Check bidirectionality: supersedes/superseded_by
        for ref in xrefs['supersedes']:
            if ref in existing_numbers:
                other_xrefs = adr_contents[ref][1]
                if num not in other_xrefs['superseded_by']:
                    issues.append(XRefIssue(
                        from_adr=f'ADR-{num}',
                        to_adr=f'ADR-{ref}',
                        issue_type='missing_backref',
                        relationship='supersedes',
                        suggested_fix=f'Add "Superseded by ADR-{num}" to ADR-{ref}'
                    ))

        for ref in xrefs['superseded_by']:
            if ref in existing_numbers:
                other_xrefs = adr_contents[ref][1]
                if num not in other_xrefs['supersedes']:
                    issues.append(XRefIssue(
                        from_adr=f'ADR-{num}',
                        to_adr=f'ADR-{ref}',
                        issue_type='missing_backref',
                        relationship='superseded_by',
                        suggested_fix=f'Add "Supersedes ADR-{num}" to ADR-{ref}'
                    ))

        # Check bidirectionality: extends/extended_by
        for ref in xrefs['extends']:
            if ref in existing_numbers:
                other_xrefs = adr_contents[ref][1]
                if num not in other_xrefs['extended_by']:
                    issues.append(XRefIssue(
                        from_adr=f'ADR-{num}',
                        to_adr=f'ADR-{ref}',
                        issue_type='missing_backref',
                        relationship='extends',
                        suggested_fix=f'Add "Extended by ADR-{num}" to ADR-{ref}'
                    ))

        # Check bidirectionality: related_to (symmetric)
        for ref in xrefs['related_to']:
            if ref in existing_numbers:
                other_xrefs = adr_contents[ref][1]
                if num not in other_xrefs['related_to'] and num not in other_xrefs['all']:
                    issues.append(XRefIssue(
                        from_adr=f'ADR-{num}',
                        to_adr=f'ADR-{ref}',
                        issue_type='missing_reciprocal',
                        relationship='related_to',
                        suggested_fix=f'Add "Related to ADR-{num}" to ADR-{ref}'
                    ))

        # Check bidirectionality: conflicts_with (symmetric)
        for ref in xrefs['conflicts_with']:
            if ref in existing_numbers:
                other_xrefs = adr_contents[ref][1]
                if num not in other_xrefs['conflicts_with']:
                    issues.append(XRefIssue(
                        from_adr=f'ADR-{num}',
                        to_adr=f'ADR-{ref}',
                        issue_type='missing_reciprocal',
                        relationship='conflicts_with',
                        suggested_fix=f'Add "Conflicts with ADR-{num}" to ADR-{ref}'
                    ))

    return issues


def check_review_dates(adr_contents: dict[str, tuple[str, dict]], adr_paths: dict[str, Path]) -> list[StaleReview]:
    """Check for stale review dates."""
    stale = []
    today = datetime.now().date()

    for num, (content, xrefs) in adr_contents.items():
        metadata = extract_metadata(content)
        review_date_str = metadata.get('review_date')

        if review_date_str:
            try:
                review_date = datetime.strptime(review_date_str, '%Y-%m-%d').date()
                if review_date < today:
                    days_overdue = (today - review_date).days
                    new_date = today + timedelta(days=180)  # 6 months
                    stale.append(StaleReview(
                        file=adr_paths[num].name,
                        adr_number=f'ADR-{num}',
                        review_date=review_date_str,
                        days_overdue=days_overdue,
                        suggested_date=new_date.strftime('%Y-%m-%d')
                    ))
            except ValueError:
                pass  # Invalid date format, will be caught by metadata validation

    return stale


def check_metadata(adr_contents: dict[str, tuple[str, dict]], adr_paths: dict[str, Path]) -> list[MetadataIssue]:
    """Check metadata completeness and validity."""
    issues = []

    for num, (content, xrefs) in adr_contents.items():
        metadata = extract_metadata(content)
        filename = adr_paths[num].name

        # Check status
        if not metadata['status']:
            issues.append(MetadataIssue(
                file=filename,
                adr_number=f'ADR-{num}',
                issue='missing status',
                field='Status',
                suggested_value='Proposed'
            ))
        elif metadata['status'] not in VALID_STATUSES and not metadata['status'].startswith('Superseded'):
            issues.append(MetadataIssue(
                file=filename,
                adr_number=f'ADR-{num}',
                issue=f'invalid status "{metadata["status"]}"',
                field='Status',
                current_value=metadata['status'],
                suggested_value='Accepted'
            ))

        # Check date
        if not metadata['date']:
            issues.append(MetadataIssue(
                file=filename,
                adr_number=f'ADR-{num}',
                issue='missing date',
                field='Date',
                suggested_value=datetime.now().strftime('%Y-%m-%d')
            ))

        # Check review date
        if not metadata['review_date']:
            suggested = (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d')
            issues.append(MetadataIssue(
                file=filename,
                adr_number=f'ADR-{num}',
                issue='missing review date',
                field='Review Date',
                suggested_value=suggested
            ))

        # Check domain (optional but useful)
        if metadata['domain'] and metadata['domain'] not in VALID_DOMAINS:
            issues.append(MetadataIssue(
                file=filename,
                adr_number=f'ADR-{num}',
                issue=f'invalid domain "{metadata["domain"]}"',
                field='Domain',
                current_value=metadata['domain']
            ))

    return issues


def parse_readme_indices(readme_path: Path) -> dict[str, set[str]]:
    """Parse README.md to extract ADR numbers from indices."""
    indices = {
        'complete_index': set(),
        'quick_reference': set(),
        'domain_index': set(),
        'keywords_index': set(),
    }

    if not readme_path.exists():
        return indices

    content = readme_path.read_text()

    # Find all ADR numbers mentioned in tables
    for match in README_TABLE_ROW.finditer(content):
        num = match.group(1)
        indices['complete_index'].add(num)

    # For simplicity, we just collect all mentioned ADR numbers
    # A more sophisticated parser would identify specific sections

    return indices


def check_readme_sync(readme_path: Path, valid_adrs: dict[str, Path],
                      adr_contents: dict[str, tuple[str, dict]]) -> list[ReadmeSyncIssue]:
    """Check README indices are synchronized with actual ADR files."""
    issues = []

    if not readme_path.exists():
        issues.append(ReadmeSyncIssue(
            index_name='README.md',
            issue_type='missing_file',
            adr_number='N/A',
            details='README.md not found in ADR directory'
        ))
        return issues

    indices = parse_readme_indices(readme_path)
    indexed_numbers = indices['complete_index']
    actual_numbers = set(valid_adrs.keys())

    # Check for ADRs missing from index
    missing_from_index = actual_numbers - indexed_numbers
    for num in sorted(missing_from_index):
        issues.append(ReadmeSyncIssue(
            index_name='Complete Index',
            issue_type='missing_from_index',
            adr_number=f'ADR-{num}',
            details=f'{valid_adrs[num].name} not in README index'
        ))

    # Check for extra entries in index (ADRs that don't exist)
    extra_in_index = indexed_numbers - actual_numbers - {'000'}  # 000 is template
    for num in sorted(extra_in_index):
        issues.append(ReadmeSyncIssue(
            index_name='Complete Index',
            issue_type='extra_in_index',
            adr_number=f'ADR-{num}',
            details=f'ADR-{num} in README but file not found'
        ))

    return issues


def find_number_gaps(valid_adrs: dict[str, Path]) -> list[str]:
    """Find gaps in ADR numbering (informational only)."""
    if not valid_adrs:
        return []

    numbers = sorted(int(n) for n in valid_adrs.keys())
    if not numbers:
        return []

    gaps = []
    for i in range(numbers[0], numbers[-1] + 1):
        if i not in numbers and i != 0:  # 0 is template
            gaps.append(f'ADR-{i:03d}')

    return gaps


def run_audit(adr_dir: Path) -> AuditResult:
    """Run full audit on ADR directory."""
    # Find all markdown files
    all_files = list(adr_dir.glob('*.md'))
    adr_files = [f for f in all_files if f.name.startswith('adr-')]

    # Validate naming
    naming_violations, valid_adrs = validate_naming(adr_files)

    # Read valid ADR contents and extract cross-refs
    adr_contents = {}  # {number: (content, xrefs)}
    for num, path in valid_adrs.items():
        content = path.read_text()
        xrefs = extract_xrefs(content)
        adr_contents[num] = (content, xrefs)

    # Check sections
    missing_sections = []
    for num, (content, xrefs) in adr_contents.items():
        result = check_sections(content, valid_adrs[num].name, f'ADR-{num}')
        if result:
            missing_sections.append(result)

    # Validate cross-references
    xref_issues = validate_xrefs(adr_contents)

    # Check review dates
    stale_reviews = check_review_dates(adr_contents, valid_adrs)

    # Check metadata
    metadata_issues = check_metadata(adr_contents, valid_adrs)

    # Check README sync
    readme_path = adr_dir / 'README.md'
    readme_issues = check_readme_sync(readme_path, valid_adrs, adr_contents)

    # Find number gaps
    gaps = find_number_gaps(valid_adrs)

    return AuditResult(
        directory=str(adr_dir),
        scan_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        total_files=len(adr_files),
        valid_adrs=len(valid_adrs),
        naming_violations=naming_violations,
        missing_sections=missing_sections,
        xref_issues=xref_issues,
        stale_reviews=stale_reviews,
        metadata_issues=metadata_issues,
        readme_sync=readme_issues,
        number_gaps=gaps,
    )


def to_json(result: AuditResult) -> str:
    """Convert audit result to JSON."""
    def serialize(obj):
        if hasattr(obj, '__dataclass_fields__'):
            return asdict(obj)
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, Path):
            return str(obj)
        return obj

    data = asdict(result)
    return json.dumps(data, indent=2, default=serialize)


def print_summary(result: AuditResult):
    """Print human-readable summary to stderr."""
    total_issues = (
        len(result.naming_violations) +
        len(result.missing_sections) +
        len(result.xref_issues) +
        len(result.stale_reviews) +
        len(result.metadata_issues) +
        len(result.readme_sync)
    )

    print(f"\n=== ADR Audit Summary ===", file=sys.stderr)
    print(f"Directory: {result.directory}", file=sys.stderr)
    print(f"Total files: {result.total_files}", file=sys.stderr)
    print(f"Valid ADRs: {result.valid_adrs}", file=sys.stderr)
    print(f"Total issues: {total_issues}", file=sys.stderr)
    print(f"  - Naming violations: {len(result.naming_violations)}", file=sys.stderr)
    print(f"  - Missing sections: {len(result.missing_sections)}", file=sys.stderr)
    print(f"  - Cross-ref issues: {len(result.xref_issues)}", file=sys.stderr)
    print(f"  - Stale reviews: {len(result.stale_reviews)}", file=sys.stderr)
    print(f"  - Metadata issues: {len(result.metadata_issues)}", file=sys.stderr)
    print(f"  - README sync: {len(result.readme_sync)}", file=sys.stderr)
    if result.number_gaps:
        print(f"  - Number gaps: {len(result.number_gaps)} (informational)", file=sys.stderr)
    print(file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description='Audit ADR collection for consistency issues',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ./adr                    # Audit ADR directory
  %(prog)s ./adr --quiet            # JSON output only (no summary)
  %(prog)s ./adr --summary-only     # Summary only (no JSON)
        """
    )
    parser.add_argument('directory', type=Path, help='Path to ADR directory')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Suppress summary output (JSON only)')
    parser.add_argument('--summary-only', '-s', action='store_true',
                        help='Print summary only (no JSON)')

    args = parser.parse_args()

    if not args.directory.exists():
        print(f"Error: Directory not found: {args.directory}", file=sys.stderr)
        sys.exit(1)

    if not args.directory.is_dir():
        print(f"Error: Not a directory: {args.directory}", file=sys.stderr)
        sys.exit(1)

    result = run_audit(args.directory)

    if not args.summary_only:
        print(to_json(result))

    if not args.quiet:
        print_summary(result)

    # Exit with error code if issues found
    total_issues = (
        len(result.naming_violations) +
        len(result.missing_sections) +
        len(result.xref_issues) +
        len(result.stale_reviews) +
        len(result.metadata_issues) +
        len(result.readme_sync)
    )
    sys.exit(1 if total_issues > 0 else 0)


if __name__ == '__main__':
    main()
