"""Tests for session_tracking utility functions"""
import pytest
from datetime import datetime, timezone, timedelta
from session_summary.lib.session_tracking import (
    create_session_entry,
    calculate_summary_stats,
    prune_old_history,
    update_indexes,
)
from lucid_cli_commons.git_utils import GitInfo


class TestCreateSessionEntry:
    """Tests for create_session_entry()"""

    def test_create_minimal_session(self, tmp_workspace):
        """Should create session entry with required fields"""
        git_info = GitInfo(tmp_workspace)
        
        entry = create_session_entry(
            session_id="sess-test123",
            source="startup",
            mode="default",
            transcript_path="/path/to/transcript.json",
            git_info=git_info
        )
        
        assert entry["sessionId"] == "sess-test123"
        assert entry["sessionSource"] == "startup"
        assert entry["environment"]["permissionMode"] == "default"
        assert entry["environment"]["transcriptPath"] == "/path/to/transcript.json"
        assert "startedAt" in entry
        assert entry["focusedOutcomes"] == []
        assert entry["events"] == []


class TestCalculateSummaryStats:
    """Tests for calculate_summary_stats()"""

    def test_calculate_with_empty_sessions(self):
        """Should calculate stats for empty sessions"""
        data = {
            "activeSessions": [],
            "recentHistory": []
        }
        
        stats = calculate_summary_stats(data)
        
        assert stats["activeSessionsCount"] == 0
        assert stats["totalSessionsCompletedLast72Hours"] == 0
        assert stats["currentFocusedOutcome"] == "No Focus Set"
        assert stats["totalTokensConsumedLast72Hours"] == 0

    def test_calculate_with_active_sessions(self):
        """Should count active sessions and focused outcomes"""
        now = datetime.now(timezone.utc).isoformat()
        
        data = {
            "activeSessions": [
                {
                    "sessionId": "sess-1",
                    "focusedOutcomes": [
                        {"outcomeId": 1, "outcomeName": "outcome-alpha"},
                        {"outcomeId": 2, "outcomeName": "outcome-beta"}
                    ],
                    "statistics": {"tokensConsumed": 1000, "durationMinutes": 30}
                },
                {
                    "sessionId": "sess-2",
                    "focusedOutcomes": [
                        {"outcomeId": 3, "outcomeName": "outcome-gamma"}
                    ],
                    "statistics": {"tokensConsumed": 500, "durationMinutes": 15}
                }
            ],
            "recentHistory": [
                {
                    "completedAt": now,
                    "tokensConsumed": 2000,
                    "durationMinutes": 60
                }
            ]
        }

        stats = calculate_summary_stats(data)

        assert stats["activeSessionsCount"] == 2
        assert stats["totalSessionsCompletedLast72Hours"] == 1
        # currentFocusedOutcome is the first focused outcome name (schema requires string)
        assert stats["currentFocusedOutcome"] == "outcome-alpha"
        assert stats["totalTokensConsumedLast72Hours"] == 2000  # Only history counted


class TestPruneOldHistory:
    """Tests for prune_old_history()"""

    def test_prune_removes_old_sessions(self):
        """Should remove sessions older than retention period"""
        now = datetime.now(timezone.utc)
        old = now - timedelta(hours=100)
        recent = now - timedelta(hours=24)
        
        data = {
            "recentHistory": [
                {"sessionId": "sess-old", "completedAt": old.isoformat()},
                {"sessionId": "sess-recent", "completedAt": recent.isoformat()}
            ]
        }
        
        prune_old_history(data, hours=72)
        
        assert len(data["recentHistory"]) == 1
        assert data["recentHistory"][0]["sessionId"] == "sess-recent"


class TestUpdateIndexes:
    """Tests for update_indexes()"""

    def test_update_indexes_from_active_sessions(self):
        """Should build indexes from active sessions and history"""
        data = {
            "activeSessions": [
                {
                    "sessionId": "sess-1",
                    "environment": {"gitBranch": "main"},
                    "focusedOutcomes": [
                        {"trackingFile": "outcomes/in-progress/001-test/outcome_track.json"}
                    ]
                }
            ],
            "recentHistory": [
                {
                    "sessionId": "sess-2",
                    "gitBranch": "feature-x",
                    "outcomes": [
                        {"outcomeId": 2, "outcomeName": "test2"}
                    ]
                }
            ],
            "indexByOutcome": {},
            "indexByBranch": {}
        }
        
        update_indexes(data)
        
        assert "outcomes/in-progress/001-test/outcome_track.json" in data["indexByOutcome"]
        assert "sess-1" in data["indexByOutcome"]["outcomes/in-progress/001-test/outcome_track.json"]
        assert "main" in data["indexByBranch"]
        assert "feature-x" in data["indexByBranch"]
