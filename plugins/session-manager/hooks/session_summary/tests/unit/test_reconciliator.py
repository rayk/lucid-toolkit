"""Unit tests for SessionReconciliator class"""
import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from session_summary.lib.reconciliator import SessionReconciliator, ReconciliationReport


class TestReconcileEmptySessions:
    """Test handling of empty activeSessions list"""

    def test_reconcile_empty_sessions(self, tmp_workspace):
        """Should handle empty activeSessions list gracefully"""
        reconciliator = SessionReconciliator(tmp_workspace)

        # Create empty structure
        data = reconciliator.manager.load()
        assert data["activeSessions"] == []

        # Run reconciliation
        report = reconciliator.reconcile_all_sessions()

        # Should return empty report
        assert report.moved_count == 0
        assert report.cleaned_count == 0
        assert report.backfilled_count == 0
        assert report.active_count == 0
        assert len(report.errors) == 0


class TestBackfillSingleSessionStats:
    """Test backfilling statistics from transcript"""

    @patch('session_summary.lib.reconciliator.TranscriptParser')
    def test_backfill_single_session_stats(self, mock_parser_class, tmp_workspace):
        """Should parse transcript and update session statistics in place"""
        reconciliator = SessionReconciliator(tmp_workspace)

        # Create a session with minimal stats
        now = datetime.now(timezone.utc)
        session = {
            "sessionId": "sess-active",
            "startedAt": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sessionSource": "startup",
            "focusedOutcomes": [],
            "environment": {
                "workingDirectory": str(tmp_workspace),
                "transcriptPath": str(tmp_workspace / "transcript.json"),
                "gitBranch": "main",
                "gitCommitHash": "abcdef1",
                "permissionMode": "default"
            },
            "events": [],
            "statistics": {
                "eventsLogged": 0,
                "tokensConsumed": 100,
                "filesModified": 0,
                "tasksCompleted": 0,
                "tasksFailed": 0,
                "gitCommits": 0,
                "durationMinutes": 0
            },
            "lastActivityAt": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "toolUsageCounts": {}
        }

        # Create transcript file
        transcript_path = tmp_workspace / "transcript.json"
        transcript_path.write_text("{}")

        # Mock parser to return enhanced stats
        mock_parser = Mock()
        mock_parser.parse.return_value = Mock(
            tokens_consumed=500,
            tool_usage_counts={"Read": 10, "Write": 5},
            files_modified=["/file1.py", "/file2.py"],
            tasks_completed=3,
            subagents_launched=1,
            last_activity_timestamp=(now + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        mock_parser_class.return_value = mock_parser

        # Add session to data
        data = reconciliator.manager.load()
        data["activeSessions"] = [session]
        reconciliator.manager.save(data)

        # Mock detector to return ACTIVE state
        with patch('session_summary.lib.reconciliator.StaleSessionDetector') as mock_detector_class:
            mock_detector = Mock()
            mock_detector.analyze_session.return_value = Mock(
                state=Mock(value='active')
            )
            # Use Mock's attribute to avoid enum comparison issues
            mock_detector.analyze_session.return_value.state.name = 'ACTIVE'
            mock_detector_class.return_value = mock_detector

            # Run reconciliation
            report = reconciliator.reconcile_all_sessions()

        # Verify stats were updated
        data = reconciliator.manager.load()
        updated_session = data["activeSessions"][0]

        assert updated_session["statistics"]["tokensConsumed"] == 500
        assert updated_session["toolUsageCounts"] == {"Read": 10, "Write": 5}
        assert updated_session["statistics"]["filesModified"] == 2
        assert updated_session["statistics"]["tasksCompleted"] == 3
        assert updated_session["subagentsLaunched"] == 1

        # Verify report
        assert report.backfilled_count == 1
        assert report.active_count == 1
        assert "sess-active" in report.backfilled_stats


class TestMoveEndedSessionToHistory:
    """Test moving ended sessions to history"""

    @patch('session_summary.lib.reconciliator.TranscriptParser')
    @patch('session_summary.lib.reconciliator.StaleSessionDetector')
    def test_move_ended_session_to_history(
        self,
        mock_detector_class,
        mock_parser_class,
        tmp_workspace
    ):
        """Should detect ENDED session and move to recentHistory"""
        reconciliator = SessionReconciliator(tmp_workspace)

        # Create an ended session
        now = datetime.now(timezone.utc)
        session = {
            "sessionId": "sess-ended",
            "startedAt": (now - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sessionSource": "startup",
            "focusedOutcomes": [],
            "environment": {
                "workingDirectory": str(tmp_workspace),
                "transcriptPath": str(tmp_workspace / "transcript.json"),
                "gitBranch": "main",
                "gitCommitHash": "abcdef1",
                "permissionMode": "default"
            },
            "events": [],
            "statistics": {
                "eventsLogged": 5,
                "tokensConsumed": 1000,
                "filesModified": 5,
                "tasksCompleted": 2,
                "tasksFailed": 0,
                "gitCommits": 1,
                "durationMinutes": 120
            },
            "lastActivityAt": (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "toolUsageCounts": {"Read": 20}
        }

        # Create transcript file
        transcript_path = tmp_workspace / "transcript.json"
        transcript_path.write_text("{}")

        # Mock detector to return ENDED state
        mock_detector = Mock()
        from enum import Enum

        class MockSessionState(Enum):
            ENDED = "ended"
            ACTIVE = "active"

        mock_detector.analyze_session.return_value = Mock(
            state=MockSessionState.ENDED
        )
        mock_detector_class.return_value = mock_detector

        # Mock parser
        mock_parser = Mock()
        mock_parser.parse.return_value = Mock(
            tokens_consumed=1000,
            tool_usage_counts={"Read": 20},
            files_modified=[],
            tasks_completed=2,
            subagents_launched=0,
            last_activity_timestamp=session["lastActivityAt"]
        )
        mock_parser_class.return_value = mock_parser

        # Add session to data
        data = reconciliator.manager.load()
        data["activeSessions"] = [session]
        reconciliator.manager.save(data)

        # Run reconciliation
        report = reconciliator.reconcile_all_sessions()

        # Verify session moved to history
        data = reconciliator.manager.load()
        assert len(data["activeSessions"]) == 0
        assert len(data["recentHistory"]) == 1

        history_entry = data["recentHistory"][0]
        assert history_entry["sessionId"] == "sess-ended"
        assert history_entry["sessionEndReason"] == "ended"
        assert history_entry["tokensConsumed"] == 1000

        # Verify report
        assert report.moved_count == 1
        assert "sess-ended" in report.moved_to_history


class TestCleanupTestSessions:
    """Test removing TEST sessions"""

    @patch('session_summary.lib.reconciliator.StaleSessionDetector')
    def test_cleanup_test_sessions(self, mock_detector_class, tmp_workspace):
        """Should remove TEST sessions from activeSessions entirely"""
        reconciliator = SessionReconciliator(tmp_workspace)

        # Create a test session
        now = datetime.now(timezone.utc)
        session = {
            "sessionId": "sess-test12345",
            "startedAt": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sessionSource": "startup",
            "focusedOutcomes": [],
            "environment": {
                "workingDirectory": str(tmp_workspace),
                "transcriptPath": str(tmp_workspace / "transcript.json"),
                "gitBranch": "main",
                "gitCommitHash": "abcdef1",
                "permissionMode": "default"
            },
            "events": [],
            "statistics": {
                "eventsLogged": 0,
                "tokensConsumed": 10,
                "filesModified": 0,
                "tasksCompleted": 0,
                "tasksFailed": 0,
                "gitCommits": 0,
                "durationMinutes": 0
            },
            "lastActivityAt": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "toolUsageCounts": {}
        }

        # Create transcript file
        transcript_path = tmp_workspace / "transcript.json"
        transcript_path.write_text("{}")

        # Mock detector to return TEST state
        mock_detector = Mock()
        from enum import Enum

        class MockSessionState(Enum):
            TEST = "test"
            ACTIVE = "active"

        mock_detector.analyze_session.return_value = Mock(
            state=MockSessionState.TEST
        )
        mock_detector_class.return_value = mock_detector

        # Add session to data
        data = reconciliator.manager.load()
        data["activeSessions"] = [session]
        reconciliator.manager.save(data)

        # Run reconciliation
        report = reconciliator.reconcile_all_sessions()

        # Verify session removed (not in active or history)
        data = reconciliator.manager.load()
        assert len(data["activeSessions"]) == 0
        assert len(data["recentHistory"]) == 0

        # Verify report
        assert report.cleaned_count == 1
        assert "sess-test12345" in report.cleaned_test_sessions


class TestPreserveActiveSessions:
    """Test that active sessions are preserved"""

    @patch('session_summary.lib.reconciliator.TranscriptParser')
    @patch('session_summary.lib.reconciliator.StaleSessionDetector')
    def test_preserve_active_sessions(
        self,
        mock_detector_class,
        mock_parser_class,
        tmp_workspace
    ):
        """Should not modify genuinely ACTIVE sessions"""
        reconciliator = SessionReconciliator(tmp_workspace)

        # Create an active session
        now = datetime.now(timezone.utc)
        session = {
            "sessionId": "sess-currentactive",
            "startedAt": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sessionSource": "startup",
            "focusedOutcomes": [],
            "environment": {
                "workingDirectory": str(tmp_workspace),
                "transcriptPath": str(tmp_workspace / "transcript.json"),
                "gitBranch": "main",
                "gitCommitHash": "abcdef1",
                "permissionMode": "default"
            },
            "events": [],
            "statistics": {
                "eventsLogged": 3,
                "tokensConsumed": 500,
                "filesModified": 3,
                "tasksCompleted": 1,
                "tasksFailed": 0,
                "gitCommits": 0,
                "durationMinutes": 30
            },
            "lastActivityAt": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "toolUsageCounts": {"Read": 5}
        }

        # Create transcript file
        transcript_path = tmp_workspace / "transcript.json"
        transcript_path.write_text("{}")

        # Mock detector to return ACTIVE state
        mock_detector = Mock()
        from enum import Enum

        class MockSessionState(Enum):
            ACTIVE = "active"

        mock_detector.analyze_session.return_value = Mock(
            state=MockSessionState.ACTIVE
        )
        mock_detector_class.return_value = mock_detector

        # Mock parser (no changes)
        mock_parser = Mock()
        mock_parser.parse.return_value = Mock(
            tokens_consumed=500,
            tool_usage_counts={"Read": 5},
            files_modified=[],
            tasks_completed=1,
            subagents_launched=0,
            last_activity_timestamp=session["lastActivityAt"]
        )
        mock_parser_class.return_value = mock_parser

        # Add session to data
        data = reconciliator.manager.load()
        data["activeSessions"] = [session]
        reconciliator.manager.save(data)

        # Run reconciliation
        report = reconciliator.reconcile_all_sessions()

        # Verify session remains in activeSessions
        data = reconciliator.manager.load()
        assert len(data["activeSessions"]) == 1
        assert data["activeSessions"][0]["sessionId"] == "sess-currentactive"
        assert len(data["recentHistory"]) == 0

        # Verify report
        assert report.active_count == 1
        assert "sess-currentactive" in report.preserved_active


class TestReconcileAllSessions:
    """Test processing all active sessions"""

    @patch('session_summary.lib.reconciliator.TranscriptParser')
    @patch('session_summary.lib.reconciliator.StaleSessionDetector')
    def test_reconcile_all_sessions(
        self,
        mock_detector_class,
        mock_parser_class,
        tmp_workspace
    ):
        """Should process all active sessions and update summary"""
        reconciliator = SessionReconciliator(tmp_workspace)

        # Create multiple sessions with different states
        now = datetime.now(timezone.utc)

        sessions = [
            {
                "sessionId": "sess-active-1",
                "startedAt": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "sessionSource": "startup",
                "focusedOutcomes": [],
                "environment": {
                    "workingDirectory": str(tmp_workspace),
                    "transcriptPath": str(tmp_workspace / "t1.json"),
                    "gitBranch": "main",
                    "gitCommitHash": "abcdef1",
                    "permissionMode": "default"
                },
                "events": [],
                "statistics": {
                    "tokensConsumed": 100,
                    "filesModified": 0,
                    "tasksCompleted": 0,
                    "gitCommits": 0
                },
                "lastActivityAt": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "toolUsageCounts": {}
            },
            {
                "sessionId": "sess-test999",
                "startedAt": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "sessionSource": "startup",
                "focusedOutcomes": [],
                "environment": {
                    "workingDirectory": str(tmp_workspace),
                    "transcriptPath": str(tmp_workspace / "t2.json"),
                    "gitBranch": "main",
                    "gitCommitHash": "abcdef1",
                    "permissionMode": "default"
                },
                "events": [],
                "statistics": {
                    "tokensConsumed": 10,
                    "filesModified": 0,
                    "tasksCompleted": 0,
                    "gitCommits": 0
                },
                "lastActivityAt": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "toolUsageCounts": {}
            },
            {
                "sessionId": "sess-endedold",
                "startedAt": (now - timedelta(hours=48)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "sessionSource": "startup",
                "focusedOutcomes": [],
                "environment": {
                    "workingDirectory": str(tmp_workspace),
                    "transcriptPath": str(tmp_workspace / "t3.json"),
                    "gitBranch": "main",
                    "gitCommitHash": "abcdef1",
                    "permissionMode": "default"
                },
                "events": [],
                "statistics": {
                    "eventsLogged": 5,
                    "tokensConsumed": 1000,
                    "filesModified": 5,
                    "tasksCompleted": 2,
                    "tasksFailed": 0,
                    "gitCommits": 1,
                    "durationMinutes": 120
                },
                "lastActivityAt": (now - timedelta(hours=47)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "toolUsageCounts": {"Read": 10}
            }
        ]

        # Create transcript files
        for i in range(1, 4):
            (tmp_workspace / f"t{i}.json").write_text("{}")

        # Mock detector to return different states
        mock_detector = Mock()
        from enum import Enum

        class MockSessionState(Enum):
            ACTIVE = "active"
            TEST = "test"
            ENDED = "ended"

        def analyze_side_effect(session):
            sid = session["sessionId"].lower()
            if "test" in sid:
                return Mock(state=MockSessionState.TEST)
            elif "ended" in sid:
                return Mock(state=MockSessionState.ENDED)
            else:
                return Mock(state=MockSessionState.ACTIVE)

        mock_detector.analyze_session.side_effect = analyze_side_effect
        mock_detector_class.return_value = mock_detector

        # Mock parser
        mock_parser = Mock()
        mock_parser.parse.return_value = Mock(
            tokens_consumed=100,
            tool_usage_counts={},
            files_modified=[],
            tasks_completed=0,
            subagents_launched=0,
            last_activity_timestamp=now.strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        mock_parser_class.return_value = mock_parser

        # Add sessions to data
        data = reconciliator.manager.load()
        data["activeSessions"] = sessions
        reconciliator.manager.save(data)

        # Run reconciliation
        report = reconciliator.reconcile_all_sessions()

        # Verify results
        data = reconciliator.manager.load()
        assert len(data["activeSessions"]) == 1  # Only active-1 remains
        assert len(data["recentHistory"]) == 1  # ended-old moved to history

        # Verify report
        assert report.active_count == 1
        assert report.cleaned_count == 1
        assert report.moved_count == 1


class TestGenerateReconciliationReport:
    """Test reconciliation report generation"""

    def test_generate_reconciliation_report(self, tmp_workspace):
        """Should return detailed report of actions taken"""
        # Create report manually
        report = ReconciliationReport(
            moved_to_history=["sess-1", "sess-2"],
            cleaned_test_sessions=["sess-TEST-1"],
            backfilled_stats=["sess-3", "sess-4", "sess-5"],
            preserved_active=["sess-6"],
            errors=["sess-7: File not found"]
        )

        # Test properties
        assert report.moved_count == 2
        assert report.cleaned_count == 1
        assert report.backfilled_count == 3
        assert report.active_count == 1
        assert len(report.errors) == 1

        # Test list contents
        assert "sess-1" in report.moved_to_history
        assert "sess-TEST-1" in report.cleaned_test_sessions
        assert "sess-3" in report.backfilled_stats
        assert "sess-6" in report.preserved_active
        assert "sess-7: File not found" in report.errors


class TestHandleConcurrentModifications:
    """Test thread-safety using SessionManager's locking"""

    def test_handle_concurrent_modifications(self, tmp_workspace):
        """Should use SessionManager's locking to prevent race conditions"""
        reconciliator = SessionReconciliator(tmp_workspace)

        # SessionManager already uses FileLockManager internally
        # This test verifies that reconciliation uses SessionManager's
        # load/save methods, which handle locking automatically

        # Create a session
        now = datetime.now(timezone.utc)
        data = reconciliator.manager.load()
        data["activeSessions"] = [{
            "sessionId": "sess-test",
            "startedAt": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sessionSource": "startup",
            "focusedOutcomes": [],
            "environment": {
                "workingDirectory": str(tmp_workspace),
                "transcriptPath": str(tmp_workspace / "transcript.json"),
                "gitBranch": "main",
                "gitCommitHash": "abcdef1",
                "permissionMode": "default"
            },
            "events": [],
            "statistics": {
                "eventsLogged": 0,
                "tokensConsumed": 100,
                "filesModified": 0,
                "tasksCompleted": 0,
                "tasksFailed": 0,
                "gitCommits": 0,
                "durationMinutes": 0
            },
            "lastActivityAt": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "toolUsageCounts": {}
        }]

        # Create transcript file
        transcript_path = tmp_workspace / "transcript.json"
        transcript_path.write_text("{}")

        reconciliator.manager.save(data)

        # Verify that locking works (lock file is cleaned up after save)
        lock_file = tmp_workspace / "status" / ".sessions_summary.lock"

        # Run reconciliation with mocked detector
        with patch('session_summary.lib.reconciliator.StaleSessionDetector') as mock_detector_class:
            mock_detector = Mock()
            from enum import Enum

            class MockSessionState(Enum):
                ACTIVE = "active"

            mock_detector.analyze_session.return_value = Mock(
                state=MockSessionState.ACTIVE
            )
            mock_detector_class.return_value = mock_detector

            with patch('session_summary.lib.reconciliator.TranscriptParser') as mock_parser_class:
                mock_parser = Mock()
                mock_parser.parse.return_value = Mock(
                    tokens_consumed=100,
                    tool_usage_counts={},
                    files_modified=[],
                    tasks_completed=0,
                    subagents_launched=0,
                    last_activity_timestamp=now.strftime("%Y-%m-%dT%H:%M:%SZ")
                )
                mock_parser_class.return_value = mock_parser

                report = reconciliator.reconcile_all_sessions()

        # Verify reconciliation completed successfully
        assert report.active_count == 1

        # Verify no lock files left behind (atomic_write cleans up)
        lock_files = list((tmp_workspace / "status").glob("*.lock"))
        assert len(lock_files) == 0, f"Found lock files: {lock_files}"
