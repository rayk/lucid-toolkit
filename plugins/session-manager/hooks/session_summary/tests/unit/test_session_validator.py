"""Tests for session_validator module"""
import pytest
from session_summary.lib.session_validator import (
    validate_session_id,
    validate_outcome_tracking_file,
    validate_session_data,
)


class TestSessionIdValidation:
    """Tests for session ID validation"""

    def test_valid_session_ids(self):
        """Should accept valid session IDs"""
        validate_session_id("sess-abc123")
        validate_session_id("sess-xyz789def456")
        validate_session_id("sess-a1b2c3d4e5f6")

    def test_invalid_session_ids(self):
        """Should reject invalid session IDs"""
        with pytest.raises(ValueError, match="Invalid session ID"):
            validate_session_id("session-abc123")

        with pytest.raises(ValueError, match="Invalid session ID"):
            validate_session_id("sess-ABC123")  # uppercase

        with pytest.raises(ValueError, match="Invalid session ID"):
            validate_session_id("sess-")  # empty suffix

        with pytest.raises(ValueError, match="Invalid session ID"):
            validate_session_id("abc123")  # no prefix


class TestOutcomeTrackingFileValidation:
    """Tests for outcome tracking file path validation"""

    def test_valid_outcome_paths(self):
        """Should accept valid outcome tracking file paths"""
        validate_outcome_tracking_file("outcomes/queued/001-test/outcome_track.json")
        validate_outcome_tracking_file("outcomes/in-progress/042-auth-system/outcome_track.json")
        validate_outcome_tracking_file("outcomes/completed/999-final/outcome_track.json")
        validate_outcome_tracking_file("outcomes/in-progress/001-a-b-c-d-e/outcome_track.json")

    def test_invalid_outcome_paths(self):
        """Should reject invalid outcome tracking file paths"""
        with pytest.raises(ValueError, match="Invalid outcome tracking file"):
            validate_outcome_tracking_file("outcomes/invalid/001-test/outcome_track.json")

        with pytest.raises(ValueError, match="Invalid outcome tracking file"):
            validate_outcome_tracking_file("outcomes/queued/test/outcome_track.json")  # no number

        with pytest.raises(ValueError, match="Invalid outcome tracking file"):
            validate_outcome_tracking_file("status/001-test/outcome_track.json")  # wrong dir


class TestSessionDataValidation:
    """Tests for full session data validation"""

    def test_valid_session_data_minimal(self, tmp_workspace):
        """Should accept minimal valid session data"""
        # Initialize paths with tmp_workspace
        from lucid_cli_commons.paths import get_paths
        get_paths(tmp_workspace)

        data = {
            "summary": {
                "activeSessionsCount": 0,
                "totalSessionsCompletedLast72Hours": 0,
                "currentFocusedOutcome": "No Focus Set",
                "totalTokensConsumedLast72Hours": 0,
                "totalDurationMinutesLast72Hours": 0,
                "lastUpdated": "2025-11-19T14:30:00Z"
            },
            "activeSessions": [],
            "lastWorked": None,
            "recentHistory": [],
            "indexByOutcome": {},
            "indexByBranch": {}
        }
        validate_session_data(data)  # Should not raise

    def test_missing_required_field(self):
        """Should reject data missing required fields"""
        data = {
            "summary": {},
            "activeSessions": []
            # Missing other required fields
        }
        with pytest.raises(ValueError, match="validation failed"):
            validate_session_data(data)

    def test_invalid_field_type(self):
        """Should reject data with wrong field types"""
        data = {
            "summary": {
                "activeSessionsCount": "not a number",  # should be int
                "totalSessionsCompletedLast72Hours": 0,
                "currentFocusedOutcome": "No Focus Set",
                "totalTokensConsumedLast72Hours": 0,
                "totalDurationMinutesLast72Hours": 0,
                "lastUpdated": "2025-11-19T14:30:00Z"
            },
            "activeSessions": [],
            "lastWorked": None,
            "recentHistory": [],
            "indexByOutcome": {},
            "indexByBranch": {}
        }
        with pytest.raises(ValueError, match="validation failed"):
            validate_session_data(data)
