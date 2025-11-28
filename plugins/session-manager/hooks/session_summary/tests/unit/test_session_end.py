"""Tests for session_end hook script"""
import pytest
import json
import sys
from pathlib import Path
from io import StringIO
from datetime import datetime, timezone

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from session_summary.lib.session_manager import SessionManager
from lucid_cli_commons.git_utils import GitInfo


class TestSessionEnd:
    """Tests for session_end.py hook script"""

    def test_valid_input_moves_to_history(self, tmp_workspace, sessions_file_empty, mock_git_repo):
        """Should successfully end session and move to history"""
        # Set environment variable early for paths initialization
        import os
        env_backup = os.environ.get("CLAUDE_WORKSPACE_ROOT")
        os.environ["CLAUDE_WORKSPACE_ROOT"] = str(tmp_workspace)

        try:
            # Setup: Create active session first
            manager = SessionManager(tmp_workspace)
            git_info = GitInfo(mock_git_repo)

            manager.add_active_session(
                session_id="sess-test123",
                source="startup",
                mode="default",
                transcript_path="/test/transcript.md",
                git_info=git_info,
                working_dir=str(mock_git_repo)
            )

            # Verify session is active
            data = manager.load()
            assert len(data["activeSessions"]) == 1
            assert data["activeSessions"][0]["sessionId"] == "sess-test123"

            # Import session_end module
            from session_summary.hooks import session_end

            # Prepare input
            input_data = {
                "session_id": "sess-test123",
                "end_reason": "logout",
                "accomplishments": ["Completed task A", "Fixed bug B"],
                "outcomes_worked": [1, 2]
            }

            # Mock stdin
            stdin_backup = sys.stdin
            sys.stdin = StringIO(json.dumps(input_data))

            # Mock stdout to capture output
            stdout_backup = sys.stdout
            sys.stdout = StringIO()

            try:
                # Run session_end.main()
                session_end.main()

                # Get output
                output = sys.stdout.getvalue()

            finally:
                # Restore stdin/stdout
                sys.stdin = stdin_backup
                sys.stdout = stdout_backup

            # Parse output
            result = json.loads(output)

            # Verify output structure
            assert result["success"] is True
            assert "message" in result
            assert "Session ended successfully" in result["message"]

            # Verify session moved to history
            # Need to create fresh manager to reload from disk
            manager2 = SessionManager(tmp_workspace)
            data = manager2.load()
            assert len(data["activeSessions"]) == 0
            assert len(data["recentHistory"]) == 1

            history = data["recentHistory"][0]
            assert history["sessionId"] == "sess-test123"
            assert history["sessionEndReason"] == "logout"
            assert history["accomplishments"] == "Completed task A; Fixed bug B"
            assert history["durationMinutes"] >= 0  # Can be 0 for very fast tests
            assert "completedAt" in history

        finally:
            # Restore environment
            if env_backup is None:
                os.environ.pop("CLAUDE_WORKSPACE_ROOT", None)
            else:
                os.environ["CLAUDE_WORKSPACE_ROOT"] = env_backup

    def test_invalid_json_input(self, tmp_workspace):
        """Should output error for invalid JSON"""
        from session_summary.hooks import session_end

        # Prepare invalid JSON
        invalid_json = "{invalid json"

        # Mock stdin/stdout
        stdin_backup = sys.stdin
        stdout_backup = sys.stdout
        sys.stdin = StringIO(invalid_json)
        sys.stdout = StringIO()

        import os
        env_backup = os.environ.get("CLAUDE_WORKSPACE_ROOT")
        os.environ["CLAUDE_WORKSPACE_ROOT"] = str(tmp_workspace)

        try:
            session_end.main()
            output = sys.stdout.getvalue()
        finally:
            sys.stdin = stdin_backup
            sys.stdout = stdout_backup
            if env_backup is None:
                os.environ.pop("CLAUDE_WORKSPACE_ROOT", None)
            else:
                os.environ["CLAUDE_WORKSPACE_ROOT"] = env_backup

        result = json.loads(output)
        assert result["success"] is False
        assert "Invalid JSON" in result["message"]

    def test_missing_required_fields(self, tmp_workspace):
        """Should output error for missing required fields"""
        from session_summary.hooks import session_end

        # Missing end_reason
        input_data = {"session_id": "sess-123"}

        stdin_backup = sys.stdin
        stdout_backup = sys.stdout
        sys.stdin = StringIO(json.dumps(input_data))
        sys.stdout = StringIO()

        import os
        env_backup = os.environ.get("CLAUDE_WORKSPACE_ROOT")
        os.environ["CLAUDE_WORKSPACE_ROOT"] = str(tmp_workspace)

        try:
            session_end.main()
            output = sys.stdout.getvalue()
        finally:
            sys.stdin = stdin_backup
            sys.stdout = stdout_backup
            if env_backup is None:
                os.environ.pop("CLAUDE_WORKSPACE_ROOT", None)
            else:
                os.environ["CLAUDE_WORKSPACE_ROOT"] = env_backup

        result = json.loads(output)
        assert result["success"] is False
        assert "Missing required field" in result["message"]

    def test_session_not_found(self, tmp_workspace, sessions_file_empty):
        """Should handle session not found gracefully"""
        from session_summary.hooks import session_end

        input_data = {
            "session_id": "sess-nonexistent",
            "end_reason": "logout"
        }

        stdin_backup = sys.stdin
        stdout_backup = sys.stdout
        sys.stdin = StringIO(json.dumps(input_data))
        sys.stdout = StringIO()

        import os
        env_backup = os.environ.get("CLAUDE_WORKSPACE_ROOT")
        os.environ["CLAUDE_WORKSPACE_ROOT"] = str(tmp_workspace)

        try:
            session_end.main()
            output = sys.stdout.getvalue()
        finally:
            sys.stdin = stdin_backup
            sys.stdout = stdout_backup
            if env_backup is None:
                os.environ.pop("CLAUDE_WORKSPACE_ROOT", None)
            else:
                os.environ["CLAUDE_WORKSPACE_ROOT"] = env_backup

        result = json.loads(output)
        assert result["success"] is False
        assert "Session not found" in result["message"]

    def test_empty_accomplishments(self, tmp_workspace, sessions_file_empty, mock_git_repo):
        """Should handle empty accomplishments list"""
        # Set environment variable early
        import os
        env_backup = os.environ.get("CLAUDE_WORKSPACE_ROOT")
        os.environ["CLAUDE_WORKSPACE_ROOT"] = str(tmp_workspace)

        try:
            # Setup active session
            manager = SessionManager(tmp_workspace)
            git_info = GitInfo(mock_git_repo)

            manager.add_active_session(
                session_id="sess-empty",
                source="startup",
                mode="default",
                transcript_path="/test/transcript.md",
                git_info=git_info,
                working_dir=str(mock_git_repo)
            )

            from session_summary.hooks import session_end

            input_data = {
                "session_id": "sess-empty",
                "end_reason": "clear",
                "accomplishments": []
            }

            stdin_backup = sys.stdin
            stdout_backup = sys.stdout
            sys.stdin = StringIO(json.dumps(input_data))
            sys.stdout = StringIO()

            try:
                session_end.main()
                output = sys.stdout.getvalue()
            finally:
                sys.stdin = stdin_backup
                sys.stdout = stdout_backup

            result = json.loads(output)
            assert result["success"] is True

            # Verify empty accomplishments
            manager2 = SessionManager(tmp_workspace)
            data = manager2.load()
            history = data["recentHistory"][0]
            assert history["accomplishments"] == ""

        finally:
            # Restore environment
            if env_backup is None:
                os.environ.pop("CLAUDE_WORKSPACE_ROOT", None)
            else:
                os.environ["CLAUDE_WORKSPACE_ROOT"] = env_backup

    def test_missing_session_id(self, tmp_workspace):
        """Should output error for missing session_id"""
        from session_summary.hooks import session_end

        # Missing session_id
        input_data = {"end_reason": "logout"}

        stdin_backup = sys.stdin
        stdout_backup = sys.stdout
        sys.stdin = StringIO(json.dumps(input_data))
        sys.stdout = StringIO()

        import os
        env_backup = os.environ.get("CLAUDE_WORKSPACE_ROOT")
        os.environ["CLAUDE_WORKSPACE_ROOT"] = str(tmp_workspace)

        try:
            session_end.main()
            output = sys.stdout.getvalue()
        finally:
            sys.stdin = stdin_backup
            sys.stdout = stdout_backup
            if env_backup is None:
                os.environ.pop("CLAUDE_WORKSPACE_ROOT", None)
            else:
                os.environ["CLAUDE_WORKSPACE_ROOT"] = env_backup

        result = json.loads(output)
        assert result["success"] is False
        assert "session_id" in result["message"]

    def test_session_end_extracts_transcript_statistics(self, tmp_workspace, sessions_file_empty, mock_git_repo):
        """Should extract statistics from transcript using TranscriptParser (TDD RED phase)"""
        import os
        env_backup = os.environ.get("CLAUDE_WORKSPACE_ROOT")
        os.environ["CLAUDE_WORKSPACE_ROOT"] = str(tmp_workspace)

        try:
            # Create a mock transcript file with known data
            transcript_path = tmp_workspace / "transcript.jsonl"
            transcript_content = [
                # Message with token usage
                {
                    "type": "message",
                    "role": "assistant",
                    "timestamp": "2025-01-20T10:00:00Z",
                    "usage": {"input_tokens": 1000, "output_tokens": 500},
                    "content": [
                        {
                            "type": "tool_use",
                            "name": "Read",
                            "input": {"file_path": "/test/file1.py"}
                        },
                        {
                            "type": "tool_use",
                            "name": "Write",
                            "input": {"file_path": "/test/file2.py", "content": "test"}
                        }
                    ]
                },
                # Another message with more tool usage
                {
                    "type": "message",
                    "role": "assistant",
                    "timestamp": "2025-01-20T10:05:00Z",
                    "usage": {"input_tokens": 800, "output_tokens": 300},
                    "content": [
                        {
                            "type": "tool_use",
                            "name": "Edit",
                            "input": {"file_path": "/test/file3.py", "old_string": "a", "new_string": "b"}
                        },
                        {
                            "type": "tool_use",
                            "name": "Bash",
                            "input": {"command": "echo test"}
                        },
                        {
                            "type": "tool_use",
                            "name": "TodoWrite",
                            "input": {
                                "todos": [
                                    {"content": "Task 1", "status": "completed", "activeForm": "Doing task 1"},
                                    {"content": "Task 2", "status": "completed", "activeForm": "Doing task 2"},
                                    {"content": "Task 3", "status": "in_progress", "activeForm": "Doing task 3"}
                                ]
                            }
                        }
                    ]
                }
            ]

            # Write transcript as JSONL
            with open(transcript_path, "w") as f:
                for obj in transcript_content:
                    f.write(json.dumps(obj) + "\n")

            # Setup: Create active session with transcript path
            manager = SessionManager(tmp_workspace)
            git_info = GitInfo(mock_git_repo)

            manager.add_active_session(
                session_id="sess-statstest",
                source="startup",
                mode="default",
                transcript_path=str(transcript_path),
                git_info=git_info,
                working_dir=str(mock_git_repo)
            )

            # Prepare input for session_end (Claude Code's actual format uses "reason", not "end_reason")
            input_data = {
                "session_id": "sess-statstest",
                "reason": "logout"
            }

            from session_summary.hooks import session_end

            stdin_backup = sys.stdin
            stdout_backup = sys.stdout
            sys.stdin = StringIO(json.dumps(input_data))
            sys.stdout = StringIO()

            try:
                session_end.main()
                output = sys.stdout.getvalue()
            finally:
                sys.stdin = stdin_backup
                sys.stdout = stdout_backup

            result = json.loads(output)

            # Verify session moved to history
            manager2 = SessionManager(tmp_workspace)
            data = manager2.load()
            assert len(data["recentHistory"]) == 1

            history = data["recentHistory"][0]

            # Assert statistics were populated from transcript
            # Expected: 1000 + 500 + 800 + 300 = 2600 tokens
            assert history["tokensConsumed"] == 2600, f"Expected 2600 tokens, got {history['tokensConsumed']}"

            # Expected: 3 files modified (file2.py from Write, file3.py from Edit)
            # Note: Read doesn't count as modified
            assert history["filesModifiedCount"] == 2, f"Expected 2 files modified, got {history['filesModifiedCount']}"

            # Expected tool usage summary
            assert "toolUsageSummary" in history
            tool_usage = history["toolUsageSummary"]
            assert tool_usage.get("Read") == 1
            assert tool_usage.get("Write") == 1
            assert tool_usage.get("Edit") == 1
            assert tool_usage.get("Bash") == 1
            assert tool_usage.get("TodoWrite") == 1

            # Expected: 2 tasks completed (from TodoWrite)
            # This would need to be tracked in session statistics
            # For now, we're focusing on the main statistics

        finally:
            if env_backup is None:
                os.environ.pop("CLAUDE_WORKSPACE_ROOT", None)
            else:
                os.environ["CLAUDE_WORKSPACE_ROOT"] = env_backup

    def test_session_end_handles_missing_transcript(self, tmp_workspace, sessions_file_empty, mock_git_repo):
        """Should handle missing transcript gracefully without crashing (TDD REFACTOR phase)"""
        import os
        env_backup = os.environ.get("CLAUDE_WORKSPACE_ROOT")
        os.environ["CLAUDE_WORKSPACE_ROOT"] = str(tmp_workspace)

        try:
            # Create session with transcript path that doesn't exist
            nonexistent_transcript = tmp_workspace / "nonexistent_transcript.jsonl"

            manager = SessionManager(tmp_workspace)
            git_info = GitInfo(mock_git_repo)

            manager.add_active_session(
                session_id="sess-nofile",
                source="startup",
                mode="default",
                transcript_path=str(nonexistent_transcript),  # File doesn't exist
                git_info=git_info,
                working_dir=str(mock_git_repo)
            )

            from session_summary.hooks import session_end

            input_data = {
                "session_id": "sess-nofile",
                "reason": "logout"
            }

            stdin_backup = sys.stdin
            stdout_backup = sys.stdout
            sys.stdin = StringIO(json.dumps(input_data))
            sys.stdout = StringIO()

            try:
                session_end.main()
                output = sys.stdout.getvalue()
            finally:
                sys.stdin = stdin_backup
                sys.stdout = stdout_backup

            result = json.loads(output)

            # Verify session still moved to history (graceful degradation)
            manager2 = SessionManager(tmp_workspace)
            data = manager2.load()
            assert len(data["recentHistory"]) == 1

            history = data["recentHistory"][0]

            # Statistics should be 0 when transcript is missing
            assert history["tokensConsumed"] == 0
            assert history["filesModifiedCount"] == 0
            assert history["toolUsageSummary"] == {}

        finally:
            if env_backup is None:
                os.environ.pop("CLAUDE_WORKSPACE_ROOT", None)
            else:
                os.environ["CLAUDE_WORKSPACE_ROOT"] = env_backup

    def test_session_end_handles_empty_transcript(self, tmp_workspace, sessions_file_empty, mock_git_repo):
        """Should handle empty transcript gracefully (TDD REFACTOR phase)"""
        import os
        env_backup = os.environ.get("CLAUDE_WORKSPACE_ROOT")
        os.environ["CLAUDE_WORKSPACE_ROOT"] = str(tmp_workspace)

        try:
            # Create empty transcript file
            transcript_path = tmp_workspace / "empty_transcript.jsonl"
            transcript_path.touch()  # Create empty file

            manager = SessionManager(tmp_workspace)
            git_info = GitInfo(mock_git_repo)

            manager.add_active_session(
                session_id="sess-empty",
                source="startup",
                mode="default",
                transcript_path=str(transcript_path),
                git_info=git_info,
                working_dir=str(mock_git_repo)
            )

            from session_summary.hooks import session_end

            input_data = {
                "session_id": "sess-empty",
                "reason": "logout"
            }

            stdin_backup = sys.stdin
            stdout_backup = sys.stdout
            sys.stdin = StringIO(json.dumps(input_data))
            sys.stdout = StringIO()

            try:
                session_end.main()
                output = sys.stdout.getvalue()
            finally:
                sys.stdin = stdin_backup
                sys.stdout = stdout_backup

            result = json.loads(output)

            # Verify session moved to history
            manager2 = SessionManager(tmp_workspace)
            data = manager2.load()
            assert len(data["recentHistory"]) == 1

            history = data["recentHistory"][0]

            # Statistics should be 0 for empty transcript
            assert history["tokensConsumed"] == 0
            assert history["filesModifiedCount"] == 0
            assert history["toolUsageSummary"] == {}

        finally:
            if env_backup is None:
                os.environ.pop("CLAUDE_WORKSPACE_ROOT", None)
            else:
                os.environ["CLAUDE_WORKSPACE_ROOT"] = env_backup
