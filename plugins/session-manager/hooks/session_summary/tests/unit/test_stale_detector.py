"""Tests for StaleSessionDetector module using Test-Driven Development"""
import pytest
from pathlib import Path
from datetime import datetime, timezone, timedelta
from session_summary.lib.stale_detector import (
    StaleSessionDetector,
    SessionState,
    StateAnalysis,
)


class TestDetectTestSessionPaths:
    """Should classify sessions with /test or /tmp/* paths as TEST"""

    def test_detect_test_path(self):
        """Should classify /test path as TEST"""
        detector = StaleSessionDetector()
        session = {
            "sessionId": "sess-test001",
            "sessionSource": "startup",
            "startedAt": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
            "lastActivityAt": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
            "environment": {
                "transcriptPath": "/test"
            }
        }

        analysis = detector.analyze_session(session)

        assert analysis.state == SessionState.TEST
        assert analysis.confidence == "high"
        assert "test path" in " ".join(analysis.reasons).lower()

    def test_detect_tmp_path(self):
        """Should classify /tmp/* path as TEST"""
        detector = StaleSessionDetector()
        session = {
            "sessionId": "sess-test002",
            "sessionSource": "startup",
            "startedAt": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
            "lastActivityAt": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
            "environment": {
                "transcriptPath": "/tmp/test-session-abc123.jsonl"
            }
        }

        analysis = detector.analyze_session(session)

        assert analysis.state == SessionState.TEST
        assert analysis.confidence == "high"

    def test_detect_tmp_nested_path(self):
        """Should classify /tmp/nested/path as TEST"""
        detector = StaleSessionDetector()
        session = {
            "sessionId": "sess-test003",
            "sessionSource": "startup",
            "startedAt": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
            "lastActivityAt": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
            "environment": {
                "transcriptPath": "/tmp/some/nested/path/transcript.jsonl"
            }
        }

        analysis = detector.analyze_session(session)

        assert analysis.state == SessionState.TEST


class TestDetectEndedViaTranscript:
    """Should classify sessions with exit/logout in transcript as ENDED"""

    def test_detect_exit_in_transcript(self, tmp_path):
        """Should find exit command in transcript and classify as ENDED"""
        # Create mock transcript file
        transcript_path = tmp_path / "transcript.jsonl"
        transcript_lines = [
            '{"type": "command", "content": "ls"}',
            '{"type": "command", "content": "pwd"}',
            '{"type": "command", "content": "exit"}',
        ]
        transcript_path.write_text("\n".join(transcript_lines))

        detector = StaleSessionDetector()
        session = {
            "sessionId": "sess-exit001",
            "sessionSource": "startup",
            "startedAt": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
            "lastActivityAt": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
            "environment": {
                "transcriptPath": str(transcript_path)
            }
        }

        analysis = detector.analyze_session(session)

        assert analysis.state == SessionState.ENDED
        assert analysis.found_end_marker is True
        assert "exit" in " ".join(analysis.reasons).lower()

    def test_detect_logout_in_transcript(self, tmp_path):
        """Should find logout command in transcript and classify as ENDED"""
        transcript_path = tmp_path / "transcript.jsonl"
        transcript_lines = [
            '{"type": "command", "content": "ls"}',
            '{"type": "command", "content": "logout"}',
        ]
        transcript_path.write_text("\n".join(transcript_lines))

        detector = StaleSessionDetector()
        session = {
            "sessionId": "sess-logout001",
            "sessionSource": "startup",
            "startedAt": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
            "lastActivityAt": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
            "environment": {
                "transcriptPath": str(transcript_path)
            }
        }

        analysis = detector.analyze_session(session)

        assert analysis.state == SessionState.ENDED
        assert analysis.found_end_marker is True


class TestDetectStaleByAge:
    """Should classify 24h+ old sessions with no activity as ZOMBIE"""

    def test_detect_old_session_no_activity(self, tmp_path):
        """Should classify old session (24h+) with no activity as ZOMBIE"""
        # Create empty transcript file
        transcript_path = tmp_path / "old_transcript.jsonl"
        transcript_path.write_text("")

        detector = StaleSessionDetector()
        old_time = datetime.now(timezone.utc) - timedelta(hours=30)

        session = {
            "sessionId": "sess-old001",
            "sessionSource": "startup",
            "startedAt": old_time.isoformat(),
            "lastActivityAt": old_time.isoformat(),
            "environment": {
                "transcriptPath": str(transcript_path)
            }
        }

        analysis = detector.analyze_session(session)

        assert analysis.state == SessionState.ZOMBIE
        assert analysis.confidence == "medium"
        assert analysis.found_end_marker is False
        assert analysis.age_hours >= 24


class TestCheckDebugLogsForSessionEnd:
    """Should find SessionEnd events in debug logs and classify as ENDED"""

    def test_find_session_end_in_debug_log(self, tmp_path):
        """Should find SessionEnd event in debug logs"""
        # Create mock debug log
        debug_log_path = tmp_path / "debug.log"
        debug_lines = [
            "[2025-11-19 10:00:00] [INFO] SessionStart: session_id=sess-dbg001",
            "[2025-11-19 10:05:00] [DEBUG] Processing command",
            "[2025-11-19 10:10:00] [INFO] SessionEnd: session_id=sess-dbg001, reason=logout",
        ]
        debug_log_path.write_text("\n".join(debug_lines))

        detector = StaleSessionDetector(debug_log_path=debug_log_path)
        session = {
            "sessionId": "sess-dbg001",
            "sessionSource": "startup",
            "startedAt": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
            "lastActivityAt": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
            "environment": {
                "transcriptPath": "/Users/test/project/transcript.jsonl"
            }
        }

        analysis = detector.analyze_session(session)

        assert analysis.state == SessionState.ENDED
        assert analysis.found_end_marker is True

    def test_no_session_end_in_debug_log(self, tmp_path):
        """Should not find SessionEnd for different session ID"""
        debug_log_path = tmp_path / "debug.log"
        debug_lines = [
            "[2025-11-19 10:00:00] [INFO] SessionStart: session_id=sess-other001",
            "[2025-11-19 10:10:00] [INFO] SessionEnd: session_id=sess-other001, reason=logout",
        ]
        debug_log_path.write_text("\n".join(debug_lines))

        # Create transcript file so it exists
        transcript_path = tmp_path / "transcript.jsonl"
        transcript_path.write_text("")

        detector = StaleSessionDetector(debug_log_path=debug_log_path)
        session = {
            "sessionId": "sess-missing001",
            "sessionSource": "startup",
            "startedAt": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
            "lastActivityAt": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
            "environment": {
                "transcriptPath": str(transcript_path)
            }
        }

        analysis = detector.analyze_session(session)

        # Should be ACTIVE since it's < 4h old
        assert analysis.state == SessionState.ACTIVE
        assert analysis.found_end_marker is False


class TestClassifyActiveSession:
    """Should classify recent sessions (<4h old) with valid path as ACTIVE"""

    def test_classify_recent_session_as_active(self, tmp_path):
        """Should classify recent session (<4h) as ACTIVE"""
        # Create transcript file
        transcript_path = tmp_path / "active_transcript.jsonl"
        transcript_path.write_text("")

        detector = StaleSessionDetector()
        recent_time = datetime.now(timezone.utc) - timedelta(hours=1)

        session = {
            "sessionId": "sess-active001",
            "sessionSource": "startup",
            "startedAt": recent_time.isoformat(),
            "lastActivityAt": recent_time.isoformat(),
            "environment": {
                "transcriptPath": str(transcript_path)
            }
        }

        analysis = detector.analyze_session(session)

        assert analysis.state == SessionState.ACTIVE
        assert analysis.confidence == "high"
        assert analysis.age_hours < 4
        assert analysis.found_end_marker is False

    def test_classify_new_session_as_active(self, tmp_path):
        """Should classify very recent session as ACTIVE"""
        # Create transcript file
        transcript_path = tmp_path / "new_transcript.jsonl"
        transcript_path.write_text("")

        detector = StaleSessionDetector()
        very_recent_time = datetime.now(timezone.utc) - timedelta(minutes=10)

        session = {
            "sessionId": "sess-active002",
            "sessionSource": "startup",
            "startedAt": very_recent_time.isoformat(),
            "lastActivityAt": very_recent_time.isoformat(),
            "environment": {
                "transcriptPath": str(transcript_path)
            }
        }

        analysis = detector.analyze_session(session)

        assert analysis.state == SessionState.ACTIVE
        assert analysis.age_hours < 1


class TestClassifyEndedSession:
    """Should classify sessions with end markers as ENDED"""

    def test_classify_with_completed_at(self):
        """Should classify session with completedAt timestamp as ENDED"""
        detector = StaleSessionDetector()
        session = {
            "sessionId": "sess-completed001",
            "sessionSource": "startup",
            "startedAt": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
            "lastActivityAt": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
            "completedAt": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
            "environment": {
                "transcriptPath": "/Users/test/project/transcript.jsonl"
            }
        }

        analysis = detector.analyze_session(session)

        assert analysis.state == SessionState.ENDED
        assert analysis.found_end_marker is True

    def test_classify_session_with_end_reason(self):
        """Should classify session with endReason as ENDED"""
        detector = StaleSessionDetector()
        session = {
            "sessionId": "sess-reason001",
            "sessionSource": "startup",
            "startedAt": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
            "lastActivityAt": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
            "endReason": "logout",
            "environment": {
                "transcriptPath": "/Users/test/project/transcript.jsonl"
            }
        }

        analysis = detector.analyze_session(session)

        assert analysis.state == SessionState.ENDED
        assert analysis.found_end_marker is True


class TestClassifyZombieSession:
    """Should classify old sessions without end markers as ZOMBIE"""

    def test_classify_zombie_no_end_markers(self, tmp_path):
        """Should classify old session with no end markers as ZOMBIE"""
        # Create transcript file
        transcript_path = tmp_path / "zombie_transcript.jsonl"
        transcript_path.write_text("")

        detector = StaleSessionDetector()
        old_time = datetime.now(timezone.utc) - timedelta(hours=48)

        session = {
            "sessionId": "sess-zombie001",
            "sessionSource": "startup",
            "startedAt": old_time.isoformat(),
            "lastActivityAt": old_time.isoformat(),
            "environment": {
                "transcriptPath": str(transcript_path)
            }
        }

        analysis = detector.analyze_session(session)

        assert analysis.state == SessionState.ZOMBIE
        assert analysis.confidence == "medium"
        assert analysis.found_end_marker is False
        assert analysis.age_hours >= 24

    def test_classify_zombie_with_stale_activity(self, tmp_path):
        """Should classify session with stale activity (12h+) as ZOMBIE"""
        # Create transcript file
        transcript_path = tmp_path / "stale_transcript.jsonl"
        transcript_path.write_text("")

        detector = StaleSessionDetector()
        stale_time = datetime.now(timezone.utc) - timedelta(hours=25)

        session = {
            "sessionId": "sess-zombie002",
            "sessionSource": "startup",
            "startedAt": stale_time.isoformat(),
            "lastActivityAt": stale_time.isoformat(),
            "environment": {
                "transcriptPath": str(transcript_path)
            }
        }

        analysis = detector.analyze_session(session)

        assert analysis.state == SessionState.ZOMBIE
        assert analysis.age_hours > 24


class TestDetectMissingTranscriptFile:
    """Should classify sessions with missing transcript files as ENDED"""

    def test_detect_missing_transcript_file(self):
        """Should classify session with non-existent transcript as ENDED"""
        detector = StaleSessionDetector()
        session = {
            "sessionId": "sess-missing001",
            "sessionSource": "startup",
            "startedAt": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
            "lastActivityAt": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
            "environment": {
                "transcriptPath": "/Users/test/nonexistent/transcript.jsonl"
            }
        }

        analysis = detector.analyze_session(session)

        assert analysis.state == SessionState.ENDED
        assert "transcript file missing" in " ".join(analysis.reasons).lower()
        assert analysis.confidence == "high"

    def test_detect_missing_temp_transcript(self):
        """Should classify session with missing temp transcript as ENDED"""
        detector = StaleSessionDetector()
        session = {
            "sessionId": "sess-tempgone001",
            "sessionSource": "startup",
            "startedAt": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
            "lastActivityAt": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
            "environment": {
                "transcriptPath": "/var/folders/tmp/deleted-transcript.jsonl"
            }
        }

        analysis = detector.analyze_session(session)

        assert analysis.state == SessionState.ENDED
        assert "transcript file missing" in " ".join(analysis.reasons).lower()

    def test_existing_transcript_not_flagged_as_missing(self, tmp_path):
        """Should not flag session with existing transcript as missing"""
        transcript_path = tmp_path / "exists.jsonl"
        transcript_path.write_text('{"type": "test"}\n')

        detector = StaleSessionDetector()
        session = {
            "sessionId": "sess-exists001",
            "sessionSource": "startup",
            "startedAt": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
            "lastActivityAt": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
            "environment": {
                "transcriptPath": str(transcript_path)
            }
        }

        analysis = detector.analyze_session(session)

        # Should be ACTIVE since it's recent and transcript exists
        assert analysis.state == SessionState.ACTIVE
        assert "missing" not in " ".join(analysis.reasons).lower()
