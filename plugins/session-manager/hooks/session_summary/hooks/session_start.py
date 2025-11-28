#!/usr/bin/env python3
"""SessionStart hook - executed when Claude Code session starts."""

import sys
import json
import os
from pathlib import Path
from typing import Dict, Any

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


def read_input() -> Dict[str, Any]:
    """
    Read and parse JSON from stdin.

    Returns:
        Parsed input dictionary

    Raises:
        ValueError: If input is not valid JSON
    """
    try:
        input_text = sys.stdin.read()
        return json.loads(input_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse input JSON: {e}") from e


def validate_input(data: Dict[str, Any]) -> None:
    """
    Validate required input fields.

    Args:
        data: Input data dictionary

    Raises:
        ValueError: If required fields are missing
    """
    required_fields = ["session_id", "source", "transcript_path"]

    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")


def output_response(success: bool, message: str, hook_output: Dict[str, Any] = None) -> None:
    """
    Output JSON response with systemMessage for user visibility.

    Uses the systemMessage field to display status to the user during hook execution.
    This provides feedback that startup scripts are running.

    Args:
        success: Whether operation succeeded
        message: Human-readable message
        hook_output: Optional hook-specific output data (logged to stderr)
    """
    # Log to stderr for debugging (Claude Code displays stderr in logs)
    if success:
        sys.stderr.write(f"[SessionStart] {message}\n")
        if hook_output:
            sys.stderr.write(f"[SessionStart] Active sessions: {hook_output.get('activeSessionsCount', 0)}\n")
    else:
        sys.stderr.write(f"[SessionStart ERROR] {message}\n")

    # Return JSON with systemMessage to display to user
    if success:
        active_count = hook_output.get('activeSessionsCount', 1) if hook_output else 1
        response = {
            "systemMessage": f"Session initialized ({active_count} active)"
        }
    else:
        response = {
            "systemMessage": f"Session startup warning: {message}"
        }
    print(json.dumps(response))


def main() -> None:
    """Main hook execution."""
    try:
        # Read and validate input
        input_data = read_input()
        validate_input(input_data)

        # Extract fields
        session_id = input_data["session_id"]
        source = input_data["source"]
        permission_mode = input_data.get("permission_mode", "default")
        transcript_path = input_data["transcript_path"]

        # Initialize session manager
        # Use workspace root from environment if set (for testing)
        workspace_root = os.environ.get("CLAUDE_WORKSPACE_ROOT")
        if workspace_root:
            manager = SessionManager(Path(workspace_root))
            git_info = GitInfo(Path(workspace_root))
        else:
            manager = SessionManager()
            git_info = GitInfo()

        # Get working directory
        working_dir = str(Path.cwd())

        # Add active session
        manager.add_active_session(
            session_id=session_id,
            source=source,
            mode=permission_mode,
            transcript_path=transcript_path,
            git_info=git_info,
            working_dir=working_dir
        )

        # Load updated data for output
        data = manager.load()

        # Find the session we just added
        session = None
        for s in data["activeSessions"]:
            if s["sessionId"] == session_id:
                session = s
                break

        # Output success response
        hook_output = {
            "session": session,
            "activeSessionsCount": len(data["activeSessions"])
        }

        output_response(
            success=True,
            message=f"Session created successfully: {session_id}",
            hook_output=hook_output
        )

    except ValueError as e:
        # Validation or parsing error
        output_response(success=False, message=str(e))
        sys.exit(1)

    except Exception as e:
        # Unexpected error
        output_response(success=False, message=f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
