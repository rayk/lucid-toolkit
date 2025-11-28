"""Tests for SessionManager class"""
import pytest
import json
from pathlib import Path
from datetime import datetime, timezone
from session_summary.lib.session_manager import SessionManager


class TestSessionManagerLoad:
    """Tests for SessionManager.load() method"""

    def test_load_existing_file(self, tmp_workspace, sessions_file_empty):
        """Should load existing sessions file"""
        manager = SessionManager(tmp_workspace)
        data = manager.load()
        
        assert "summary" in data
        assert "activeSessions" in data
        assert "recentHistory" in data
        assert isinstance(data["activeSessions"], list)

    def test_load_nonexistent_file(self, tmp_workspace):
        """Should create empty structure if file doesn't exist"""
        manager = SessionManager(tmp_workspace)
        data = manager.load()
        
        assert data["summary"]["activeSessionsCount"] == 0
        assert data["activeSessions"] == []
        assert data["recentHistory"] == []
        assert data["indexByOutcome"] == {}
        assert data["indexByBranch"] == {}

    def test_load_invalid_json(self, tmp_workspace):
        """Should raise error if file contains invalid JSON"""
        sessions_file = tmp_workspace / "status" / "sessions_summary.json"
        sessions_file.write_text("{ invalid json")
        
        manager = SessionManager(tmp_workspace)
        with pytest.raises(ValueError, match="Failed to parse"):
            manager.load()

    def test_load_caches_data(self, tmp_workspace, sessions_file_empty):
        """Should cache loaded data for repeated calls"""
        manager = SessionManager(tmp_workspace)
        
        data1 = manager.load()
        data2 = manager.load()
        
        # Should return the same object (cached)
        assert data1 is data2


class TestSessionManagerSave:
    """Tests for SessionManager.save() method"""

    def test_save_valid_data(self, tmp_workspace):
        """Should save valid data to file"""
        manager = SessionManager(tmp_workspace)
        data = manager.load()  # Get empty structure
        
        # Modify data
        data["summary"]["activeSessionsCount"] = 1
        
        # Save
        manager.save(data)
        
        # Verify file exists and contains data
        sessions_file = tmp_workspace / "status" / "sessions_summary.json"
        assert sessions_file.exists()
        
        with open(sessions_file, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data["summary"]["activeSessionsCount"] == 1

    def test_save_validates_data(self, tmp_workspace):
        """Should validate data before saving"""
        manager = SessionManager(tmp_workspace)
        
        # Invalid data (missing required fields)
        invalid_data = {"summary": {}}
        
        with pytest.raises(ValueError, match="validation failed"):
            manager.save(invalid_data)

    def test_save_atomic(self, tmp_workspace):
        """Should use atomic write (temp file + rename)"""
        manager = SessionManager(tmp_workspace)
        data = manager.load()
        
        manager.save(data)
        
        # Verify no temp file remains
        sessions_dir = tmp_workspace / "status"
        temp_files = list(sessions_dir.glob("*.tmp"))
        assert len(temp_files) == 0

    def test_save_updates_cache(self, tmp_workspace):
        """Should update internal cache after save"""
        manager = SessionManager(tmp_workspace)
        data = manager.load()
        
        data["summary"]["activeSessionsCount"] = 5
        manager.save(data)
        
        # Load again - should return cached version
        loaded = manager.load()
        assert loaded["summary"]["activeSessionsCount"] == 5


class TestSessionManagerAddActiveSession:
    """Tests for SessionManager.add_active_session()"""

    def test_add_session_to_empty(self, tmp_workspace, mock_git_repo):
        """Should add first session to empty activeSessions"""
        from lucid_cli_commons.git_utils import GitInfo
        
        manager = SessionManager(tmp_workspace)
        git_info = GitInfo(mock_git_repo)
        
        manager.add_active_session(
            session_id="sess-test123",
            source="startup",
            mode="default",
            transcript_path="/test.json",
            git_info=git_info
        )
        
        data = manager.load()
        assert len(data["activeSessions"]) == 1
        assert data["activeSessions"][0]["sessionId"] == "sess-test123"
        assert data["summary"]["activeSessionsCount"] == 1

    def test_add_session_persists(self, tmp_workspace, mock_git_repo):
        """Should persist added session to file"""
        from lucid_cli_commons.git_utils import GitInfo
        
        manager = SessionManager(tmp_workspace)
        git_info = GitInfo(mock_git_repo)
        
        manager.add_active_session(
            session_id="sess-test123",
            source="startup",
            mode="default",
            transcript_path="/test.json",
            git_info=git_info
        )
        
        # Verify file was written
        sessions_file = tmp_workspace / "status" / "sessions_summary.json"
        assert sessions_file.exists()


class TestSessionManagerRemoveActiveSession:
    """Tests for SessionManager.remove_active_session()"""

    def test_remove_session_to_history(self, tmp_workspace, mock_git_repo):
        """Should move session from active to history"""
        from lucid_cli_commons.git_utils import GitInfo
        
        manager = SessionManager(tmp_workspace)
        git_info = GitInfo(mock_git_repo)
        
        # Add session
        manager.add_active_session(
            session_id="sess-test123",
            source="startup",
            mode="default",
            transcript_path="/test.json",
            git_info=git_info
        )
        
        # Remove session
        manager.remove_active_session(
            session_id="sess-test123",
            end_reason="logout",
            accomplishments="Test work completed"
        )
        
        data = manager.load()
        assert len(data["activeSessions"]) == 0
        assert len(data["recentHistory"]) == 1
        assert data["recentHistory"][0]["sessionId"] == "sess-test123"
        assert data["recentHistory"][0]["accomplishments"] == "Test work completed"

    def test_remove_nonexistent_session(self, tmp_workspace):
        """Should raise error if session not found"""
        manager = SessionManager(tmp_workspace)
        
        with pytest.raises(ValueError, match="Session not found"):
            manager.remove_active_session(
                session_id="sess-nonexistent",
                end_reason="logout",
                accomplishments="test"
            )
