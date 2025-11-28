"""
Integration tests for concurrent session handling.

Tests file locking, atomic operations, and race condition prevention
when multiple processes access session data simultaneously.
"""

import json
import multiprocessing
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict

import pytest


def find_active_session(sessions, session_id):
    """Find active session by ID."""
    matches = [s for s in sessions["activeSessions"] if s["sessionId"] == session_id]
    if not matches:
        raise ValueError(f"Session {session_id} not found in activeSessions")
    if len(matches) > 1:
        raise ValueError(f"Multiple sessions found with ID {session_id}")
    return matches[0]


def find_history_session(sessions, session_id):
    """Find history session by ID."""
    matches = [s for s in sessions["recentHistory"] if s["sessionId"] == session_id]
    if not matches:
        raise ValueError(f"Session {session_id} not found in recentHistory")
    if len(matches) > 1:
        raise ValueError(f"Multiple sessions found with ID {session_id}")
    return matches[0]


def session_exists_active(sessions, session_id):
    """Check if session exists in activeSessions."""
    return any(s["sessionId"] == session_id for s in sessions["activeSessions"])


def session_exists_history(sessions, session_id):
    """Check if session exists in recentHistory."""
    return any(s["sessionId"] == session_id for s in sessions["recentHistory"])


def count_active_sessions(sessions):
    """Count active sessions."""
    return len(sessions["activeSessions"])


def count_history_sessions(sessions):
    """Count history sessions."""
    return len(sessions["recentHistory"])


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


@pytest.fixture
def status_dir(tmp_path):
    """Create temporary status directory."""
    import shutil
    status = tmp_path / "status"
    status.mkdir()

    # Create schema directory and copy schema file
    schema_dir = tmp_path / ".claude" / "schema"
    schema_dir.mkdir(parents=True)

    # Copy actual schema from workspace
    workspace_schema = Path(__file__).parent.parent.parent.parent.parent.parent / ".claude" / "schema" / "session_summary_schema.json"
    if workspace_schema.exists():
        shutil.copy(workspace_schema, schema_dir / "session_summary_schema.json")

    return status


def run_hook_subprocess(hook_path: Path, payload: Dict[str, Any], env: Dict[str, str]) -> int:
    """Run a hook script in a subprocess and return exit code."""
    result = subprocess.run(
        [sys.executable, str(hook_path)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
    )
    return result.returncode


def start_session_worker(args):
    """Worker function to start a session (for multiprocessing)."""
    hook_path, session_id, status_dir = args

    payload = {
        "session_id": session_id,
        "source": "startup",
        "permission_mode": "default",
        "transcript_path": f"/test/{session_id}.json",
    }

    env = {
        "CLAUDE_WORKSPACE_ROOT": str(status_dir.parent),
        "PATH": sys.path[0],
    }

    return run_hook_subprocess(hook_path, payload, env)


def end_session_worker(args):
    """Worker function to end a session (for multiprocessing)."""
    hook_path, session_id, status_dir = args

    payload = {
        "session_id": session_id,
        "end_reason": "logout",
    }

    env = {
        "CLAUDE_WORKSPACE_ROOT": str(status_dir.parent),
        "PATH": sys.path[0],
    }

    return run_hook_subprocess(hook_path, payload, env)


class TestConcurrentSessionStarts:
    """Test concurrent session start operations."""

    def test_concurrent_starts_all_succeed(
        self,
        session_start_hook,
        status_dir,
    ):
        """Test that multiple concurrent session starts all succeed."""
        num_sessions = 10
        session_ids = [f"sess-concstart{i}" for i in range(num_sessions)]

        # Prepare worker arguments
        worker_args = [(session_start_hook, sid, status_dir) for sid in session_ids]

        # Run all starts concurrently
        with multiprocessing.Pool(processes=num_sessions) as pool:
            results = pool.map(start_session_worker, worker_args)

        # Verify all succeeded
        assert all(result == 0 for result in results), "Some starts failed"

        # Verify all sessions recorded
        active_file = status_dir / "sessions_summary.json"
        with open(active_file) as f:
            sessions = json.load(f)

        assert len(sessions["activeSessions"]) == num_sessions
        for session_id in session_ids:
            assert session_exists_active(sessions, session_id)

    def test_concurrent_starts_no_data_loss(
        self,
        session_start_hook,
        status_dir,
    ):
        """Test that concurrent starts don't lose data."""
        num_sessions = 20
        session_ids = [f"sess-noloss{i}" for i in range(num_sessions)]

        worker_args = [(session_start_hook, sid, status_dir) for sid in session_ids]

        with multiprocessing.Pool(processes=10) as pool:
            pool.map(start_session_worker, worker_args)

        # Verify integrity
        active_file = status_dir / "sessions_summary.json"
        with open(active_file) as f:
            sessions = json.load(f)

        # Should have exactly num_sessions, no duplicates, no missing
        assert len(sessions["activeSessions"]) == num_sessions

        # Verify schema compliance
        for session_id in session_ids:
            session = find_active_session(sessions, session_id)
            assert "startedAt" in session
            assert "sessionSource" in session
            assert "environment" in session
            assert "permissionMode" in session["environment"]


class TestConcurrentSessionEnds:
    """Test concurrent session end operations."""

    def test_concurrent_ends_all_succeed(
        self,
        session_start_hook,
        session_end_hook,
        status_dir,
    ):
        """Test that multiple concurrent session ends all succeed."""
        num_sessions = 10
        session_ids = [f"sess-concend{i}" for i in range(num_sessions)]

        # First, start all sessions sequentially to avoid conflicts
        env = {
            "CLAUDE_WORKSPACE_ROOT": str(status_dir.parent),
            "PATH": sys.path[0],
        }

        for session_id in session_ids:
            payload = {
                "session_id": session_id,
                "source": "startup",
                "permission_mode": "default",
                "transcript_path": f"/test/{session_id}.json",
            }
            run_hook_subprocess(session_start_hook, payload, env)

        # Now end them all concurrently
        worker_args = [(session_end_hook, sid, status_dir) for sid in session_ids]

        with multiprocessing.Pool(processes=num_sessions) as pool:
            results = pool.map(end_session_worker, worker_args)

        # Verify all succeeded
        assert all(result == 0 for result in results), "Some ends failed"

        # Verify all moved to history
        active_file = status_dir / "sessions_summary.json"
        with open(active_file) as f:
            sessions = json.load(f)

        assert len(sessions["activeSessions"]) == 0
        assert len(sessions["recentHistory"]) == num_sessions

        for session_id in session_ids:
            assert session_exists_history(sessions, session_id)
            history_session = find_history_session(sessions, session_id)
            assert "completedAt" in history_session


class TestFileLockingPreventsCorruption:
    """Test that file locking prevents data corruption."""

    def test_rapid_alternating_operations(
        self,
        session_start_hook,
        session_end_hook,
        status_dir,
    ):
        """Test rapid alternating start/end operations."""
        num_iterations = 20

        env = {
            "CLAUDE_WORKSPACE_ROOT": str(status_dir.parent),
            "PATH": sys.path[0],
        }

        # Rapidly start and end sessions
        for i in range(num_iterations):
            session_id = f"sess-rapid{i}"

            start_payload = {
                "session_id": session_id,
                "source": "startup",
                "permission_mode": "default",
                "transcript_path": f"/test/{session_id}.json",
            }

            result = run_hook_subprocess(session_start_hook, start_payload, env)
            assert result == 0

            end_payload = {
                "session_id": session_id,
                "end_reason": "logout",
            }

            result = run_hook_subprocess(session_end_hook, end_payload, env)
            assert result == 0

        # Verify data integrity
        active_file = status_dir / "sessions_summary.json"
        with open(active_file) as f:
            sessions = json.load(f)

        # All should be in history, none active
        assert len(sessions["activeSessions"]) == 0
        assert len(sessions["recentHistory"]) == num_iterations

        # Verify JSON is valid (no corruption)
        assert "summary" in sessions
        assert sessions["summary"]["totalSessionsCompletedLast72Hours"] == num_iterations

    def test_file_remains_valid_json(
        self,
        session_start_hook,
        status_dir,
    ):
        """Test that concurrent writes never corrupt the JSON file."""
        num_sessions = 15

        session_ids = [f"sess-jsonvalid{i}" for i in range(num_sessions)]
        worker_args = [(session_start_hook, sid, status_dir) for sid in session_ids]

        with multiprocessing.Pool(processes=10) as pool:
            pool.map(start_session_worker, worker_args)

        # Read and parse JSON - should not raise exception
        active_file = status_dir / "sessions_summary.json"
        with open(active_file) as f:
            sessions = json.load(f)

        # Verify structure is intact
        assert isinstance(sessions, dict)
        assert "activeSessions" in sessions
        assert "recentHistory" in sessions
        assert "summary" in sessions

        # Verify all sessions present
        assert len(sessions["activeSessions"]) == num_sessions


class TestMixedConcurrentOperations:
    """Test mixed concurrent operations (starts + ends)."""

    def test_simultaneous_starts_and_ends(
        self,
        session_start_hook,
        session_end_hook,
        status_dir,
    ):
        """Test simultaneous session starts and ends."""
        env = {
            "CLAUDE_WORKSPACE_ROOT": str(status_dir.parent),
            "PATH": sys.path[0],
        }

        # Pre-create some sessions to end
        existing_sessions = [f"sess-existing{i}" for i in range(5)]
        for session_id in existing_sessions:
            payload = {
                "session_id": session_id,
                "source": "startup",
                "permission_mode": "default",
                "transcript_path": f"/test/{session_id}.json",
            }
            run_hook_subprocess(session_start_hook, payload, env)

        # Prepare mixed operations
        new_sessions = [f"sess-new{i}" for i in range(5)]

        start_args = [(session_start_hook, sid, status_dir) for sid in new_sessions]
        end_args = [(session_end_hook, sid, status_dir) for sid in existing_sessions]

        all_args = start_args + end_args

        # Shuffle to mix operations
        import random
        random.shuffle(all_args)

        # Execute mixed operations
        with multiprocessing.Pool(processes=10) as pool:
            # Map appropriate worker based on hook type
            results = []
            for hook, sid, sdir in all_args:
                if "session_start" in str(hook):
                    results.append(pool.apply_async(start_session_worker, [(hook, sid, sdir)]))
                else:
                    results.append(pool.apply_async(end_session_worker, [(hook, sid, sdir)]))

            # Wait for all to complete
            exit_codes = [r.get() for r in results]

        # Verify all succeeded
        assert all(code == 0 for code in exit_codes)

        # Verify final state
        active_file = status_dir / "sessions_summary.json"
        with open(active_file) as f:
            sessions = json.load(f)

        # Should have 5 new active sessions
        assert len(sessions["activeSessions"]) == 5

        # Should have 5 sessions in history
        assert len(sessions["recentHistory"]) == 5

        # Verify correct sessions in each category
        for session_id in new_sessions:
            assert session_exists_active(sessions, session_id)

        for session_id in existing_sessions:
            assert session_exists_history(sessions, session_id)


class TestAtomicWrites:
    """Test atomic write operations prevent partial updates."""

    def test_no_partial_writes_on_crash(
        self,
        session_start_hook,
        status_dir,
    ):
        """Test that atomic writes prevent partial data on simulated crashes.

        Note: This is a best-effort test. True crash simulation would require
        more complex infrastructure.
        """
        # Start initial session to create file
        env = {
            "CLAUDE_WORKSPACE_ROOT": str(status_dir.parent),
            "PATH": sys.path[0],
        }

        payload = {
            "session_id": "sess-initial",
            "source": "startup",
            "permission_mode": "default",
            "transcript_path": "/test/initial.json",
        }

        run_hook_subprocess(session_start_hook, payload, env)

        active_file = status_dir / "sessions_summary.json"

        # Record initial file size
        initial_size = active_file.stat().st_size

        # Start many sessions rapidly
        num_sessions = 10
        for i in range(num_sessions):
            payload["session_id"] = f"sess-rapid{i}"
            run_hook_subprocess(session_start_hook, payload, env)

        # Verify file is larger (data was added)
        final_size = active_file.stat().st_size
        assert final_size > initial_size

        # Verify file is still valid JSON (no partial writes)
        with open(active_file) as f:
            sessions = json.load(f)

        # Should have initial + num_sessions
        assert len(sessions["activeSessions"]) == num_sessions + 1
