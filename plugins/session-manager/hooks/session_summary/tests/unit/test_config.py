"""Tests for session_summary config module"""
import pytest
from session_summary.lib.config import (
    HISTORY_RETENTION_HOURS,
    STALE_SESSION_HOURS,
    MAX_EVENTS_PER_SESSION,
    SESSION_ID_PATTERN,
    OUTCOME_TRACKING_FILE_PATTERN,
)


class TestConfigConstants:
    """Tests for configuration constants"""

    def test_history_retention_hours(self):
        """Should define history retention period"""
        assert HISTORY_RETENTION_HOURS == 72
        assert isinstance(HISTORY_RETENTION_HOURS, int)

    def test_stale_session_hours(self):
        """Should define stale session threshold"""
        assert STALE_SESSION_HOURS == 4
        assert isinstance(STALE_SESSION_HOURS, int)

    def test_max_events_per_session(self):
        """Should define max events cap"""
        assert MAX_EVENTS_PER_SESSION == 100
        assert isinstance(MAX_EVENTS_PER_SESSION, int)

    def test_session_id_pattern(self):
        """Should define session ID regex pattern"""
        import re
        # Pattern should match valid session IDs
        pattern = re.compile(SESSION_ID_PATTERN)

        # Valid IDs
        assert pattern.match("sess-abc123")
        assert pattern.match("sess-xyz789def")
        assert pattern.match("sess-a1b2c3")

        # Invalid IDs
        assert not pattern.match("session-abc123")
        assert not pattern.match("sess-ABC123")  # uppercase not allowed
        assert not pattern.match("sess-")
        assert not pattern.match("abc123")

    def test_outcome_tracking_file_pattern(self):
        """Should define outcome tracking file regex pattern"""
        import re
        pattern = re.compile(OUTCOME_TRACKING_FILE_PATTERN)

        # Valid paths
        assert pattern.match("outcomes/queued/001-test/outcome_track.json")
        assert pattern.match("outcomes/in-progress/042-auth-system/outcome_track.json")
        assert pattern.match("outcomes/completed/999-final-outcome/outcome_track.json")
        assert pattern.match("outcomes/in-progress/001-test-outcome-name-here/outcome_track.json")

        # Invalid paths
        assert not pattern.match("outcomes/invalid/001-test/outcome_track.json")
        assert not pattern.match("outcomes/queued/test/outcome_track.json")  # no number
        assert not pattern.match("outcomes/queued/001-Test/outcome_track.json")  # uppercase
        assert not pattern.match("status/001-test/outcome_track.json")  # wrong dir
