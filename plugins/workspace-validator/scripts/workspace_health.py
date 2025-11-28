#!/usr/bin/env python3
"""
Comprehensive workspace health check and maintenance script.

This script performs all maintenance operations for the lucid_stack workspace:
- Phase 1: Capability directory ↔ summary synchronization
- Phase 2: Outcome directory ↔ summary synchronization
- Phase 3: Cross-reference integrity validation
- Phase 4: Index rebuild and validation
- Phase 5: Temporal health checks
- Phase 6: Temp file cleanup
- Phase 7: Git health check
- Phase 8: Comprehensive health report

Usage:
    python3 workspace_health.py [--dry-run] [--verbose] [--fix] [--phase N]

Options:
    --dry-run   Show what would be done without making changes
    --verbose   Show detailed information
    --fix       Automatically fix issues where possible
    --phase N   Run only specific phase (1-8)
"""

import sys
import json
import argparse
import subprocess
import re
from pathlib import Path
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum

# Add parent directory to path for imports
SCRIPT_DIR = Path(__file__).parent
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent.parent  # shared/scripts -> .claude/shared -> .claude -> workspace root
sys.path.insert(0, str(WORKSPACE_ROOT / "shared/hook_scripts"))

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


# =============================================================================
# ANSI Colors for Output
# =============================================================================

class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Colors
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"


class Icons:
    """Unicode icons for status indicators."""
    CHECK = "✓"
    CROSS = "✗"
    WARN = "⚠"
    INFO = "ℹ"
    FIX = "🔧"
    SKIP = "⊘"
    SYNC = "🔄"
    CLEAN = "🧹"


# =============================================================================
# Data Classes for Health Report
# =============================================================================

class Severity(Enum):
    """Issue severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class Issue:
    """Represents a detected issue."""
    severity: Severity
    category: str
    message: str
    path: Optional[str] = None
    auto_fixable: bool = False
    fixed: bool = False
    fix_description: Optional[str] = None


@dataclass
class PhaseResult:
    """Result of running a health check phase."""
    name: str
    passed: bool
    issues: List[Issue] = field(default_factory=list)
    fixes_applied: int = 0
    items_checked: int = 0
    duration_ms: float = 0


@dataclass
class HealthReport:
    """Complete health report for the workspace."""
    timestamp: str
    phases: List[PhaseResult] = field(default_factory=list)
    overall_healthy: bool = True
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    fixes_applied: int = 0

    def add_phase(self, phase: PhaseResult):
        """Add a phase result and update counters."""
        self.phases.append(phase)
        for issue in phase.issues:
            if issue.severity == Severity.CRITICAL:
                self.critical_count += 1
                self.overall_healthy = False
            elif issue.severity == Severity.HIGH:
                self.high_count += 1
                self.overall_healthy = False
            elif issue.severity == Severity.MEDIUM:
                self.medium_count += 1
            elif issue.severity == Severity.LOW:
                self.low_count += 1
        self.fixes_applied += phase.fixes_applied


# =============================================================================
# Utility Functions
# =============================================================================

def load_json(path: Path) -> Optional[Dict[Any, Any]]:
    """Load JSON file, returning None on error."""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return None


def save_json(path: Path, data: Dict[Any, Any], indent: int = 2) -> bool:
    """Save JSON file, returning True on success."""
    try:
        with open(path, 'w') as f:
            json.dump(data, f, indent=indent)
        return True
    except Exception:
        return False


def get_iso_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso_timestamp(ts: str) -> Optional[datetime]:
    """Parse ISO timestamp string to datetime."""
    try:
        # Handle both with and without timezone
        if ts.endswith('Z'):
            return datetime.fromisoformat(ts.replace('Z', '+00:00'))
        return datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return None


def run_git_command(args: List[str], cwd: Path = WORKSPACE_ROOT) -> Tuple[bool, str]:
    """Run a git command and return (success, output)."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            timeout=10,
            cwd=cwd
        )
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        return False, str(e)


def validate_against_schema(data: Dict, schema_name: str) -> List[str]:
    """Validate data against a JSON schema, return list of errors."""
    if not HAS_JSONSCHEMA:
        return ["jsonschema not installed - skipping validation"]

    schema_path = WORKSPACE_ROOT / ".claude" / "schema" / f"{schema_name}.json"
    if not schema_path.exists():
        return [f"Schema not found: {schema_name}"]

    try:
        schema = load_json(schema_path)
        if schema is None:
            return [f"Failed to load schema: {schema_name}"]

        validator = jsonschema.Draft7Validator(schema)
        errors = []
        for error in validator.iter_errors(data):
            path = ".".join(str(p) for p in error.path) if error.path else "root"
            errors.append(f"{path}: {error.message}")
        return errors[:5]  # Limit to first 5 errors
    except Exception as e:
        return [f"Schema validation error: {str(e)}"]


# =============================================================================
# Phase 1: Capability Directory-Summary Synchronization
# =============================================================================

def phase1_capability_sync(dry_run: bool, fix: bool, verbose: bool) -> PhaseResult:
    """Synchronize capability directories with capability_summary.json."""
    import time
    start = time.time()
    result = PhaseResult(name="Capability Directory-Summary Sync", passed=True, items_checked=0)

    capabilities_dir = WORKSPACE_ROOT / "capabilities"
    summary_path = WORKSPACE_ROOT / "status" / "capability_summary.json"

    # Load current summary
    summary = load_json(summary_path)
    if summary is None:
        result.issues.append(Issue(
            severity=Severity.CRITICAL,
            category="capability_summary",
            message="Failed to load capability_summary.json",
            path=str(summary_path)
        ))
        result.passed = False
        result.duration_ms = (time.time() - start) * 1000
        return result

    # Get capability directories (excluding hidden)
    cap_dirs = [d for d in capabilities_dir.iterdir()
                if d.is_dir() and not d.name.startswith('.')]

    # Get capabilities from summary
    summary_caps = {c.get('id') or c.get('folderName'): c
                    for c in summary.get('capabilities', [])}

    result.items_checked = len(cap_dirs) + len(summary_caps)

    # Check each directory
    for cap_dir in cap_dirs:
        folder_name = cap_dir.name
        track_file = cap_dir / "capability_track.json"

        # Check if capability_track.json exists
        if not track_file.exists():
            issue = Issue(
                severity=Severity.HIGH,
                category="capability_track",
                message=f"Missing capability_track.json for '{folder_name}'",
                path=str(cap_dir),
                auto_fixable=True,
                fix_description="Create skeleton capability_track.json"
            )

            if fix and not dry_run:
                # Create skeleton capability_track.json
                skeleton = create_capability_track_skeleton(folder_name)
                if save_json(track_file, skeleton):
                    issue.fixed = True
                    result.fixes_applied += 1

            result.issues.append(issue)
            result.passed = False
        else:
            # Validate against schema
            cap_data = load_json(track_file)
            if cap_data:
                errors = validate_against_schema(cap_data, "capability_track_schema")
                for error in errors:
                    result.issues.append(Issue(
                        severity=Severity.MEDIUM,
                        category="schema_validation",
                        message=f"Schema error in {folder_name}: {error}",
                        path=str(track_file)
                    ))

        # Check if in summary
        if folder_name not in summary_caps:
            issue = Issue(
                severity=Severity.HIGH,
                category="summary_sync",
                message=f"Capability '{folder_name}' not in summary",
                path=str(cap_dir),
                auto_fixable=True,
                fix_description="Add capability entry to summary"
            )

            if fix and not dry_run:
                # Add to summary
                cap_entry = create_capability_summary_entry(folder_name, cap_dir)
                if cap_entry:
                    summary['capabilities'].append(cap_entry)
                    summary['summary']['totalCapabilities'] = len(summary['capabilities'])
                    issue.fixed = True
                    result.fixes_applied += 1

            result.issues.append(issue)
            result.passed = False

    # Check for orphaned summary entries
    dir_names = {d.name for d in cap_dirs}
    for cap_id in summary_caps:
        if cap_id not in dir_names:
            issue = Issue(
                severity=Severity.MEDIUM,
                category="orphan_entry",
                message=f"Summary entry '{cap_id}' has no directory",
                auto_fixable=True,
                fix_description="Remove orphaned entry from summary"
            )

            if fix and not dry_run:
                summary['capabilities'] = [c for c in summary['capabilities']
                                          if (c.get('id') or c.get('folderName')) != cap_id]
                summary['summary']['totalCapabilities'] = len(summary['capabilities'])
                issue.fixed = True
                result.fixes_applied += 1

            result.issues.append(issue)

    # Save updated summary if fixes were applied
    if fix and not dry_run and result.fixes_applied > 0:
        summary['summary']['lastUpdated'] = get_iso_timestamp()
        save_json(summary_path, summary)

    result.duration_ms = (time.time() - start) * 1000
    return result


def create_capability_track_skeleton(folder_name: str) -> Dict:
    """Create a minimal capability_track.json skeleton."""
    name = folder_name.replace('-', ' ').title()
    return {
        "folderName": folder_name,
        "name": name,
        "description": f"[TODO] Describe what {name} enables the system to DO",
        "purpose": f"[TODO] Explain why {name} matters strategically",
        "type": "atomic",
        "status": "active",
        "currentMaturity": 0,
        "targetMaturity": 80,
        "coreValues": {
            "primary": ["Dependability"],
            "secondary": []
        },
        "outcomes": {
            "requiredOutcomes": [],
            "builtByOutcomes": []
        },
        "metadata": {
            "created": get_iso_timestamp(),
            "updated": get_iso_timestamp(),
            "directoryPath": f"capabilities/{folder_name}/",
            "hierarchyLevel": 0
        }
    }


def create_capability_summary_entry(folder_name: str, cap_dir: Path) -> Optional[Dict]:
    """Create a capability summary entry from directory."""
    track_file = cap_dir / "capability_track.json"

    if track_file.exists():
        cap_data = load_json(track_file)
        if cap_data:
            return {
                "id": folder_name,
                "folderName": folder_name,
                "name": cap_data.get('name', folder_name.replace('-', ' ').title()),
                "type": cap_data.get('type', 'atomic'),
                "status": cap_data.get('status', 'active'),
                "domain": cap_data.get('domain', 'Uncategorized'),
                "currentMaturity": cap_data.get('currentMaturity', 0),
                "targetMaturity": cap_data.get('targetMaturity', 80),
                "outcomeCount": len(cap_data.get('outcomes', {}).get('requiredOutcomes', [])),
                "completedOutcomeCount": len(cap_data.get('outcomes', {}).get('builtByOutcomes', [])),
                "directoryPath": f"capabilities/{folder_name}/"
            }

    # Minimal entry if no track file
    return {
        "id": folder_name,
        "folderName": folder_name,
        "name": folder_name.replace('-', ' ').title(),
        "type": "atomic",
        "status": "active",
        "domain": "Uncategorized",
        "currentMaturity": 0,
        "targetMaturity": 80,
        "outcomeCount": 0,
        "completedOutcomeCount": 0,
        "directoryPath": f"capabilities/{folder_name}/"
    }


# =============================================================================
# Phase 2: Outcome Directory-Summary Synchronization
# =============================================================================

def phase2_outcome_sync(dry_run: bool, fix: bool, verbose: bool) -> PhaseResult:
    """Synchronize outcome directories with outcome_summary.json."""
    import time
    start = time.time()
    result = PhaseResult(name="Outcome Directory-Summary Sync", passed=True, items_checked=0)

    outcomes_base = WORKSPACE_ROOT / "outcomes"
    summary_path = WORKSPACE_ROOT / "status" / "outcome_summary.json"
    states = ["queued", "in-progress", "completed"]

    # Load current summary
    summary = load_json(summary_path)
    if summary is None:
        result.issues.append(Issue(
            severity=Severity.CRITICAL,
            category="outcome_summary",
            message="Failed to load outcome_summary.json",
            path=str(summary_path)
        ))
        result.passed = False
        result.duration_ms = (time.time() - start) * 1000
        return result

    # Get outcomes from summary
    summary_outcomes = {o.get('id') or o.get('folderName'): o
                       for o in summary.get('outcomes', [])}

    found_outcomes = {}  # id -> (state, path)

    # Check each state directory
    for state in states:
        state_dir = outcomes_base / state
        if not state_dir.exists():
            continue

        # Get outcome directories
        outcome_dirs = [d for d in state_dir.iterdir()
                       if d.is_dir() and not d.name.startswith('.')]

        for outcome_dir in outcome_dirs:
            folder_name = outcome_dir.name
            result.items_checked += 1

            # Parse outcome ID from folder name (e.g., "001-name" -> "001")
            match = re.match(r'^(\d+)-(.+)$', folder_name)
            if not match:
                result.issues.append(Issue(
                    severity=Severity.MEDIUM,
                    category="naming",
                    message=f"Invalid outcome folder name: {folder_name}",
                    path=str(outcome_dir)
                ))
                continue

            outcome_id = match.group(1)
            found_outcomes[folder_name] = (state, outcome_dir)

            # Check outcome_track.json
            track_file = outcome_dir / "outcome_track.json"
            if not track_file.exists():
                issue = Issue(
                    severity=Severity.HIGH,
                    category="outcome_track",
                    message=f"Missing outcome_track.json for '{folder_name}'",
                    path=str(outcome_dir),
                    auto_fixable=True,
                    fix_description="Create skeleton outcome_track.json"
                )

                if fix and not dry_run:
                    skeleton = create_outcome_track_skeleton(folder_name, state)
                    if save_json(track_file, skeleton):
                        issue.fixed = True
                        result.fixes_applied += 1

                result.issues.append(issue)
                result.passed = False
            else:
                # Validate schema
                outcome_data = load_json(track_file)
                if outcome_data:
                    errors = validate_against_schema(outcome_data, "outcome_track_schema")
                    for error in errors:
                        result.issues.append(Issue(
                            severity=Severity.MEDIUM,
                            category="schema_validation",
                            message=f"Schema error in {folder_name}: {error}",
                            path=str(track_file)
                        ))

                    # Check state consistency
                    track_state = outcome_data.get('state')
                    if track_state and track_state != state:
                        result.issues.append(Issue(
                            severity=Severity.HIGH,
                            category="state_mismatch",
                            message=f"State mismatch: {folder_name} in '{state}/' but track says '{track_state}'",
                            path=str(track_file),
                            auto_fixable=True
                        ))

            # Check if in summary
            if folder_name not in summary_outcomes:
                issue = Issue(
                    severity=Severity.HIGH,
                    category="summary_sync",
                    message=f"Outcome '{folder_name}' not in summary",
                    path=str(outcome_dir),
                    auto_fixable=True,
                    fix_description="Add outcome entry to summary"
                )

                if fix and not dry_run:
                    entry = create_outcome_summary_entry(folder_name, state, outcome_dir)
                    if entry:
                        summary['outcomes'].append(entry)
                        issue.fixed = True
                        result.fixes_applied += 1

                result.issues.append(issue)
                result.passed = False
            else:
                # Check state matches
                summary_state = summary_outcomes[folder_name].get('state')
                if summary_state != state:
                    issue = Issue(
                        severity=Severity.HIGH,
                        category="state_mismatch",
                        message=f"Summary says '{folder_name}' is '{summary_state}' but found in '{state}/'",
                        auto_fixable=True
                    )

                    if fix and not dry_run:
                        # Update summary state
                        for o in summary['outcomes']:
                            if (o.get('id') or o.get('folderName')) == folder_name:
                                o['state'] = state
                                issue.fixed = True
                                result.fixes_applied += 1
                                break

                    result.issues.append(issue)

    # Check for orphaned summary entries
    for outcome_id in summary_outcomes:
        if outcome_id not in found_outcomes:
            issue = Issue(
                severity=Severity.MEDIUM,
                category="orphan_entry",
                message=f"Summary entry '{outcome_id}' has no directory",
                auto_fixable=True,
                fix_description="Remove orphaned entry from summary"
            )

            if fix and not dry_run:
                summary['outcomes'] = [o for o in summary['outcomes']
                                      if (o.get('id') or o.get('folderName')) != outcome_id]
                issue.fixed = True
                result.fixes_applied += 1

            result.issues.append(issue)

    # Save updated summary and recalculate stats
    if fix and not dry_run and result.fixes_applied > 0:
        recalculate_outcome_summary_stats(summary)
        summary['summary']['lastUpdated'] = get_iso_timestamp()
        save_json(summary_path, summary)

    result.duration_ms = (time.time() - start) * 1000
    return result


def create_outcome_track_skeleton(folder_name: str, state: str) -> Dict:
    """Create a minimal outcome_track.json skeleton."""
    match = re.match(r'^(\d+)-(.+)$', folder_name)
    if match:
        number = match.group(1)
        name_part = match.group(2)
        name = name_part.replace('-', ' ').title()
    else:
        number = "000"
        name = folder_name.replace('-', ' ').title()

    return {
        "outcomeId": folder_name,
        "number": int(number),
        "name": name,
        "description": f"[TODO] Describe what this outcome delivers",
        "state": state,
        "capabilities": [],
        "tasks": [],
        "executionLog": [],
        "estimatedTokens": 0,
        "consumedTokens": 0,
        "metadata": {
            "created": get_iso_timestamp(),
            "updated": get_iso_timestamp()
        }
    }


def create_outcome_summary_entry(folder_name: str, state: str, outcome_dir: Path) -> Optional[Dict]:
    """Create an outcome summary entry from directory."""
    track_file = outcome_dir / "outcome_track.json"

    if track_file.exists():
        outcome_data = load_json(track_file)
        if outcome_data:
            return {
                "id": folder_name,
                "folderName": folder_name,
                "name": outcome_data.get('name', folder_name),
                "state": state,
                "capabilities": outcome_data.get('capabilities', []),
                "taskCount": len(outcome_data.get('tasks', [])),
                "completedTaskCount": len([t for t in outcome_data.get('tasks', [])
                                          if t.get('state') == 'success']),
                "estimatedTokens": outcome_data.get('estimatedTokens', 0),
                "consumedTokens": outcome_data.get('consumedTokens', 0),
                "directoryPath": f"outcomes/{state}/{folder_name}/"
            }

    return {
        "id": folder_name,
        "folderName": folder_name,
        "name": folder_name,
        "state": state,
        "capabilities": [],
        "taskCount": 0,
        "completedTaskCount": 0,
        "estimatedTokens": 0,
        "consumedTokens": 0,
        "directoryPath": f"outcomes/{state}/{folder_name}/"
    }


def recalculate_outcome_summary_stats(summary: Dict):
    """Recalculate outcome summary statistics."""
    outcomes = summary.get('outcomes', [])

    by_state = {"queued": 0, "in-progress": 0, "completed": 0}
    total_tasks = 0
    completed_tasks = 0
    total_estimated = 0
    total_consumed = 0

    for o in outcomes:
        state = o.get('state', 'queued')
        if state in by_state:
            by_state[state] += 1
        total_tasks += o.get('taskCount', 0)
        completed_tasks += o.get('completedTaskCount', 0)
        total_estimated += o.get('estimatedTokens', 0)
        total_consumed += o.get('consumedTokens', 0)

    summary['summary'] = {
        "totalOutcomes": len(outcomes),
        "outcomesByState": by_state,
        "totalTasks": total_tasks,
        "tasksByState": {
            "ready": 0,
            "current": 0,
            "success": completed_tasks,
            "fail": 0
        },
        "totalEstimatedTokens": total_estimated,
        "totalConsumedTokens": total_consumed,
        "overallCompletionRate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
        "lastUpdated": get_iso_timestamp()
    }

    # Rebuild indexes
    summary['indexByState'] = {
        "queued": [o['id'] for o in outcomes if o.get('state') == 'queued'],
        "in-progress": [o['id'] for o in outcomes if o.get('state') == 'in-progress'],
        "completed": [o['id'] for o in outcomes if o.get('state') == 'completed']
    }

    # Rebuild capability index
    cap_index = {}
    for o in outcomes:
        for cap in o.get('capabilities', []):
            cap_id = cap if isinstance(cap, str) else cap.get('id', cap.get('folderName'))
            if cap_id:
                if cap_id not in cap_index:
                    cap_index[cap_id] = []
                cap_index[cap_id].append(o['id'])
    summary['indexByCapability'] = cap_index


# =============================================================================
# Phase 3: Cross-Reference Integrity Validation
# =============================================================================

def phase3_cross_reference_validation(dry_run: bool, fix: bool, verbose: bool) -> PhaseResult:
    """Validate cross-references between capabilities and outcomes."""
    import time
    start = time.time()
    result = PhaseResult(name="Cross-Reference Integrity", passed=True, items_checked=0)

    capabilities_dir = WORKSPACE_ROOT / "capabilities"
    outcomes_base = WORKSPACE_ROOT / "outcomes"

    # Build sets of existing entities
    existing_capabilities = set()
    existing_outcomes = {}  # folder_name -> state

    # Scan capabilities
    for cap_dir in capabilities_dir.iterdir():
        if cap_dir.is_dir() and not cap_dir.name.startswith('.'):
            existing_capabilities.add(cap_dir.name)

    # Scan outcomes
    for state in ["queued", "in-progress", "completed"]:
        state_dir = outcomes_base / state
        if state_dir.exists():
            for outcome_dir in state_dir.iterdir():
                if outcome_dir.is_dir() and not outcome_dir.name.startswith('.'):
                    existing_outcomes[outcome_dir.name] = state

    # Validate capability → outcome references
    for cap_name in existing_capabilities:
        track_file = capabilities_dir / cap_name / "capability_track.json"
        if not track_file.exists():
            continue

        cap_data = load_json(track_file)
        if not cap_data:
            continue

        result.items_checked += 1
        outcomes_section = cap_data.get('outcomes', {})

        # Check requiredOutcomes
        for req in outcomes_section.get('requiredOutcomes', []):
            path = req.get('outcomeTrackingFile', '')
            result.items_checked += 1

            # Extract outcome folder from path
            match = re.search(r'outcomes/(queued|in-progress|completed)/([^/]+)/', path)
            if match:
                expected_state = match.group(1)
                outcome_folder = match.group(2)

                if outcome_folder not in existing_outcomes:
                    result.issues.append(Issue(
                        severity=Severity.HIGH,
                        category="broken_reference",
                        message=f"Capability '{cap_name}' references non-existent outcome '{outcome_folder}'",
                        path=str(track_file)
                    ))
                    result.passed = False
                elif existing_outcomes[outcome_folder] != expected_state:
                    actual_state = existing_outcomes[outcome_folder]
                    result.issues.append(Issue(
                        severity=Severity.MEDIUM,
                        category="stale_reference",
                        message=f"Outcome '{outcome_folder}' moved from '{expected_state}' to '{actual_state}'",
                        path=str(track_file),
                        auto_fixable=True
                    ))

        # Check builtByOutcomes
        for built in outcomes_section.get('builtByOutcomes', []):
            path = built.get('outcomeTrackingFile', '')
            result.items_checked += 1

            match = re.search(r'outcomes/(queued|in-progress|completed)/([^/]+)/', path)
            if match:
                expected_state = match.group(1)
                outcome_folder = match.group(2)

                if outcome_folder not in existing_outcomes:
                    result.issues.append(Issue(
                        severity=Severity.HIGH,
                        category="broken_reference",
                        message=f"Capability '{cap_name}' builtBy non-existent outcome '{outcome_folder}'",
                        path=str(track_file)
                    ))
                    result.passed = False
                elif expected_state != "completed":
                    result.issues.append(Issue(
                        severity=Severity.MEDIUM,
                        category="invalid_reference",
                        message=f"builtByOutcome '{outcome_folder}' should be in completed/, not {expected_state}/",
                        path=str(track_file)
                    ))

        # Check composedOf references (for composed capabilities)
        if cap_data.get('type') == 'composed':
            composed_of = cap_data.get('relationships', {}).get('composedOf', [])
            total_weight = 0

            for sub in composed_of:
                sub_folder = sub.get('folderName')
                weight = sub.get('weight', 0)
                total_weight += weight
                result.items_checked += 1

                if sub_folder and sub_folder not in existing_capabilities:
                    result.issues.append(Issue(
                        severity=Severity.HIGH,
                        category="broken_reference",
                        message=f"Composed capability '{cap_name}' references non-existent sub-capability '{sub_folder}'",
                        path=str(track_file)
                    ))
                    result.passed = False

            # Check weights sum to 1.0
            if composed_of and abs(total_weight - 1.0) > 0.01:
                result.issues.append(Issue(
                    severity=Severity.MEDIUM,
                    category="invalid_weights",
                    message=f"Composed capability '{cap_name}' weights sum to {total_weight:.2f}, should be 1.0",
                    path=str(track_file)
                ))

    # Validate outcome → capability references
    for outcome_folder, state in existing_outcomes.items():
        track_file = outcomes_base / state / outcome_folder / "outcome_track.json"
        if not track_file.exists():
            continue

        outcome_data = load_json(track_file)
        if not outcome_data:
            continue

        result.items_checked += 1

        for cap_ref in outcome_data.get('capabilities', []):
            cap_id = cap_ref if isinstance(cap_ref, str) else cap_ref.get('id', cap_ref.get('folderName'))

            if cap_id and cap_id not in existing_capabilities:
                result.issues.append(Issue(
                    severity=Severity.MEDIUM,
                    category="broken_reference",
                    message=f"Outcome '{outcome_folder}' references non-existent capability '{cap_id}'",
                    path=str(track_file)
                ))

    result.duration_ms = (time.time() - start) * 1000
    return result


# =============================================================================
# Phase 4: Index Rebuild and Validation
# =============================================================================

def phase4_index_validation(dry_run: bool, fix: bool, verbose: bool) -> PhaseResult:
    """Validate and rebuild summary indexes."""
    import time
    start = time.time()
    result = PhaseResult(name="Index Validation & Rebuild", passed=True, items_checked=0)

    # Rebuild capability summary indexes
    cap_summary_path = WORKSPACE_ROOT / "status" / "capability_summary.json"
    cap_summary = load_json(cap_summary_path)

    if cap_summary:
        result.items_checked += 1
        caps = cap_summary.get('capabilities', [])

        # Expected indexes
        expected_by_type = {"atomic": [], "composed": []}
        expected_by_status = {"active": [], "deprecated": [], "merged": []}
        expected_by_domain = {}
        expected_by_maturity = {"0-30": [], "30-60": [], "60-80": [], "80-100": []}

        for cap in caps:
            cap_id = cap.get('id') or cap.get('folderName')
            cap_type = cap.get('type', 'atomic')
            status = cap.get('status', 'active')
            domain = cap.get('domain', 'Uncategorized')
            maturity = cap.get('currentMaturity', 0)

            if cap_type in expected_by_type:
                expected_by_type[cap_type].append(cap_id)
            if status in expected_by_status:
                expected_by_status[status].append(cap_id)
            if domain not in expected_by_domain:
                expected_by_domain[domain] = []
            expected_by_domain[domain].append(cap_id)

            if maturity < 30:
                expected_by_maturity["0-30"].append(cap_id)
            elif maturity < 60:
                expected_by_maturity["30-60"].append(cap_id)
            elif maturity < 80:
                expected_by_maturity["60-80"].append(cap_id)
            else:
                expected_by_maturity["80-100"].append(cap_id)

        # Compare with actual indexes
        actual_by_type = cap_summary.get('indexByType', {})
        if actual_by_type != expected_by_type:
            issue = Issue(
                severity=Severity.LOW,
                category="index_drift",
                message="capability_summary indexByType is out of sync",
                auto_fixable=True
            )

            if fix and not dry_run:
                cap_summary['indexByType'] = expected_by_type
                issue.fixed = True
                result.fixes_applied += 1

            result.issues.append(issue)

        actual_by_status = cap_summary.get('indexByStatus', {})
        if actual_by_status != expected_by_status:
            issue = Issue(
                severity=Severity.LOW,
                category="index_drift",
                message="capability_summary indexByStatus is out of sync",
                auto_fixable=True
            )

            if fix and not dry_run:
                cap_summary['indexByStatus'] = expected_by_status
                issue.fixed = True
                result.fixes_applied += 1

            result.issues.append(issue)

        # Save if fixes applied
        if fix and not dry_run and result.fixes_applied > 0:
            cap_summary['summary']['lastUpdated'] = get_iso_timestamp()
            save_json(cap_summary_path, cap_summary)

    # Validate session summary indexes
    session_summary_path = WORKSPACE_ROOT / "status" / "sessions_summary.json"
    session_summary = load_json(session_summary_path)

    if session_summary:
        result.items_checked += 1

        # Rebuild indexByBranch
        active = session_summary.get('activeSessions', [])
        history = session_summary.get('recentHistory', [])

        expected_by_branch = {}
        all_session_ids = set()

        for session in active:
            session_id = session.get('sessionId')
            branch = session.get('environment', {}).get('gitBranch', 'unknown')
            if session_id:
                all_session_ids.add(session_id)
                if branch not in expected_by_branch:
                    expected_by_branch[branch] = []
                expected_by_branch[branch].append(session_id)

        for session in history:
            session_id = session.get('sessionId')
            branch = session.get('gitBranch', 'unknown')
            if session_id:
                all_session_ids.add(session_id)
                if branch not in expected_by_branch:
                    expected_by_branch[branch] = []
                if session_id not in expected_by_branch[branch]:
                    expected_by_branch[branch].append(session_id)

        actual_by_branch = session_summary.get('indexByBranch', {})

        # Check for stale entries in index
        for branch, ids in actual_by_branch.items():
            for session_id in ids:
                if session_id not in all_session_ids:
                    result.issues.append(Issue(
                        severity=Severity.LOW,
                        category="stale_index",
                        message=f"indexByBranch contains stale session {session_id}",
                        auto_fixable=True
                    ))

        if fix and not dry_run:
            session_summary['indexByBranch'] = expected_by_branch
            session_summary['summary']['lastUpdated'] = get_iso_timestamp()
            save_json(session_summary_path, session_summary)
            result.fixes_applied += 1

    result.duration_ms = (time.time() - start) * 1000
    return result


# =============================================================================
# Phase 5: Temporal Health Checks
# =============================================================================

def phase5_temporal_health(dry_run: bool, fix: bool, verbose: bool) -> PhaseResult:
    """Check for stale timestamps and zombie sessions."""
    import time
    start = time.time()
    result = PhaseResult(name="Temporal Health", passed=True, items_checked=0)

    now = datetime.now(timezone.utc)

    # Check session summary
    session_path = WORKSPACE_ROOT / "status" / "sessions_summary.json"
    session_data = load_json(session_path)

    if session_data:
        result.items_checked += 1

        # Check for zombie sessions (active > 24h)
        for session in session_data.get('activeSessions', []):
            session_id = session.get('sessionId', 'unknown')
            started_at = parse_iso_timestamp(session.get('startedAt', ''))

            if started_at:
                age = now - started_at
                if age > timedelta(hours=24):
                    result.issues.append(Issue(
                        severity=Severity.MEDIUM,
                        category="zombie_session",
                        message=f"Session {session_id[:8]}... is {age.days}d {age.seconds//3600}h old",
                        auto_fixable=True,
                        fix_description="Run session reconciliation"
                    ))
                elif age > timedelta(hours=12):
                    result.issues.append(Issue(
                        severity=Severity.LOW,
                        category="old_session",
                        message=f"Session {session_id[:8]}... is {age.seconds//3600}h old",
                    ))

        # Check for stale history (older than 72h)
        history = session_data.get('recentHistory', [])
        stale_count = 0

        for session in history:
            completed_at = parse_iso_timestamp(session.get('completedAt', ''))
            if completed_at:
                age = now - completed_at
                if age > timedelta(hours=72):
                    stale_count += 1

        if stale_count > 0:
            issue = Issue(
                severity=Severity.LOW,
                category="stale_history",
                message=f"{stale_count} sessions in history are older than 72h",
                auto_fixable=True,
                fix_description="Prune old history entries"
            )

            if fix and not dry_run:
                cutoff = now - timedelta(hours=72)
                session_data['recentHistory'] = [
                    s for s in history
                    if parse_iso_timestamp(s.get('completedAt', '')) and
                       parse_iso_timestamp(s.get('completedAt', '')) > cutoff
                ]
                session_data['summary']['totalSessionsCompletedLast72Hours'] = len(session_data['recentHistory'])
                session_data['summary']['lastUpdated'] = get_iso_timestamp()
                save_json(session_path, session_data)
                issue.fixed = True
                result.fixes_applied += 1

            result.issues.append(issue)

    # Check lock file staleness
    lock_file = WORKSPACE_ROOT / "status" / ".sessions_summary.lock"
    if lock_file.exists():
        result.items_checked += 1
        lock_age = now - datetime.fromtimestamp(lock_file.stat().st_mtime, tz=timezone.utc)

        if lock_age > timedelta(minutes=5):
            issue = Issue(
                severity=Severity.MEDIUM,
                category="stale_lock",
                message=f"Lock file is {lock_age.seconds//60}m old (may be stale)",
                auto_fixable=True,
                fix_description="Remove stale lock file"
            )

            if fix and not dry_run:
                try:
                    lock_file.unlink()
                    issue.fixed = True
                    result.fixes_applied += 1
                except OSError:
                    pass

            result.issues.append(issue)

    # Check lastUpdated timestamps on summary files
    for summary_name, max_age_days in [
        ("capability_summary.json", 7),
        ("outcome_summary.json", 7),
        ("sessions_summary.json", 1)
    ]:
        summary_path = WORKSPACE_ROOT / "status" / summary_name
        if summary_path.exists():
            result.items_checked += 1
            data = load_json(summary_path)
            if data:
                last_updated = parse_iso_timestamp(data.get('summary', {}).get('lastUpdated', ''))
                if last_updated:
                    age = now - last_updated
                    if age > timedelta(days=max_age_days):
                        result.issues.append(Issue(
                            severity=Severity.INFO,
                            category="stale_timestamp",
                            message=f"{summary_name} not updated in {age.days} days"
                        ))

    result.duration_ms = (time.time() - start) * 1000
    return result


# =============================================================================
# Phase 6: Temp File Cleanup
# =============================================================================

def phase6_temp_cleanup(dry_run: bool, fix: bool, verbose: bool) -> PhaseResult:
    """Clean up temporary files based on retention policy."""
    import time
    start = time.time()
    result = PhaseResult(name="Temp File Cleanup", passed=True, items_checked=0)

    temp_dir = WORKSPACE_ROOT / ".claude" / "temp"
    if not temp_dir.exists():
        result.duration_ms = (time.time() - start) * 1000
        return result

    now = datetime.now(timezone.utc)

    # Retention policies from project_map.json
    policies = [
        ("exec-report-*.md", 72),
        ("agent-*.log", 12),
        ("search-*.json", 6),
        ("task-*.txt", 24),
    ]

    preserve_patterns = ["*.keep", "README.md"]
    files_removed = 0
    bytes_freed = 0

    for pattern, max_age_hours in policies:
        for file_path in temp_dir.glob(pattern):
            result.items_checked += 1

            # Check if should preserve
            should_preserve = any(file_path.match(p) for p in preserve_patterns)
            if should_preserve:
                continue

            # Check age
            file_age = now - datetime.fromtimestamp(file_path.stat().st_mtime, tz=timezone.utc)

            if file_age > timedelta(hours=max_age_hours):
                file_size = file_path.stat().st_size

                issue = Issue(
                    severity=Severity.INFO,
                    category="temp_file",
                    message=f"Temp file {file_path.name} is {file_age.seconds//3600}h old",
                    path=str(file_path),
                    auto_fixable=True
                )

                if fix and not dry_run:
                    try:
                        file_path.unlink()
                        files_removed += 1
                        bytes_freed += file_size
                        issue.fixed = True
                        result.fixes_applied += 1
                    except OSError:
                        pass

                result.issues.append(issue)

    if files_removed > 0 and verbose:
        result.issues.append(Issue(
            severity=Severity.INFO,
            category="cleanup_summary",
            message=f"Removed {files_removed} files, freed {bytes_freed/1024:.1f}KB"
        ))

    result.duration_ms = (time.time() - start) * 1000
    return result


# =============================================================================
# Phase 7: Git Health Check
# =============================================================================

def phase7_git_health(dry_run: bool, fix: bool, verbose: bool) -> PhaseResult:
    """Check git repository health."""
    import time
    start = time.time()
    result = PhaseResult(name="Git Health", passed=True, items_checked=0)

    # Check for uncommitted tracking files
    success, status_output = run_git_command(["status", "--porcelain"])
    if success:
        result.items_checked += 1

        tracking_files = [
            "status/sessions_summary.json",
            "status/capability_summary.json",
            "status/outcome_summary.json",
            "project_map.json"
        ]

        modified_tracking = []
        for line in status_output.split('\n'):
            if line:
                file_path = line[3:].strip()
                for tf in tracking_files:
                    if tf in file_path:
                        modified_tracking.append(tf)

        if modified_tracking:
            result.issues.append(Issue(
                severity=Severity.INFO,
                category="uncommitted_changes",
                message=f"Modified tracking files: {', '.join(modified_tracking)}"
            ))

    # Check remote tracking
    success, branch_output = run_git_command(["branch", "-vv"])
    if success:
        result.items_checked += 1

        current_branch = None
        has_upstream = False

        for line in branch_output.split('\n'):
            if line.startswith('*'):
                current_branch = line.split()[1]
                has_upstream = '[' in line and 'origin' in line
                break

        if current_branch and not has_upstream:
            result.issues.append(Issue(
                severity=Severity.LOW,
                category="no_upstream",
                message=f"Branch '{current_branch}' has no upstream tracking"
            ))

    # Check for merge conflicts
    success, diff_output = run_git_command(["diff", "--check"])
    if not success and "conflict" in diff_output.lower():
        result.issues.append(Issue(
            severity=Severity.HIGH,
            category="merge_conflict",
            message="Merge conflicts detected in working tree"
        ))
        result.passed = False

    result.duration_ms = (time.time() - start) * 1000
    return result


# =============================================================================
# Phase 8: Comprehensive Health Report
# =============================================================================

def print_health_report(report: HealthReport, verbose: bool):
    """Print the final health report."""
    print()
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}  WORKSPACE HEALTH REPORT{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
    print()

    # Overall status
    if report.overall_healthy:
        print(f"  {Colors.GREEN}{Icons.CHECK} Overall Status: HEALTHY{Colors.RESET}")
    else:
        print(f"  {Colors.RED}{Icons.CROSS} Overall Status: ISSUES FOUND{Colors.RESET}")

    print(f"  {Colors.GRAY}Timestamp: {report.timestamp}{Colors.RESET}")
    print()

    # Issue counts
    print(f"  {Colors.BOLD}Issue Summary:{Colors.RESET}")
    print(f"    {Colors.RED}Critical: {report.critical_count}{Colors.RESET}")
    print(f"    {Colors.YELLOW}High: {report.high_count}{Colors.RESET}")
    print(f"    {Colors.BLUE}Medium: {report.medium_count}{Colors.RESET}")
    print(f"    {Colors.GRAY}Low: {report.low_count}{Colors.RESET}")
    print(f"    {Colors.GREEN}Fixes Applied: {report.fixes_applied}{Colors.RESET}")
    print()

    # Phase results
    print(f"  {Colors.BOLD}Phase Results:{Colors.RESET}")
    print()

    for phase in report.phases:
        status_icon = f"{Colors.GREEN}{Icons.CHECK}" if phase.passed else f"{Colors.RED}{Icons.CROSS}"
        print(f"  {status_icon} {phase.name}{Colors.RESET}")
        print(f"    {Colors.GRAY}Checked: {phase.items_checked} | Duration: {phase.duration_ms:.0f}ms{Colors.RESET}")

        if phase.fixes_applied > 0:
            print(f"    {Colors.GREEN}{Icons.FIX} Fixed: {phase.fixes_applied}{Colors.RESET}")

        # Show issues for this phase
        if phase.issues:
            critical_high = [i for i in phase.issues if i.severity in [Severity.CRITICAL, Severity.HIGH]]
            if critical_high or verbose:
                issues_to_show = phase.issues if verbose else critical_high[:3]
                for issue in issues_to_show:
                    severity_color = {
                        Severity.CRITICAL: Colors.RED,
                        Severity.HIGH: Colors.YELLOW,
                        Severity.MEDIUM: Colors.BLUE,
                        Severity.LOW: Colors.GRAY,
                        Severity.INFO: Colors.GRAY
                    }.get(issue.severity, Colors.WHITE)

                    fixed_mark = f" {Colors.GREEN}[FIXED]{Colors.RESET}" if issue.fixed else ""
                    print(f"      {severity_color}[{issue.severity.value}]{Colors.RESET} {issue.message}{fixed_mark}")

                remaining = len(phase.issues) - len(issues_to_show)
                if remaining > 0:
                    print(f"      {Colors.GRAY}... and {remaining} more (use --verbose to see all){Colors.RESET}")
        print()

    # Summary statistics
    print(f"  {Colors.BOLD}Workspace Statistics:{Colors.RESET}")

    # Load summaries for stats
    cap_summary = load_json(WORKSPACE_ROOT / "status" / "capability_summary.json")
    outcome_summary = load_json(WORKSPACE_ROOT / "status" / "outcome_summary.json")
    session_summary = load_json(WORKSPACE_ROOT / "status" / "sessions_summary.json")

    if cap_summary:
        caps = cap_summary.get('summary', {})
        print(f"    Capabilities: {caps.get('totalCapabilities', 0)}")
        print(f"    Avg Maturity: {caps.get('averageMaturity', 0):.0f}%")

    if outcome_summary:
        outs = outcome_summary.get('summary', {})
        by_state = outs.get('outcomesByState', {})
        print(f"    Outcomes: {outs.get('totalOutcomes', 0)} (Q:{by_state.get('queued', 0)}/I:{by_state.get('in-progress', 0)}/C:{by_state.get('completed', 0)})")

    if session_summary:
        sess = session_summary.get('summary', {})
        print(f"    Active Sessions: {sess.get('activeSessionsCount', 0)}")
        print(f"    Sessions (72h): {sess.get('totalSessionsCompletedLast72Hours', 0)}")

    print()
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")

    # Recommendations
    if not report.overall_healthy:
        print()
        print(f"  {Colors.BOLD}Recommended Actions:{Colors.RESET}")

        if report.critical_count > 0:
            print(f"    {Colors.RED}1. Fix critical issues immediately{Colors.RESET}")
            print(f"       Run: python3 workspace_health.py --fix")

        if report.high_count > 0:
            print(f"    {Colors.YELLOW}2. Address high-priority issues{Colors.RESET}")
            print(f"       Run: python3 workspace_health.py --fix --verbose")

        print()


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    """Main entry point for workspace health check."""
    parser = argparse.ArgumentParser(
        description="Comprehensive workspace health check and maintenance"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed information"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix issues where possible"
    )
    parser.add_argument(
        "--phase",
        type=int,
        choices=[1, 2, 3, 4, 5, 6, 7, 8],
        help="Run only specific phase"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output report as JSON"
    )

    args = parser.parse_args()

    print()
    print(f"{Colors.CYAN}{Icons.SYNC} Workspace Health Check Starting...{Colors.RESET}")

    if args.dry_run:
        print(f"{Colors.YELLOW}{Icons.WARN} DRY RUN MODE - No changes will be saved{Colors.RESET}")

    if args.fix:
        print(f"{Colors.GREEN}{Icons.FIX} AUTO-FIX MODE - Will attempt to fix issues{Colors.RESET}")

    print()

    # Initialize report
    report = HealthReport(timestamp=get_iso_timestamp())

    # Phase functions
    phases = [
        (1, "Capability Sync", phase1_capability_sync),
        (2, "Outcome Sync", phase2_outcome_sync),
        (3, "Cross-References", phase3_cross_reference_validation),
        (4, "Index Validation", phase4_index_validation),
        (5, "Temporal Health", phase5_temporal_health),
        (6, "Temp Cleanup", phase6_temp_cleanup),
        (7, "Git Health", phase7_git_health),
    ]

    # Run phases
    for phase_num, phase_name, phase_func in phases:
        if args.phase and args.phase != phase_num:
            continue

        print(f"{Colors.CYAN}Phase {phase_num}: {phase_name}...{Colors.RESET}")

        try:
            phase_result = phase_func(args.dry_run, args.fix, args.verbose)
            report.add_phase(phase_result)

            if phase_result.passed:
                print(f"  {Colors.GREEN}{Icons.CHECK} Passed{Colors.RESET}")
            else:
                print(f"  {Colors.YELLOW}{Icons.WARN} Issues found: {len(phase_result.issues)}{Colors.RESET}")

            if phase_result.fixes_applied > 0:
                print(f"  {Colors.GREEN}{Icons.FIX} Fixed: {phase_result.fixes_applied}{Colors.RESET}")

        except Exception as e:
            print(f"  {Colors.RED}{Icons.CROSS} Error: {str(e)}{Colors.RESET}")
            report.add_phase(PhaseResult(
                name=phase_name,
                passed=False,
                issues=[Issue(
                    severity=Severity.CRITICAL,
                    category="phase_error",
                    message=f"Phase failed with error: {str(e)}"
                )]
            ))

    # Output report
    if args.json:
        # JSON output
        json_report = {
            "timestamp": report.timestamp,
            "overall_healthy": report.overall_healthy,
            "critical_count": report.critical_count,
            "high_count": report.high_count,
            "medium_count": report.medium_count,
            "low_count": report.low_count,
            "fixes_applied": report.fixes_applied,
            "phases": [
                {
                    "name": p.name,
                    "passed": p.passed,
                    "items_checked": p.items_checked,
                    "fixes_applied": p.fixes_applied,
                    "duration_ms": p.duration_ms,
                    "issues": [
                        {
                            "severity": i.severity.value,
                            "category": i.category,
                            "message": i.message,
                            "path": i.path,
                            "fixed": i.fixed
                        }
                        for i in p.issues
                    ]
                }
                for p in report.phases
            ]
        }
        print(json.dumps(json_report, indent=2))
    else:
        print_health_report(report, args.verbose)

    # Exit code
    sys.exit(0 if report.overall_healthy else 1)


if __name__ == "__main__":
    main()
