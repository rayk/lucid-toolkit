"""Integration tests for full reconciliation workflow"""
import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch, Mock
from session_summary.lib.reconciliator import SessionReconciliator


class TestFullReconciliationWorkflow:
    """End-to-end reconciliation test"""

    @patch('session_summary.lib.reconciliator.TranscriptParser')
    @patch('session_summary.lib.reconciliator.StaleSessionDetector')
    def test_full_reconciliation_workflow(
        self,
        mock_detector_class,
        mock_parser_class,
        tmp_workspace
    ):
        """
        End-to-end test: Create 5 sessions (active, ended, zombie, test, current),
        run reconciliation, verify correct handling of each
        """
        reconciliator = SessionReconciliator(tmp_workspace)
        now = datetime.now(timezone.utc)

        # Create 5 different types of sessions
        sessions = [
            # 1. Active session (should be preserved and backfilled)
            {
                "sessionId": "sess-active-working",
                "startedAt": (now - timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "sessionSource": "startup",
                "focusedOutcomes": [
                    {
                        "outcomeId": 1,
                        "outcomeName": "Implement Feature",
                        "trackingFile": "outcomes/in-progress/001-implement-feature/outcome_track.json",
                        "focusedAt": (now - timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
                    }
                ],
                "environment": {
                    "workingDirectory": str(tmp_workspace),
                    "transcriptPath": str(tmp_workspace / "transcript1.json"),
                    "gitBranch": "feature-branch",
                    "gitCommitHash": "abcdef1",
                    "permissionMode": "default"
                },
                "events": [],
                "statistics": {
                    "eventsLogged": 10,
                    "tokensConsumed": 5000,
                    "filesModified": 3,
                    "tasksCompleted": 2,
                    "tasksFailed": 0,
                    "gitCommits": 1,
                    "durationMinutes": 30
                },
                "lastActivityAt": (now - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "toolUsageCounts": {"Read": 10, "Write": 5}
            },
            # 2. Ended session (should move to history)
            {
                "sessionId": "sess-ended-yesterday",
                "startedAt": (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "sessionSource": "resume",
                "focusedOutcomes": [
                    {
                        "outcomeId": 2,
                        "outcomeName": "Fix Bug",
                        "trackingFile": "outcomes/completed/002-fix-bug/outcome_track.json",
                        "focusedAt": (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
                    }
                ],
                "environment": {
                    "workingDirectory": str(tmp_workspace),
                    "transcriptPath": str(tmp_workspace / "transcript2.json"),
                    "gitBranch": "bugfix",
                    "gitCommitHash": "def4567",
                    "permissionMode": "default"
                },
                "events": [],
                "statistics": {
                    "eventsLogged": 20,
                    "tokensConsumed": 8000,
                    "filesModified": 8,
                    "tasksCompleted": 5,
                    "tasksFailed": 0,
                    "gitCommits": 3,
                    "durationMinutes": 120
                },
                "lastActivityAt": (now - timedelta(hours=20)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "toolUsageCounts": {"Read": 30, "Edit": 15, "Bash": 10}
            },
            # 3. Zombie session (old, should move to history)
            {
                "sessionId": "sess-zombie-week-old",
                "startedAt": (now - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "sessionSource": "startup",
                "focusedOutcomes": [],
                "environment": {
                    "workingDirectory": str(tmp_workspace),
                    "transcriptPath": str(tmp_workspace / "transcript3.json"),
                    "gitBranch": "old-branch",
                    "gitCommitHash": "abc1234",
                    "permissionMode": "default"
                },
                "events": [],
                "statistics": {
                    "eventsLogged": 5,
                    "tokensConsumed": 2000,
                    "filesModified": 1,
                    "tasksCompleted": 0,
                    "tasksFailed": 0,
                    "gitCommits": 0,
                    "durationMinutes": 60
                },
                "lastActivityAt": (now - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "toolUsageCounts": {"Read": 5}
            },
            # 4. Test session (should be removed entirely)
            {
                "sessionId": "sess-testintegration12345",
                "startedAt": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "sessionSource": "startup",
                "focusedOutcomes": [],
                "environment": {
                    "workingDirectory": str(tmp_workspace),
                    "transcriptPath": str(tmp_workspace / "transcript4.json"),
                    "gitBranch": "main",
                    "gitCommitHash": "fedcba9",
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
            },
            # 5. Current active session (should be preserved)
            {
                "sessionId": "sess-current-main-session",
                "startedAt": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "sessionSource": "startup",
                "focusedOutcomes": [
                    {
                        "outcomeId": 3,
                        "outcomeName": "Refactor Code",
                        "trackingFile": "outcomes/in-progress/003-refactor-code/outcome_track.json",
                        "focusedAt": now.strftime("%Y-%m-%dT%H:%M:%SZ")
                    }
                ],
                "environment": {
                    "workingDirectory": str(tmp_workspace),
                    "transcriptPath": str(tmp_workspace / "transcript5.json"),
                    "gitBranch": "main",
                    "gitCommitHash": "current",
                    "permissionMode": "default"
                },
                "events": [],
                "statistics": {
                    "eventsLogged": 8,
                    "tokensConsumed": 1500,
                    "filesModified": 2,
                    "tasksCompleted": 1,
                    "tasksFailed": 0,
                    "gitCommits": 0,
                    "durationMinutes": 20
                },
                "lastActivityAt": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "toolUsageCounts": {"Read": 8, "Write": 3},
                "subagentsLaunched": 1
            }
        ]

        # Create transcript files
        for i in range(1, 6):
            (tmp_workspace / f"transcript{i}.json").write_text("{}")

        # Set up session data
        data = reconciliator.manager.load()
        data["activeSessions"] = sessions
        reconciliator.manager.save(data)

        # Mock detector to return appropriate states
        mock_detector = Mock()
        from enum import Enum

        class MockSessionState(Enum):
            ACTIVE = "active"
            ENDED = "ended"
            ZOMBIE = "zombie"
            TEST = "test"

        def analyze_side_effect(session):
            sid = session["sessionId"]
            if "TEST" in sid:
                return Mock(state=MockSessionState.TEST)
            elif "ended" in sid:
                return Mock(state=MockSessionState.ENDED)
            elif "zombie" in sid:
                return Mock(state=MockSessionState.ZOMBIE)
            else:
                return Mock(state=MockSessionState.ACTIVE)

        mock_detector.analyze_session.side_effect = analyze_side_effect
        mock_detector_class.return_value = mock_detector

        # Mock parser to return enhanced stats for active sessions
        mock_parser = Mock()

        def parse_side_effect():
            # Return different stats based on which session is being parsed
            return Mock(
                tokens_consumed=10000,  # Enhanced from transcript
                tool_usage_counts={"Read": 20, "Write": 10},
                files_modified=["/file1.py", "/file2.py", "/file3.py"],
                tasks_completed=3,
                subagents_launched=2,
                last_activity_timestamp=now.strftime("%Y-%m-%dT%H:%M:%SZ")
            )

        mock_parser.parse.side_effect = parse_side_effect
        mock_parser_class.return_value = mock_parser

        # Run reconciliation
        report = reconciliator.reconcile_all_sessions()

        # Verify report contents
        assert report.active_count == 2  # sess-active-working and sess-current-main-session
        assert report.moved_count == 2  # sess-ended-yesterday and sess-zombie-week-old
        assert report.cleaned_count == 1  # sess-TEST-integration-12345
        assert report.backfilled_count == 2  # Both active sessions should be backfilled
        assert len(report.errors) == 0  # No errors

        # Verify active sessions
        assert "sess-active-working" in report.preserved_active
        assert "sess-current-main-session" in report.preserved_active

        # Verify moved sessions
        assert "sess-ended-yesterday" in report.moved_to_history
        assert "sess-zombie-week-old" in report.moved_to_history

        # Verify cleaned session
        assert "sess-testintegration12345" in report.cleaned_test_sessions

        # Verify backfilled sessions
        assert "sess-active-working" in report.backfilled_stats
        assert "sess-current-main-session" in report.backfilled_stats

        # Load final data and verify structure
        final_data = reconciliator.manager.load()

        # Should have 2 active sessions
        assert len(final_data["activeSessions"]) == 2
        active_ids = [s["sessionId"] for s in final_data["activeSessions"]]
        assert "sess-active-working" in active_ids
        assert "sess-current-main-session" in active_ids

        # Should have 2 history entries
        assert len(final_data["recentHistory"]) == 2
        history_ids = [h["sessionId"] for h in final_data["recentHistory"]]
        assert "sess-ended-yesterday" in history_ids
        assert "sess-zombie-week-old" in history_ids

        # Verify history entries have correct end reasons
        for entry in final_data["recentHistory"]:
            if entry["sessionId"] == "sess-ended-yesterday":
                assert entry["sessionEndReason"] == "ended"
            elif entry["sessionId"] == "sess-zombie-week-old":
                assert entry["sessionEndReason"] == "zombie"

        # Verify summary was recalculated
        assert final_data["summary"]["activeSessionsCount"] == 2

        # Verify indexes were updated
        assert 1 in final_data["indexByOutcome"]
        assert 3 in final_data["indexByOutcome"]

        # Verify active sessions have backfilled statistics
        for session in final_data["activeSessions"]:
            if session["sessionId"] == "sess-active-working":
                # Should have enhanced stats from transcript
                assert session["statistics"]["tokensConsumed"] == 10000
                assert session["toolUsageCounts"] == {"Read": 20, "Write": 10}
                assert session["statistics"]["filesModified"] == 3
                assert session["statistics"]["tasksCompleted"] == 3
                assert session.get("subagentsLaunched", 0) == 2

        # Verify TEST session is completely gone (not in active or history)
        all_session_ids = active_ids + history_ids
        assert "sess-testintegration12345" not in all_session_ids

        # Print summary for verification
        print("\n=== Reconciliation Summary ===")
        print(f"Active sessions preserved: {report.active_count}")
        print(f"Sessions moved to history: {report.moved_count}")
        print(f"Test sessions cleaned: {report.cleaned_count}")
        print(f"Sessions backfilled: {report.backfilled_count}")
        print(f"Errors: {len(report.errors)}")
        print(f"\nFinal active sessions: {len(final_data['activeSessions'])}")
        print(f"Final history entries: {len(final_data['recentHistory'])}")
