#!/usr/bin/env python3
"""SessionEnd hook - executed when Claude Code session ends.

Reads JSON from stdin with session end information, updates the session
entry with end timestamp and details, then moves it from activeSessions
to recentHistory.

Input JSON format (from Claude Code):
{
  "session_id": "7096cff8-4c25-43e1-9f12-9c51574bed16",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "permission_mode": "default|plan|acceptEdits|bypassPermissions",
  "hook_event_name": "SessionEnd",
  "reason": "clear|logout|prompt_input_exit|other"
}

Output JSON format:
{}  // Empty object - SessionEnd hooks perform side effects only

Note: Claude Code validates hook output against a strict control field schema.
Returning custom fields like "success" or "message" will cause validation errors.
SessionEnd hooks should return empty JSON {} and rely on exit code for status.
"""

import sys
import json
import os
from datetime import datetime, timezone
from pathlib import Path

# Check for required dependencies before importing
def check_dependencies():
    """Check if required dependencies are installed."""
    missing = []
    try:
        import filelock
    except ImportError:
        missing.append("filelock")

    try:
        import jsonschema
    except ImportError:
        missing.append("jsonschema")

    if missing:
        error_response = {
            "success": False,
            "message": f"Missing required dependencies: {', '.join(missing)}. Install with: pip3 install -r hooks/requirements.txt"
        }
        print(json.dumps(error_response, indent=2))
        sys.exit(1)

# Check dependencies first
check_dependencies()

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from session_summary.lib.session_manager import SessionManager
from lucid_cli_commons.git_utils import GitInfo


def main():
    """Main entry point for session_end hook."""
    try:
        # Read JSON from stdin
        input_data = json.load(sys.stdin)

        # Extract required fields (from Claude Code's actual input format)
        session_id = input_data.get("session_id")
        reason = input_data.get("reason")  # Claude Code sends "reason" not "end_reason"

        # Validate required fields
        if not session_id:
            output_error("Missing required field: session_id")
            return

        if not reason:
            output_error("Missing required field: reason")
            return

        # Extract optional fields
        accomplishments_list = input_data.get("accomplishments", [])
        outcomes_worked = input_data.get("outcomes_worked", [])

        # Convert accomplishments array to semicolon-separated string
        accomplishments = "; ".join(accomplishments_list) if accomplishments_list else ""

        # Initialize session manager
        # Use workspace root from environment if set (for testing)
        workspace_root = os.environ.get("CLAUDE_WORKSPACE_ROOT")
        if workspace_root:
            manager = SessionManager(Path(workspace_root))
            git_info = GitInfo(Path(workspace_root))
        else:
            manager = SessionManager()
            git_info = GitInfo()

        # Load current data to get session details before removal
        data = manager.load()
        session = None
        for s in data["activeSessions"]:
            if s["sessionId"] == session_id:
                session = s
                break

        if session is None:
            output_error(f"Session not found: {session_id}")
            return

        # Parse transcript to extract statistics
        from session_summary.lib.transcript_parser import TranscriptParser
        from session_summary.lib.accomplishments import generate_accomplishments

        transcript_path = Path(session["environment"]["transcriptPath"])
        parser = TranscriptParser(transcript_path)
        stats = parser.parse()

        # Update session statistics before moving to history
        session["statistics"]["tokensConsumed"] = stats.tokens_consumed
        session["statistics"]["filesModified"] = len(stats.files_modified)
        session["statistics"]["tasksCompleted"] = stats.tasks_completed
        session["statistics"]["tasksFailed"] = stats.tasks_failed
        session["subagentsLaunched"] = stats.subagents_launched
        session["toolUsageCounts"] = stats.tool_usage_counts

        # Generate meaningful accomplishments from transcript stats
        # If user provided accomplishments, use those (backward compatibility)
        if accomplishments:
            # User provided accomplishments - keep them
            pass
        else:
            # Generate from session data
            accomplishments = generate_accomplishments(stats, git_info)

        # Calculate duration
        started_at = datetime.fromisoformat(session["startedAt"].replace("Z", "+00:00"))
        ended_at = datetime.now(timezone.utc)
        duration_minutes = (ended_at - started_at).total_seconds() / 60

        # Remove active session and move to history
        manager.remove_active_session(
            session_id=session_id,
            end_reason=reason,
            accomplishments=accomplishments,
            git_info=git_info
        )

        # Output success
        output_success(
            message=f"Session ended successfully: {session_id}",
            session_id=session_id,
            duration=round(duration_minutes, 2),
            moved_to_history=True
        )

    except json.JSONDecodeError as e:
        output_error(f"Invalid JSON input: {e}")
    except ValueError as e:
        output_error(str(e))
    except Exception as e:
        output_error(f"Unexpected error: {e}")


def output_success(message: str, **kwargs):
    """Output successful result as JSON with systemMessage for user visibility."""
    # Log to stderr for debugging (Claude Code displays stderr in logs)
    sys.stderr.write(f"[SessionEnd] {message}\n")

    duration = kwargs.get("duration")
    if duration:
        sys.stderr.write(f"[SessionEnd] Duration: {duration} minutes\n")

    # Return JSON with systemMessage to display to user
    if duration:
        display_msg = f"Session ended ({duration} min)"
    else:
        display_msg = "Session ended"

    result = {
        "systemMessage": display_msg
    }
    print(json.dumps(result))


def output_error(message: str):
    """Output error result as JSON."""
    # Claude Code validates hook output against a strict schema.
    # For errors, we write to stderr and return empty JSON with exit code 0.
    # Non-zero exit codes cause Claude Code to show generic error messages.
    import sys
    sys.stderr.write(f"SessionEnd hook error: {message}\n")
    result = {}  # Empty object is valid
    print(json.dumps(result))


if __name__ == "__main__":
    main()
