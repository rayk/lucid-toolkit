"""
Integration test for SessionEnd transcript parsing integration.

Tests the full lifecycle of SessionEnd hook with real transcript parsing:
- SessionStart creates session
- Transcript file is created with real tool usage data
- SessionEnd parses transcript and populates statistics
- Verify statistics are correctly extracted and stored in history
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict
import os

import pytest


@pytest.fixture
def hook_scripts_dir():
    """Get the hook scripts directory."""
    return Path(__file__).parent.parent.parent.parent


@pytest.fixture
def session_start_hook(hook_scripts_dir):
    """Path to session start hook."""
    return hook_scripts_dir / "session_summary" / "hooks" / "session_start.py"


@pytest.fixture
def session_end_hook(hook_scripts_dir):
    """Path to session end hook."""
    return hook_scripts_dir / "session_summary" / "hooks" / "session_end.py"


def run_hook(hook_path: Path, payload: Dict[str, Any], env: Dict[str, str]) -> subprocess.CompletedProcess:
    """Run a hook script with given payload and environment."""
    result = subprocess.run(
        [sys.executable, str(hook_path)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
    )
    return result


class TestSessionEndTranscriptIntegration:
    """Integration tests for SessionEnd transcript parsing."""

    def test_session_end_extracts_and_stores_transcript_stats(
        self, tmp_path, mock_git_repo, session_start_hook, session_end_hook
    ):
        """Test full lifecycle: SessionStart -> transcript creation -> SessionEnd -> verify stats."""
        # Setup test environment
        status_dir = tmp_path / "status"
        status_dir.mkdir()

        env = os.environ.copy()
        env["CLAUDE_WORKSPACE_ROOT"] = str(tmp_path)

        # Initialize git repo in tmp_path for GitInfo
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "--allow-empty", "-m", "Initial commit"], cwd=tmp_path, capture_output=True)

        # Step 1: Start session
        transcript_path = tmp_path / "session_transcript.jsonl"

        start_payload = {
            "session_id": "sess-integration",
            "source": "startup",
            "permission_mode": "default",
            "transcript_path": str(transcript_path),
            "working_dir": str(tmp_path),
            "hook_event_name": "SessionStart"
        }

        start_result = run_hook(session_start_hook, start_payload, env)
        assert start_result.returncode == 0, f"SessionStart failed: {start_result.stderr}"

        # Step 2: Create realistic transcript with tool usage
        transcript_content = [
            # Message with token usage and tool calls
            {
                "type": "message",
                "role": "assistant",
                "timestamp": "2025-01-20T10:00:00Z",
                "usage": {"input_tokens": 1500, "output_tokens": 800},
                "content": [
                    {
                        "type": "tool_use",
                        "id": "tool1",
                        "name": "Read",
                        "input": {"file_path": "/test/app.py"}
                    },
                    {
                        "type": "tool_use",
                        "id": "tool2",
                        "name": "Write",
                        "input": {
                            "file_path": "/test/config.json",
                            "content": '{"key": "value"}'
                        }
                    }
                ]
            },
            # Another message with more activity
            {
                "type": "message",
                "role": "assistant",
                "timestamp": "2025-01-20T10:05:00Z",
                "usage": {"input_tokens": 2000, "output_tokens": 1200},
                "content": [
                    {
                        "type": "tool_use",
                        "id": "tool3",
                        "name": "Edit",
                        "input": {
                            "file_path": "/test/utils.py",
                            "old_string": "def old()",
                            "new_string": "def new()"
                        }
                    },
                    {
                        "type": "tool_use",
                        "id": "tool4",
                        "name": "Bash",
                        "input": {"command": "pytest tests/"}
                    },
                    {
                        "type": "tool_use",
                        "id": "tool5",
                        "name": "TodoWrite",
                        "input": {
                            "todos": [
                                {"content": "Task 1", "status": "completed", "activeForm": "Task 1"},
                                {"content": "Task 2", "status": "completed", "activeForm": "Task 2"},
                                {"content": "Task 3", "status": "completed", "activeForm": "Task 3"},
                            ]
                        }
                    },
                    {
                        "type": "tool_use",
                        "id": "tool6",
                        "name": "Task",
                        "input": {"prompt": "Research API design"}
                    }
                ]
            }
        ]

        # Write transcript as JSONL
        with open(transcript_path, "w") as f:
            for obj in transcript_content:
                f.write(json.dumps(obj) + "\n")

        # Step 3: End session
        end_payload = {
            "session_id": "sess-integration",
            "reason": "logout",
            "hook_event_name": "SessionEnd"
        }

        end_result = run_hook(session_end_hook, end_payload, env)
        assert end_result.returncode == 0, f"SessionEnd failed: {end_result.stderr}"

        # Step 4: Verify statistics were extracted and stored
        sessions_file = status_dir / "sessions_summary.json"
        assert sessions_file.exists(), "sessions_summary.json should exist"

        with open(sessions_file) as f:
            sessions = json.load(f)

        # Session should be in history, not active
        assert len(sessions["activeSessions"]) == 0, "Should have no active sessions"
        assert len(sessions["recentHistory"]) == 1, "Should have one history entry"

        history = sessions["recentHistory"][0]
        assert history["sessionId"] == "sess-integration"

        # Verify transcript statistics were extracted
        # Expected tokens: 1500 + 800 + 2000 + 1200 = 5500
        assert history["tokensConsumed"] == 5500, \
            f"Expected 5500 tokens, got {history['tokensConsumed']}"

        # Expected files modified: config.json (Write) + utils.py (Edit) = 2
        assert history["filesModifiedCount"] == 2, \
            f"Expected 2 files modified, got {history['filesModifiedCount']}"

        # Verify tool usage summary
        assert "toolUsageSummary" in history
        tool_usage = history["toolUsageSummary"]
        assert tool_usage.get("Read") == 1, "Should have 1 Read call"
        assert tool_usage.get("Write") == 1, "Should have 1 Write call"
        assert tool_usage.get("Edit") == 1, "Should have 1 Edit call"
        assert tool_usage.get("Bash") == 1, "Should have 1 Bash call"
        assert tool_usage.get("TodoWrite") == 1, "Should have 1 TodoWrite call"
        assert tool_usage.get("Task") == 1, "Should have 1 Task call"

        # Verify subagent launches (Task tool)
        assert history["subagentsLaunched"] == 1, \
            f"Expected 1 subagent launch, got {history['subagentsLaunched']}"

    def test_session_end_with_malformed_transcript_degrades_gracefully(
        self, tmp_path, mock_git_repo, session_start_hook, session_end_hook
    ):
        """Test SessionEnd handles malformed transcript gracefully."""
        status_dir = tmp_path / "status"
        status_dir.mkdir()

        env = os.environ.copy()
        env["CLAUDE_WORKSPACE_ROOT"] = str(tmp_path)

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "commit", "--allow-empty", "-m", "Initial"], cwd=tmp_path, capture_output=True)

        # Start session
        transcript_path = tmp_path / "malformed_transcript.jsonl"

        start_payload = {
            "session_id": "sess-malformed",
            "source": "startup",
            "permission_mode": "default",
            "transcript_path": str(transcript_path),
            "working_dir": str(tmp_path),
            "hook_event_name": "SessionStart"
        }

        start_result = run_hook(session_start_hook, start_payload, env)
        assert start_result.returncode == 0

        # Create transcript with mix of valid and malformed JSON
        with open(transcript_path, "w") as f:
            # Valid line
            f.write(json.dumps({
                "type": "message",
                "timestamp": "2025-01-20T10:00:00Z",
                "usage": {"input_tokens": 100, "output_tokens": 50}
            }) + "\n")
            # Malformed line (should be skipped)
            f.write("{invalid json here}\n")
            # Another valid line
            f.write(json.dumps({
                "type": "message",
                "timestamp": "2025-01-20T10:01:00Z",
                "usage": {"input_tokens": 200, "output_tokens": 100}
            }) + "\n")

        # End session
        end_payload = {
            "session_id": "sess-malformed",
            "reason": "logout",
            "hook_event_name": "SessionEnd"
        }

        end_result = run_hook(session_end_hook, end_payload, env)
        assert end_result.returncode == 0, f"SessionEnd should succeed: {end_result.stderr}"

        # Verify session moved to history with partial stats
        sessions_file = status_dir / "sessions_summary.json"
        with open(sessions_file) as f:
            sessions = json.load(f)

        assert len(sessions["recentHistory"]) == 1
        history = sessions["recentHistory"][0]

        # Should have tokens from valid lines only: 100 + 50 + 200 + 100 = 450
        assert history["tokensConsumed"] == 450, \
            f"Expected 450 tokens (malformed line skipped), got {history['tokensConsumed']}"
