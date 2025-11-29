#!/usr/bin/env python3
"""Context session end hook.

Triggered when a Claude Code session ends. Finalizes context tracking
and generates session summary metrics.

Path Structure:
  - .lucid/current_session.json       - Active session state (finalized then archived)
  - status/sessions_summary.json      - All sessions index (updated with completion)

The current session is finalized with end time and moved from activeSessions
to completedSessions in the summary. The current_session.json file is preserved
for potential recovery or analysis.
"""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from lucid_cli_commons.locking import atomic_write

logging.basicConfig(level=logging.WARNING, format='[context] %(levelname)s: %(message)s', stream=sys.stderr)
logger = logging.getLogger(__name__)


def get_current_session_path() -> Path:
    """Get path to current session file in .lucid directory."""
    return Path.cwd() / ".lucid" / "current_session.json"


def get_sessions_summary_path() -> Path:
    """Get path to sessions summary file in status directory."""
    return Path.cwd() / "status" / "sessions_summary.json"


def finalize_session_record(session: dict) -> dict:
    """Finalize session record with end time and status."""
    session["endTime"] = datetime.now(timezone.utc).isoformat()
    session["status"] = "completed"
    return session


def load_sessions_summary() -> dict:
    """Load existing sessions summary."""
    summary_path = get_sessions_summary_path()
    if summary_path.exists():
        try:
            with open(summary_path) as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            backup_path = summary_path.with_suffix('.json.corrupt')
            logger.error(f"Corrupted JSON at {summary_path}: {e}. Backing up to {backup_path}")
            summary_path.rename(backup_path)
        except IOError as e:
            logger.error(f"IO error reading {summary_path}: {e}")

    return {
        "activeSessions": [],
        "completedSessions": [],
        "staleSessions": []
    }


def update_sessions_summary(session_record: dict) -> None:
    """Move session from active to completed in sessions summary."""
    summary = load_sessions_summary()
    session_id = session_record.get("sessionId")

    # Remove from active sessions
    summary["activeSessions"] = [
        s for s in summary["activeSessions"]
        if s.get("sessionId") != session_id
    ]

    # Add to completed sessions
    summary["completedSessions"].append({
        "sessionId": session_id,
        "startTime": session_record["startTime"],
        "endTime": session_record["endTime"],
        "status": session_record["status"],
        "metrics": session_record.get("metrics", {}),
        "violations": session_record.get("violations", [])
    })

    # Write updated summary
    summary_path = get_sessions_summary_path()
    with atomic_write(summary_path, timeout=10) as f:
        json.dump(summary, f, indent=2)


def main() -> int:
    """Execute context end hook."""
    current_session_path = get_current_session_path()

    if not current_session_path.exists():
        print("No active session found", file=sys.stderr)
        return 0

    # Load current session
    try:
        with open(current_session_path) as f:
            session = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading session: {e}", file=sys.stderr)
        return 1

    # Finalize session
    session = finalize_session_record(session)

    # Write finalized session (kept for archival/recovery)
    with atomic_write(current_session_path, timeout=10) as f:
        json.dump(session, f, indent=2)

    # Update sessions summary
    update_sessions_summary(session)

    # Print summary
    metrics = session.get("metrics", {})
    print(f"Session completed:", file=sys.stderr)
    print(f"  Session ID: {session.get('sessionId', 'unknown')}", file=sys.stderr)
    print(f"  Tool calls: {metrics.get('toolCalls', 0)}", file=sys.stderr)
    print(f"  Delegations: {metrics.get('delegations', 0)}", file=sys.stderr)
    print(f"  Checkpoints: {len(metrics.get('checkpoints', []))}", file=sys.stderr)
    print(f"  Violations: {len(session.get('violations', []))}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
