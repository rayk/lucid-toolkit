#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# ///
"""Get current Claude Code session information.

Reads the debug symlink to find current session ID and transcript path.
"""
import json
from pathlib import Path


def get_session_info():
    """Get current session ID and transcript path."""
    debug_dir = Path.home() / ".claude" / "debug"
    latest_link = debug_dir / "latest"

    result = {
        "session_id": None,
        "transcript_path": None,
        "debug_log_path": None
    }

    try:
        if latest_link.is_symlink():
            # Get debug log path from symlink
            debug_log = latest_link.resolve()
            result["debug_log_path"] = str(debug_log)

            # Session ID is the filename without .txt
            session_id = debug_log.stem
            result["session_id"] = session_id

            # Transcript is in ~/.claude/projects/<hash>/transcripts/<session_id>.jsonl
            # We need to find it by searching
            projects_dir = Path.home() / ".claude" / "projects"
            if projects_dir.exists():
                for project_dir in projects_dir.iterdir():
                    if project_dir.is_dir():
                        transcript = project_dir / "transcripts" / f"{session_id}.jsonl"
                        if transcript.exists():
                            result["transcript_path"] = str(transcript)
                            break
    except Exception as e:
        result["error"] = str(e)

    return result


def main():
    info = get_session_info()
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
