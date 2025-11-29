#!/usr/bin/env python3
"""Context session start hook.

Triggered when a new Claude Code session begins. Initializes context tracking
and establishes baseline metrics for context window conservation.

Path Structure:
  - .lucid/current_session.json       - Active session state (transient)
  - status/sessions_summary.json      - All sessions index (persistent)

The current session file tracks real-time state for the active session.
The sessions summary maintains a historical index of all sessions for
cross-session analysis and work resumption.
"""

import json
import logging
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from lucid_cli_commons.locking import atomic_write

logging.basicConfig(level=logging.WARNING, format='[context] %(levelname)s: %(message)s', stream=sys.stderr)
logger = logging.getLogger(__name__)


def get_current_session_path() -> Path:
    """Get path to current session file in .lucid directory."""
    lucid_dir = Path.cwd() / ".lucid"
    lucid_dir.mkdir(exist_ok=True)
    return lucid_dir / "current_session.json"


def get_sessions_summary_path() -> Path:
    """Get path to sessions summary file in status directory."""
    status_dir = Path.cwd() / "status"
    status_dir.mkdir(exist_ok=True)
    return status_dir / "sessions_summary.json"


def generate_session_id() -> str:
    """Generate unique session identifier."""
    return f"sess-{uuid.uuid4().hex[:12]}"


def initialize_session_record() -> dict:
    """Initialize a new session tracking record."""
    return {
        "sessionId": generate_session_id(),
        "startTime": datetime.now(timezone.utc).isoformat(),
        "endTime": None,
        "status": "active",
        "metrics": {
            "toolCalls": 0,
            "delegations": 0,
            "checkpoints": [],
            "contextSaved": 0
        },
        "violations": []
    }


def load_sessions_summary() -> dict:
    """Load existing sessions summary or create new structure."""
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
    """Add new session to sessions summary."""
    summary = load_sessions_summary()

    # Add to active sessions
    summary["activeSessions"].append({
        "sessionId": session_record["sessionId"],
        "startTime": session_record["startTime"],
        "status": session_record["status"]
    })

    # Write updated summary
    summary_path = get_sessions_summary_path()
    with atomic_write(summary_path, timeout=10) as f:
        json.dump(summary, f, indent=2)


def main() -> int:
    """Execute context start hook."""
    # Initialize new session record
    session_record = initialize_session_record()

    # Write current session file
    current_session_path = get_current_session_path()
    with atomic_write(current_session_path, timeout=10) as f:
        json.dump(session_record, f, indent=2)

    # Update sessions summary
    update_sessions_summary(session_record)

    print(f"Context tracking initialized:", file=sys.stderr)
    print(f"  Current session: {current_session_path}", file=sys.stderr)
    print(f"  Sessions summary: {get_sessions_summary_path()}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
