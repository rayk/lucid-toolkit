#!/usr/bin/env python3
"""
Regenerate capability snapshot hook.

Triggered after any tool modifies capability_summary.json.
Regenerates status/capability_snapshot.md for instant display.
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, Any

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lucid_cli_commons.paths import get_paths
from lucid_cli_commons.locking import atomic_write


def read_input() -> Dict[str, Any]:
    """
    Read and parse JSON from stdin.

    Returns:
        Parsed input dictionary (may be empty for some hook types)
    """
    try:
        input_text = sys.stdin.read()
        if not input_text.strip():
            return {}
        return json.loads(input_text)
    except json.JSONDecodeError:
        return {}


def generate_snapshot(summary_data: Dict[str, Any]) -> str:
    """
    Generate formatted markdown snapshot from summary data.

    Args:
        summary_data: Parsed capability_summary.json content

    Returns:
        Formatted markdown string
    """
    from datetime import datetime

    summary = summary_data.get("summary", {})
    index_by_domain = summary_data.get("indexByDomain", {})
    blocked_caps = summary_data.get("blockedCapabilities", [])
    at_risk_caps = summary_data.get("atRiskCapabilities", [])

    # Count capabilities
    total_caps = sum(len(caps) for caps in index_by_domain.values())

    # Activity states
    activity = summary.get("capabilitiesByActivityState", {})
    active = activity.get("active", 0)
    stalled = activity.get("stalled", 0)
    complete = activity.get("complete", 0)

    # Build capability lookup
    cap_info = {cap["folderName"]: cap for cap in at_risk_caps}

    lines = []

    # Header with full timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z").strip()
    if not timestamp.endswith(('UTC', 'EST', 'PST', 'CST', 'MST', 'EDT', 'PDT', 'CDT', 'MDT')):
        # Fallback to explicit local time indicator
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S (local)")
    lines.append(f"## Capability Snapshot")
    lines.append(f"Generated: {timestamp}")
    lines.append("")

    # Summary table
    lines.extend([
        "### Summary",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total Capabilities | {total_caps} |",
        f"| Average Maturity | {summary.get('averageMaturity', 0)}% |",
        f"| Active/Stalled/Complete | {active}/{stalled}/{complete} |",
        f"| Blocked | {summary.get('blockedCapabilitiesCount', 0)} |",
        f"| At Risk | {summary.get('atRiskCapabilitiesCount', 0)} |",
        ""
    ])

    # By Domain
    lines.append("### By Domain\n")
    for domain, cap_ids in sorted(index_by_domain.items()):
        if not cap_ids:
            continue

        lines.append(f"#### {domain}")
        lines.append("| Capability | Maturity | Target | Status |")
        lines.append("|------------|----------|--------|--------|")

        for cap_id in cap_ids:
            info = cap_info.get(cap_id, {})
            maturity_gap = info.get("maturityGap", 80)
            target = maturity_gap if maturity_gap >= 80 else 80
            current = target - maturity_gap

            activity_state = info.get("activityState", "stalled")
            is_blocked = cap_id in blocked_caps
            status = "Blocked" if is_blocked else activity_state.capitalize()

            lines.append(f"| {cap_id} | {current}% | {target}% | {status} |")

        lines.append("")

    # Maturity Distribution
    dist = summary.get("maturityDistribution", {})
    low = dist.get("0-30", 0)
    mid_low = dist.get("30-60", 0)
    mid_high = dist.get("60-80", 0)
    high = dist.get("80-100", 0)
    total = low + mid_low + mid_high + high

    def bar(count: int, max_width: int = 20) -> str:
        if total == 0 or count == 0:
            return ""
        width = int((count / total) * max_width)
        return "" * width if width > 0 else ""

    lines.extend([
        "### Maturity Distribution",
        "```",
        f"[0-30%]:   {bar(low)} {low} caps",
        f"[30-60%]:  {bar(mid_low)} {mid_low} caps",
        f"[60-80%]:  {bar(mid_high)} {mid_high} caps",
        f"[80-100%]: {bar(high)} {high} caps",
        "```",
        ""
    ])

    # Blocked
    if blocked_caps:
        lines.append(f"### Blocked Capabilities ({len(blocked_caps)})")
        for cap_id in blocked_caps:
            lines.append(f"- {cap_id}")
        lines.append("")
    else:
        lines.extend(["### Blocked Capabilities", "None", ""])

    # At Risk (top 5)
    if at_risk_caps:
        sorted_caps = sorted(at_risk_caps, key=lambda x: x.get("maturityGap", 0), reverse=True)[:5]
        lines.extend([
            "### At Risk (Top 5 by Maturity Gap)",
            "| Capability | Gap | State |",
            "|------------|-----|-------|",
        ])
        for cap in sorted_caps:
            lines.append(f"| {cap['folderName']} | {cap.get('maturityGap', 0)}% | {cap.get('activityState', 'unknown')} |")
        lines.append("")
    else:
        lines.extend(["### At Risk", "None", ""])

    # Health assessment
    assessment_parts = []
    if summary.get("averageMaturity", 0) == 0:
        assessment_parts.append("All capabilities at 0% maturity")
    else:
        assessment_parts.append(f"Average maturity: {summary.get('averageMaturity', 0)}%")

    if active == 0:
        assessment_parts.append("no active work")
    else:
        assessment_parts.append(f"{active} actively progressing")

    if blocked_caps:
        assessment_parts.append(f"{len(blocked_caps)} of {total_caps} blocked")

    # Find unblocked for recommendation
    unblocked = []
    for caps in index_by_domain.values():
        for cap in caps:
            if cap not in blocked_caps:
                unblocked.append(cap)

    recommendation = ""
    if unblocked and blocked_caps:
        suggestions = unblocked[:4]
        recommendation = f"\n\nRecommend prioritizing unblocked: {', '.join(suggestions)}"

    lines.append(f"---\n**Health**: {'. '.join(assessment_parts)}.{recommendation}")

    return "\n".join(lines)


def output_response(success: bool, message: str) -> None:
    """
    Output JSON response for hook.

    Args:
        success: Whether operation succeeded
        message: Human-readable message
    """
    if success:
        sys.stderr.write(f"[CapabilitySnapshot] {message}\n")
    else:
        sys.stderr.write(f"[CapabilitySnapshot ERROR] {message}\n")

    # Return empty JSON to pass Claude Code's hook validator
    print(json.dumps({}))


def main() -> None:
    """Main hook execution."""
    try:
        # Read input (may be empty)
        read_input()

        # Get workspace paths
        workspace_root = os.environ.get("CLAUDE_WORKSPACE_ROOT")
        if workspace_root:
            paths = get_paths(Path(workspace_root))
        else:
            paths = get_paths()

        # Read capability summary
        summary_path = paths.capability_summary
        if not summary_path.exists():
            output_response(False, f"Capability summary not found: {summary_path}")
            sys.exit(1)

        with open(summary_path, "r") as f:
            summary_data = json.load(f)

        # Generate snapshot
        snapshot_md = generate_snapshot(summary_data)

        # Write snapshot atomically to capabilities root
        snapshot_path = paths.workspace_root / "capabilities" / "SNAPSHOT.md"
        with atomic_write(snapshot_path, timeout=10) as f:
            f.write(snapshot_md)

        output_response(True, f"Snapshot regenerated: {snapshot_path}")

    except FileNotFoundError as e:
        output_response(False, f"File not found: {e}")
        sys.exit(1)

    except json.JSONDecodeError as e:
        output_response(False, f"Invalid JSON: {e}")
        sys.exit(1)

    except Exception as e:
        output_response(False, f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
