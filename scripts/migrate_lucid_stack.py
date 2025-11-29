#!/usr/bin/env python3
"""
Migrate capabilities, outcomes, and actors from lucid_stack to lucid-toolkit format.

This script handles the structural differences between the two systems:
- Source: lucid_stack (numeric-prefixed directories, 0-4 state prefixes)
- Target: lucid-toolkit schema format (kebab-case only, state names without prefixes)

Usage:
    python migrate_lucid_stack.py --source /path/to/lucid_stack --target /path/to/target
    python migrate_lucid_stack.py --source /path/to/lucid_stack --target /path/to/target --dry-run
"""

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def utc_now_iso() -> str:
    """Return current UTC time as ISO 8601 string."""
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


# =============================================================================
# Path Transformation Utilities
# =============================================================================

def strip_numeric_prefix(name: str) -> str:
    """
    Remove numeric prefix from directory names.

    Examples:
        '01-trust-security' -> 'trust-security'
        '99-platform' -> 'platform'
        '005-ontology-iteration' -> 'ontology-iteration'
        'budget-planning-financial' -> 'budget-planning-financial' (no change)
    """
    # Pattern: optional leading zeros + digits + hyphen at start
    return re.sub(r'^[0-9]+-', '', name)


def normalize_state_directory(state_dir: str) -> str:
    """
    Convert numbered state directories to standard state names.

    Examples:
        '0-queued' -> 'queued'
        '1-ready' -> 'ready'
        '2-in-progress' -> 'in-progress'
        '3-blocked' -> 'blocked'
        '4-completed' -> 'completed'
    """
    state_map = {
        '0-queued': 'queued',
        '1-ready': 'ready',
        '2-in-progress': 'in-progress',
        '3-blocked': 'blocked',
        '4-completed': 'completed',
    }
    return state_map.get(state_dir, state_dir)


def transform_capability_path(source_path: str) -> str:
    """
    Transform capability path from source format to target format.

    Examples:
        'capabilities/01-trust-security/authentication-system/'
            -> 'capabilities/trust-security/authentication-system/'
        'capabilities/03-financial/budget-planning-financial/'
            -> 'capabilities/financial/budget-planning-financial/'
    """
    parts = source_path.split('/')
    transformed = []
    for part in parts:
        if part.startswith(('01-', '02-', '03-', '04-', '99-')):
            transformed.append(strip_numeric_prefix(part))
        else:
            transformed.append(part)
    return '/'.join(transformed)


def transform_outcome_path(source_path: str) -> str:
    """
    Transform outcome path from source format to target format.

    Examples:
        'outcomes/2-in-progress/005-ontology/'
            -> 'outcomes/in-progress/005-ontology/'
        'outcomes/0-queued/002-legislative-monitor/'
            -> 'outcomes/queued/002-legislative-monitor/'
    """
    parts = source_path.split('/')
    transformed = []
    for i, part in enumerate(parts):
        if i == 1 and part in ('0-queued', '1-ready', '2-in-progress', '3-blocked', '4-completed'):
            transformed.append(normalize_state_directory(part))
        else:
            transformed.append(part)
    return '/'.join(transformed)


def transform_path_references(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively transform all path references in a JSON structure.
    """
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                # Check if it's a path that needs transformation
                if value.startswith('capabilities/'):
                    result[key] = transform_capability_path(value)
                elif value.startswith('outcomes/'):
                    result[key] = transform_outcome_path(value)
                else:
                    result[key] = value
            elif isinstance(value, (dict, list)):
                result[key] = transform_path_references(value)
            else:
                result[key] = value
        return result
    elif isinstance(data, list):
        return [transform_path_references(item) for item in data]
    else:
        return data


# =============================================================================
# Capability Migration
# =============================================================================

def migrate_capability_track(source_data: Dict[str, Any], source_path: Path) -> Dict[str, Any]:
    """
    Migrate a capability_track.json from lucid_stack to lucid-toolkit format.
    """
    # Start with path-transformed data
    data = transform_path_references(source_data)

    # Update directoryPath in metadata
    if 'metadata' in data and 'directoryPath' in data['metadata']:
        data['metadata']['directoryPath'] = transform_capability_path(
            data['metadata']['directoryPath']
        )

    # Ensure required fields have defaults if missing
    if 'outcomes' not in data:
        data['outcomes'] = {
            'requiredOutcomes': [],
            'builtByOutcomes': [],
            'enablesOutcomes': []
        }

    # Transform folder names in relationships
    if 'relationships' in data:
        relationships = data['relationships']

        # Transform prerequisites
        if 'prerequisites' in relationships:
            for prereq in relationships['prerequisites']:
                if 'folderName' in prereq:
                    prereq['folderName'] = strip_numeric_prefix(prereq['folderName'])

        # Transform enables
        if 'enables' in relationships:
            for enables in relationships['enables']:
                if 'folderName' in enables:
                    enables['folderName'] = strip_numeric_prefix(enables['folderName'])

        # Transform composedOf
        if 'composedOf' in relationships:
            for composed in relationships['composedOf']:
                if 'folderName' in composed:
                    composed['folderName'] = strip_numeric_prefix(composed['folderName'])

        # Transform parentFolderName
        if 'parentFolderName' in relationships and relationships['parentFolderName']:
            relationships['parentFolderName'] = strip_numeric_prefix(
                relationships['parentFolderName']
            )

    # Update metadata timestamp
    if 'metadata' not in data:
        data['metadata'] = {}
    data['metadata']['updated'] = utc_now_iso()
    data['metadata']['migratedFrom'] = str(source_path)

    return data


def migrate_capabilities(
    source_dir: Path,
    target_dir: Path,
    dry_run: bool = False
) -> List[Tuple[Path, Path]]:
    """
    Migrate all capabilities from source to target.

    Returns list of (source, target) path tuples for migrated files.
    """
    source_caps = source_dir / 'capabilities'
    target_caps = target_dir / 'capabilities'

    if not source_caps.exists():
        print(f"Warning: Source capabilities directory not found: {source_caps}")
        return []

    migrated = []

    # Walk through source capability directories
    for domain_dir in sorted(source_caps.iterdir()):
        if not domain_dir.is_dir() or domain_dir.name.startswith('.'):
            continue

        # Transform domain directory name (remove numeric prefix)
        target_domain_name = strip_numeric_prefix(domain_dir.name)
        target_domain_dir = target_caps / target_domain_name

        # Process capability directories within the domain
        for cap_dir in sorted(domain_dir.iterdir()):
            if not cap_dir.is_dir():
                # Handle domain-level files (SNAPSHOT.md, etc.)
                if cap_dir.suffix in ('.md', '.json') and not cap_dir.name.startswith('.'):
                    target_file = target_caps / target_domain_name / cap_dir.name
                    if not dry_run:
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(cap_dir, target_file)
                    print(f"  Copy: {cap_dir.name} -> {target_file.relative_to(target_dir)}")
                    migrated.append((cap_dir, target_file))
                continue

            # Check for capability_track.json
            cap_track = cap_dir / 'capability_track.json'
            if cap_track.exists():
                target_cap_dir = target_domain_dir / cap_dir.name
                target_track = target_cap_dir / 'capability_track.json'

                # Migrate the tracking file
                with open(cap_track, 'r') as f:
                    source_data = json.load(f)

                migrated_data = migrate_capability_track(source_data, cap_track)

                if not dry_run:
                    target_cap_dir.mkdir(parents=True, exist_ok=True)
                    with open(target_track, 'w') as f:
                        json.dump(migrated_data, f, indent=2)

                print(f"  Migrate: {cap_track.relative_to(source_dir)} -> {target_track.relative_to(target_dir)}")
                migrated.append((cap_track, target_track))

                # Copy associated markdown files
                for md_file in cap_dir.glob('*.md'):
                    target_md = target_cap_dir / md_file.name
                    if not dry_run:
                        shutil.copy2(md_file, target_md)
                    print(f"  Copy: {md_file.name}")
                    migrated.append((md_file, target_md))

                # Process sub-capabilities (nested directories)
                for sub_dir in cap_dir.iterdir():
                    if sub_dir.is_dir() and (sub_dir / 'capability_track.json').exists():
                        sub_track = sub_dir / 'capability_track.json'
                        target_sub_dir = target_cap_dir / sub_dir.name
                        target_sub_track = target_sub_dir / 'capability_track.json'

                        with open(sub_track, 'r') as f:
                            sub_data = json.load(f)

                        migrated_sub_data = migrate_capability_track(sub_data, sub_track)

                        if not dry_run:
                            target_sub_dir.mkdir(parents=True, exist_ok=True)
                            with open(target_sub_track, 'w') as f:
                                json.dump(migrated_sub_data, f, indent=2)

                        print(f"    Migrate sub: {sub_dir.name}/capability_track.json")
                        migrated.append((sub_track, target_sub_track))

                        # Copy sub-capability markdown files
                        for md_file in sub_dir.glob('*.md'):
                            target_md = target_sub_dir / md_file.name
                            if not dry_run:
                                shutil.copy2(md_file, target_md)
                            migrated.append((md_file, target_md))

    return migrated


# =============================================================================
# Outcome Migration
# =============================================================================

def migrate_outcome_track(source_data: Dict[str, Any], source_path: Path) -> Dict[str, Any]:
    """
    Migrate an outcome_track.json from lucid_stack to lucid-toolkit format.
    """
    # Start with path-transformed data
    data = transform_path_references(source_data)

    # Transform capabilityPath references in outcome object
    if 'outcome' in data:
        outcome = data['outcome']

        # Transform capabilityContributions
        if 'capabilityContributions' in outcome:
            for contrib in outcome['capabilityContributions']:
                if 'capabilityPath' in contrib:
                    contrib['capabilityPath'] = transform_capability_path(
                        contrib['capabilityPath']
                    )
                # Also strip numeric prefix from capabilityId
                if 'capabilityId' in contrib:
                    contrib['capabilityId'] = strip_numeric_prefix(contrib['capabilityId'])

        # Update timestamp
        outcome['updatedAt'] = utc_now_iso()

    return data


def migrate_outcomes(
    source_dir: Path,
    target_dir: Path,
    dry_run: bool = False
) -> List[Tuple[Path, Path]]:
    """
    Migrate all outcomes from source to target.

    Returns list of (source, target) path tuples for migrated files.
    """
    source_outcomes = source_dir / 'outcomes'
    target_outcomes = target_dir / 'outcomes'

    if not source_outcomes.exists():
        print(f"Warning: Source outcomes directory not found: {source_outcomes}")
        return []

    migrated = []

    # Map state directories
    state_dirs = [
        ('0-queued', 'queued'),
        ('1-ready', 'ready'),
        ('2-in-progress', 'in-progress'),
        ('3-blocked', 'blocked'),
        ('4-completed', 'completed'),
    ]

    for source_state, target_state in state_dirs:
        source_state_dir = source_outcomes / source_state
        if not source_state_dir.exists():
            continue

        target_state_dir = target_outcomes / target_state

        # Process each outcome directory
        for outcome_dir in sorted(source_state_dir.iterdir()):
            if not outcome_dir.is_dir():
                continue

            target_outcome_dir = target_state_dir / outcome_dir.name

            # Migrate outcome_track.json
            outcome_track = outcome_dir / 'outcome_track.json'
            if outcome_track.exists():
                with open(outcome_track, 'r') as f:
                    source_data = json.load(f)

                migrated_data = migrate_outcome_track(source_data, outcome_track)

                target_track = target_outcome_dir / 'outcome_track.json'
                if not dry_run:
                    target_outcome_dir.mkdir(parents=True, exist_ok=True)
                    with open(target_track, 'w') as f:
                        json.dump(migrated_data, f, indent=2)

                print(f"  Migrate: {outcome_track.relative_to(source_dir)} -> {target_track.relative_to(target_dir)}")
                migrated.append((outcome_track, target_track))

            # Copy all other files in outcome directory
            for item in outcome_dir.iterdir():
                if item.name == 'outcome_track.json':
                    continue

                target_item = target_outcome_dir / item.name

                if item.is_file():
                    if not dry_run:
                        target_outcome_dir.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, target_item)
                    print(f"    Copy: {item.name}")
                    migrated.append((item, target_item))

                elif item.is_dir():
                    # Handle subdirectories (child outcomes, reports, evidence)
                    if not dry_run:
                        if target_item.exists():
                            shutil.rmtree(target_item)
                        shutil.copytree(item, target_item)
                    print(f"    Copy dir: {item.name}/")
                    migrated.append((item, target_item))

                    # If it's a child outcome, migrate its tracking file
                    child_track = item / 'outcome_track.json'
                    if child_track.exists():
                        with open(child_track, 'r') as f:
                            child_data = json.load(f)

                        migrated_child = migrate_outcome_track(child_data, child_track)
                        target_child_track = target_item / 'outcome_track.json'

                        if not dry_run:
                            with open(target_child_track, 'w') as f:
                                json.dump(migrated_child, f, indent=2)

                        print(f"      Migrate child: {item.name}/outcome_track.json")

    return migrated


# =============================================================================
# Status/Summary Migration
# =============================================================================

def migrate_summary(source_file: Path, target_file: Path, dry_run: bool = False) -> bool:
    """
    Migrate a summary JSON file, transforming all path references.
    """
    if not source_file.exists():
        print(f"  Skip: {source_file.name} not found")
        return False

    with open(source_file, 'r') as f:
        data = json.load(f)

    # Transform all path references
    migrated_data = transform_path_references(data)

    # Update lastUpdated timestamp
    if 'summary' in migrated_data and 'lastUpdated' in migrated_data['summary']:
        migrated_data['summary']['lastUpdated'] = utc_now_iso()
    if 'lastUpdated' in migrated_data:
        migrated_data['lastUpdated'] = utc_now_iso()

    if not dry_run:
        target_file.parent.mkdir(parents=True, exist_ok=True)
        with open(target_file, 'w') as f:
            json.dump(migrated_data, f, indent=2)

    print(f"  Migrate: {source_file.name} -> {target_file}")
    return True


def migrate_status(
    source_dir: Path,
    target_dir: Path,
    dry_run: bool = False
) -> List[Tuple[Path, Path]]:
    """
    Migrate status/summary files from source to target.
    """
    source_status = source_dir / 'status'
    target_status = target_dir / 'status'

    if not source_status.exists():
        print(f"Warning: Source status directory not found: {source_status}")
        return []

    migrated = []

    # Core summary files to migrate
    summary_files = [
        'capability_summary.json',
        'outcome_summary.json',
        'actor_summary.json',
        'sessions_summary.json',
    ]

    for filename in summary_files:
        source_file = source_status / filename
        target_file = target_status / filename

        if migrate_summary(source_file, target_file, dry_run):
            migrated.append((source_file, target_file))

    # Copy any additional files
    for item in source_status.iterdir():
        if item.name in summary_files or item.name.startswith('.'):
            continue

        target_item = target_status / item.name

        if item.is_file():
            if not dry_run:
                target_status.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target_item)
            print(f"  Copy: {item.name}")
            migrated.append((item, target_item))

    return migrated


# =============================================================================
# Main Migration
# =============================================================================

def run_migration(
    source_dir: Path,
    target_dir: Path,
    dry_run: bool = False,
    skip_capabilities: bool = False,
    skip_outcomes: bool = False,
    skip_status: bool = False,
) -> Dict[str, int]:
    """
    Run the full migration.

    Returns counts of migrated items by category.
    """
    print(f"\n{'='*60}")
    print(f"Lucid Stack Migration")
    print(f"{'='*60}")
    print(f"Source: {source_dir}")
    print(f"Target: {target_dir}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"{'='*60}\n")

    counts = {
        'capabilities': 0,
        'outcomes': 0,
        'status': 0,
    }

    # Migrate capabilities
    if not skip_capabilities:
        print("Migrating capabilities...")
        cap_migrated = migrate_capabilities(source_dir, target_dir, dry_run)
        counts['capabilities'] = len(cap_migrated)
        print(f"  Total: {counts['capabilities']} files\n")

    # Migrate outcomes
    if not skip_outcomes:
        print("Migrating outcomes...")
        out_migrated = migrate_outcomes(source_dir, target_dir, dry_run)
        counts['outcomes'] = len(out_migrated)
        print(f"  Total: {counts['outcomes']} files\n")

    # Migrate status/summaries
    if not skip_status:
        print("Migrating status files...")
        status_migrated = migrate_status(source_dir, target_dir, dry_run)
        counts['status'] = len(status_migrated)
        print(f"  Total: {counts['status']} files\n")

    # Summary
    print(f"{'='*60}")
    print("Migration Summary")
    print(f"{'='*60}")
    print(f"  Capabilities: {counts['capabilities']} files")
    print(f"  Outcomes:     {counts['outcomes']} files")
    print(f"  Status:       {counts['status']} files")
    print(f"  ─────────────────────────")
    print(f"  Total:        {sum(counts.values())} files")

    if dry_run:
        print(f"\n⚠️  DRY RUN - No files were actually written")
        print(f"    Run without --dry-run to perform migration")
    else:
        print(f"\n✓ Migration complete")

    print(f"{'='*60}\n")

    return counts


def main():
    parser = argparse.ArgumentParser(
        description='Migrate lucid_stack data to lucid-toolkit format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run to see what would be migrated
  python migrate_lucid_stack.py --source /path/to/lucid_stack --target /path/to/target --dry-run

  # Full migration
  python migrate_lucid_stack.py --source /path/to/lucid_stack --target /path/to/target

  # Migrate only capabilities
  python migrate_lucid_stack.py --source /path/to/lucid_stack --target /path/to/target --skip-outcomes --skip-status
        """
    )

    parser.add_argument(
        '--source', '-s',
        type=Path,
        required=True,
        help='Source directory (lucid_stack root)'
    )

    parser.add_argument(
        '--target', '-t',
        type=Path,
        required=True,
        help='Target directory for migrated data'
    )

    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be migrated without making changes'
    )

    parser.add_argument(
        '--skip-capabilities',
        action='store_true',
        help='Skip capability migration'
    )

    parser.add_argument(
        '--skip-outcomes',
        action='store_true',
        help='Skip outcome migration'
    )

    parser.add_argument(
        '--skip-status',
        action='store_true',
        help='Skip status/summary file migration'
    )

    args = parser.parse_args()

    # Validate source directory
    if not args.source.exists():
        print(f"Error: Source directory does not exist: {args.source}")
        return 1

    # Create target directory if needed (unless dry run)
    if not args.dry_run and not args.target.exists():
        args.target.mkdir(parents=True, exist_ok=True)

    # Run migration
    try:
        counts = run_migration(
            source_dir=args.source,
            target_dir=args.target,
            dry_run=args.dry_run,
            skip_capabilities=args.skip_capabilities,
            skip_outcomes=args.skip_outcomes,
            skip_status=args.skip_status,
        )
        return 0 if sum(counts.values()) > 0 else 1

    except Exception as e:
        print(f"Error during migration: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
