"""Tests for session_start hook"""
import pytest
import json
import subprocess
from pathlib import Path


class TestSessionStartHook:
    """Tests for session_start.py hook executable"""

    @pytest.fixture
    def hook_path(self):
        """Get path to session_start.py hook"""
        return Path(__file__).parent.parent.parent / "hooks" / "session_start.py"

    def test_valid_input_creates_session(self, hook_path, tmp_workspace, sessions_file_empty):
        """Should create session entry with valid input"""
        input_data = {
            "session_id": "sess-1234567890",
            "source": "startup",
            "permission_mode": "default",
            "transcript_path": "/path/to/transcript.jsonl"
        }

        # Run hook as subprocess
        result = subprocess.run(
            ["python3", str(hook_path)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            cwd=tmp_workspace
        )

        # Parse output
        assert result.returncode == 0
        output = json.loads(result.stdout)

        # Assertions
        assert output["success"] is True
        assert "Session created successfully" in output["message"]
        assert "hookSpecificOutput" in output
        assert output["hookSpecificOutput"]["session"]["sessionId"] == "sess-1234567890"

    def test_invalid_json_input(self, hook_path, tmp_workspace):
        """Should output error for invalid JSON"""
        result = subprocess.run(
            ["python3", str(hook_path)],
            input="not valid json",
            capture_output=True,
            text=True,
            cwd=tmp_workspace
        )

        # Parse output
        output = json.loads(result.stdout)

        assert output["success"] is False
        assert "Failed to parse input JSON" in output["message"]

    def test_missing_required_fields(self, hook_path, tmp_workspace):
        """Should output error for missing required fields"""
        input_data = {
            "session_id": "sess-test",
            # Missing: source, transcript_path
        }

        result = subprocess.run(
            ["python3", str(hook_path)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            cwd=tmp_workspace
        )

        output = json.loads(result.stdout)

        assert output["success"] is False
        assert "Missing required field" in output["message"]

    def test_permission_mode_is_optional(self, hook_path, tmp_workspace, sessions_file_empty):
        """Should use default permission_mode when not provided"""
        input_data = {
            "session_id": "sess-no-mode",
            "source": "startup",
            # permission_mode is omitted
            "transcript_path": "/test.jsonl"
        }

        result = subprocess.run(
            ["python3", str(hook_path)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            cwd=tmp_workspace
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)

        # Should succeed
        assert output["success"] is True
        assert "Session created successfully" in output["message"]

        # Verify session was created with default mode
        session = output["hookSpecificOutput"]["session"]
        assert session["sessionId"] == "sess-no-mode"
        assert session["environment"]["permissionMode"] == "default"  # Should default to "default"

    def test_git_info_integration(self, hook_path, mock_git_repo, sessions_file_empty):
        """Should capture git branch and commit info"""
        input_data = {
            "session_id": "sess-git-test",
            "source": "startup",
            "permission_mode": "default",
            "transcript_path": "/test.jsonl"
        }

        result = subprocess.run(
            ["python3", str(hook_path)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            cwd=mock_git_repo
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)

        assert output["success"] is True

        # Verify git info was captured
        session = output["hookSpecificOutput"]["session"]
        env = session["environment"]
        assert env["gitBranch"] == "main"
        assert env["gitCommitHash"] is not None
        assert len(env["gitCommitHash"]) == 40  # Full SHA

    def test_valid_source_values(self, hook_path, tmp_workspace, sessions_file_empty):
        """Should accept valid source values"""
        valid_sources = ["startup", "resume", "clear"]

        for source in valid_sources:
            input_data = {
                "session_id": f"sess-{source}",
                "source": source,
                "permission_mode": "default",
                "transcript_path": "/test.jsonl"
            }

            result = subprocess.run(
                ["python3", str(hook_path)],
                input=json.dumps(input_data),
                capture_output=True,
                text=True,
                cwd=tmp_workspace
            )

            output = json.loads(result.stdout)
            assert output["success"] is True, f"Failed for source: {source}"

    def test_valid_permission_modes(self, hook_path, tmp_workspace, sessions_file_empty):
        """Should accept valid permission modes"""
        valid_modes = ["default", "plan", "accept-edits", "bypass-permissions"]

        for mode in valid_modes:
            input_data = {
                "session_id": f"sess-{mode}",
                "source": "startup",
                "permission_mode": mode,
                "transcript_path": "/test.jsonl"
            }

            result = subprocess.run(
                ["python3", str(hook_path)],
                input=json.dumps(input_data),
                capture_output=True,
                text=True,
                cwd=tmp_workspace
            )

            output = json.loads(result.stdout)
            assert output["success"] is True, f"Failed for mode: {mode}"

    def test_output_format(self, hook_path, tmp_workspace, sessions_file_empty):
        """Should output JSON with required fields"""
        input_data = {
            "session_id": "sess-format-test",
            "source": "startup",
            "permission_mode": "default",
            "transcript_path": "/test.jsonl"
        }

        result = subprocess.run(
            ["python3", str(hook_path)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            cwd=tmp_workspace
        )

        # Should be valid JSON
        output = json.loads(result.stdout)

        # Required fields
        assert "success" in output
        assert "message" in output
        assert isinstance(output["success"], bool)
        assert isinstance(output["message"], str)

    def test_creates_sessions_file_if_missing(self, hook_path, tmp_workspace):
        """Should create sessions_summary.json if it doesn't exist"""
        # Remove sessions file if it exists
        sessions_file = tmp_workspace / "status" / "sessions_summary.json"
        if sessions_file.exists():
            sessions_file.unlink()

        input_data = {
            "session_id": "sess-new",
            "source": "startup",
            "permission_mode": "default",
            "transcript_path": "/test.jsonl"
        }

        result = subprocess.run(
            ["python3", str(hook_path)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            cwd=tmp_workspace
        )

        output = json.loads(result.stdout)
        assert output["success"] is True

        # File should now exist
        assert sessions_file.exists()

        # Should be valid JSON
        data = json.loads(sessions_file.read_text())
        assert len(data["activeSessions"]) == 1
        assert data["activeSessions"][0]["sessionId"] == "sess-new"
