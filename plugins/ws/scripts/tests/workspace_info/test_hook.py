"""
Tests for workspace_info.hook module.
"""
import json
import os
import sys
from pathlib import Path
from io import StringIO

import pytest

from workspace_info.hook import HookContext, run_hook, _read_stdin, _write_response


def test_hook_context_from_stdin_with_full_json(mock_stdin, hook_stdin_post_tool_use, mock_env):
    """Test HookContext parsing with complete hook input JSON."""
    mock_env(CLAUDE_PROJECT_DIR="/workspace/root")

    with mock_stdin(hook_stdin_post_tool_use):
        ctx = HookContext.from_stdin()

    assert ctx.session_id == "sess-abc123def456"
    assert ctx.transcript_path == Path("/tmp/claude/transcripts/sess-abc123def456.json")
    assert ctx.cwd == Path("/Users/dev/my-workspace")
    assert ctx.hook_event == "PostToolUse"
    assert ctx.tool_name == "Edit"
    assert ctx.tool_input["file_path"] == "/Users/dev/my-workspace/outcomes/in-progress/005-my-outcome/outcome_track.json"
    assert ctx.project_dir == Path("/workspace/root")
    assert ctx.log is not None


def test_hook_context_from_stdin_with_empty_input(mock_stdin, mock_env):
    """Test HookContext handles empty stdin gracefully."""
    mock_env(CLAUDE_PROJECT_DIR=None)

    with mock_stdin({}):
        ctx = HookContext.from_stdin()

    assert ctx.session_id is None
    assert ctx.transcript_path is None
    assert ctx.hook_event is None
    assert ctx.tool_name is None
    assert ctx.tool_input == {}
    assert ctx.project_dir == Path.cwd()


def test_hook_context_from_stdin_with_malformed_json(mock_env, monkeypatch):
    """Test HookContext handles malformed JSON gracefully."""
    mock_env(CLAUDE_PROJECT_DIR="/workspace")

    # Mock stdin with invalid JSON
    monkeypatch.setattr(sys, 'stdin', StringIO("not valid json {"))

    ctx = HookContext.from_stdin()

    # Should still create valid context with defaults
    assert ctx.session_id is None
    assert ctx.project_dir == Path("/workspace")


def test_hook_context_uses_claude_project_dir_env(mock_stdin, mock_env):
    """Test HookContext prioritizes CLAUDE_PROJECT_DIR environment variable."""
    mock_env(
        CLAUDE_PROJECT_DIR="/priority/path",
        CLAUDE_WORKSPACE_ROOT="/fallback/path"
    )

    with mock_stdin({"cwd": "/stdin/path"}):
        ctx = HookContext.from_stdin()

    assert ctx.project_dir == Path("/priority/path")


def test_hook_context_falls_back_to_cwd(mock_stdin, mock_env):
    """Test HookContext falls back to cwd when no environment variables set."""
    mock_env(CLAUDE_PROJECT_DIR=None, CLAUDE_WORKSPACE_ROOT=None)

    with mock_stdin({"cwd": "/stdin/cwd"}):
        ctx = HookContext.from_stdin()

    assert ctx.project_dir == Path("/stdin/cwd")


def test_success_returns_zero(mock_stdin, capture_stdout):
    """Test success() returns exit code 0 and outputs correct JSON."""
    with mock_stdin({}):
        ctx = HookContext.from_stdin()

    with capture_stdout as cap:
        exit_code = ctx.success()

    assert exit_code == 0
    response = json.loads(cap.captured)
    assert response["continue"] is True
    assert "additionalContext" not in response


def test_success_with_context_adds_additional_context(mock_stdin, capture_stdout):
    """Test success() with context adds additionalContext to response."""
    with mock_stdin({}):
        ctx = HookContext.from_stdin()

    with capture_stdout as cap:
        exit_code = ctx.success(context="Workspace initialized")

    assert exit_code == 0
    response = json.loads(cap.captured)
    assert response["continue"] is True
    assert response["additionalContext"] == "Workspace initialized"


def test_block_returns_two(mock_stdin, capture_stdout):
    """Test block() returns exit code 2 and outputs blocking response."""
    with mock_stdin({}):
        ctx = HookContext.from_stdin()

    with capture_stdout as cap:
        exit_code = ctx.block("Cannot proceed")

    assert exit_code == 2
    response = json.loads(cap.captured)
    assert response["continue"] is False
    assert response["stopReason"] == "Cannot proceed"


def test_warn_returns_one(mock_stdin, capture_stdout):
    """Test warn() returns exit code 1 and outputs warning response."""
    with mock_stdin({}):
        ctx = HookContext.from_stdin()

    with capture_stdout as cap:
        exit_code = ctx.warn("Minor issue detected")

    assert exit_code == 1
    response = json.loads(cap.captured)
    assert response["continue"] is True
    assert response["systemMessage"] == "Minor issue detected"


def test_run_hook_decorator_catches_exceptions(mock_stdin, capture_stdout, tmp_workspace, monkeypatch):
    """Test run_hook decorator catches exceptions and returns success."""
    # Create a hook function that raises an exception
    @run_hook
    def failing_hook(ws, ctx):
        raise ValueError("Intentional test error")

    with mock_stdin({"cwd": str(tmp_workspace)}):
        with capture_stdout as cap:
            with pytest.raises(SystemExit) as exc_info:
                failing_hook()

    # Should exit with 0 (success) despite exception
    assert exc_info.value.code == 0

    # Should still output success response
    response = json.loads(cap.captured)
    assert response["continue"] is True


def test_run_hook_decorator_returns_exit_code_from_function(mock_stdin, capture_stdout, tmp_workspace):
    """Test run_hook decorator uses exit code returned by function."""
    @run_hook
    def warning_hook(ws, ctx):
        return ctx.warn("Test warning")

    with mock_stdin({"cwd": str(tmp_workspace)}):
        with capture_stdout as cap:
            with pytest.raises(SystemExit) as exc_info:
                warning_hook()

    # Should use the exit code returned by the function
    assert exc_info.value.code == 1


def test_run_hook_decorator_defaults_to_success(mock_stdin, capture_stdout, tmp_workspace):
    """Test run_hook decorator defaults to success when function returns None."""
    @run_hook
    def simple_hook(ws, ctx):
        # Do nothing, return None implicitly
        pass

    with mock_stdin({"cwd": str(tmp_workspace)}):
        with capture_stdout as cap:
            with pytest.raises(SystemExit) as exc_info:
                simple_hook()

    # Should exit with 0 when function returns None
    assert exc_info.value.code == 0
    response = json.loads(cap.captured)
    assert response["continue"] is True
