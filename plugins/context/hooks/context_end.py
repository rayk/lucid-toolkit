#!/usr/bin/env python3
"""Context session end hook.

Triggered when a Claude Code session ends. Finalizes context tracking
and generates session summary metrics.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def get_context_tracking_path() -> Path:
    """Get path to context tracking file in .lucid directory."""
    return Path.cwd() / ".lucid" / "context_tracking.json"


def finalize_context_tracking(tracking: dict) -> dict:
    """Finalize context tracking record with end time and status."""
    tracking["endTime"] = datetime.now(timezone.utc).isoformat()
    tracking["status"] = "completed"
    return tracking


def main() -> int:
    """Execute context end hook."""
    tracking_path = get_context_tracking_path()

    if not tracking_path.exists():
        print("No active context tracking found", file=sys.stderr)
        return 0

    # Load existing tracking
    with open(tracking_path) as f:
        tracking = json.load(f)

    # Finalize tracking
    tracking = finalize_context_tracking(tracking)

    # Write updated tracking
    with open(tracking_path, "w") as f:
        json.dump(tracking, f, indent=2)

    # Print summary
    metrics = tracking.get("metrics", {})
    print(f"Session completed:", file=sys.stderr)
    print(f"  Tool calls: {metrics.get('toolCalls', 0)}", file=sys.stderr)
    print(f"  Delegations: {metrics.get('delegations', 0)}", file=sys.stderr)
    print(f"  Checkpoints: {len(metrics.get('checkpoints', []))}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
