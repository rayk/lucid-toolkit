"""
Unit tests for accomplishments generation module.

Tests the generation of meaningful accomplishments from session data.
Following TDD approach - tests written first, then implementation.
"""
import pytest
from session_summary.lib.accomplishments import generate_accomplishments
from session_summary.lib.transcript_parser import TranscriptStats
from lucid_cli_commons.git_utils import GitInfo
from unittest.mock import Mock, PropertyMock


class TestAccomplishmentsGeneration:
    """Test suite for accomplishments generation."""

    def test_generate_from_git_commit_message(self):
        """Git commit message should be included in accomplishments."""
        # Arrange
        stats = TranscriptStats()
        mock_git = Mock(spec=GitInfo)
        type(mock_git).last_commit_message = PropertyMock(
            return_value="feat: add authentication system"
        )

        # Act
        result = generate_accomplishments(stats, mock_git)

        # Assert
        assert "feat: add authentication system" in result

    def test_generate_from_tasks_completed(self):
        """Task completion count should be included in accomplishments."""
        # Arrange
        stats = TranscriptStats(tasks_completed=5)

        # Act
        result = generate_accomplishments(stats)

        # Assert
        assert "Completed 5 tasks" in result

    def test_generate_from_files_modified(self):
        """File modification count should be included in accomplishments."""
        # Arrange
        stats = TranscriptStats()
        stats.files_modified = {
            "/path/to/file1.py",
            "/path/to/file2.py",
            "/path/to/file3.py",
            "/path/to/file4.py",
            "/path/to/file5.py",
            "/path/to/file6.py",
            "/path/to/file7.py",
            "/path/to/file8.py"
        }

        # Act
        result = generate_accomplishments(stats)

        # Assert
        assert "Modified 8 files" in result

    def test_generate_combined(self):
        """All sources should be combined into single accomplishments string."""
        # Arrange
        stats = TranscriptStats(tasks_completed=3)
        stats.files_modified = {
            "/path/to/file1.py",
            "/path/to/file2.py",
            "/path/to/file3.py",
            "/path/to/file4.py",
            "/path/to/file5.py"
        }
        mock_git = Mock(spec=GitInfo)
        type(mock_git).last_commit_message = PropertyMock(
            return_value="feat: implement auth system"
        )

        # Act
        result = generate_accomplishments(stats, mock_git)

        # Assert
        assert "feat: implement auth system" in result
        assert "Completed 3 tasks" in result
        assert "Modified 5 files" in result
        # Should be semicolon-separated
        assert ";" in result

    def test_generate_empty_when_no_data(self):
        """Should return default message when no meaningful data available."""
        # Arrange
        stats = TranscriptStats()

        # Act
        result = generate_accomplishments(stats)

        # Assert
        assert result == "Session completed"

    def test_generate_with_subagents(self):
        """Should include subagent launch count when present."""
        # Arrange
        stats = TranscriptStats(subagents_launched=3, tasks_completed=2)

        # Act
        result = generate_accomplishments(stats)

        # Assert
        assert "Launched 3 subagents" in result
        assert "Completed 2 tasks" in result

    def test_generate_with_multiline_commit_message(self):
        """Should only use first line (subject) of multi-line commit message."""
        # Arrange
        stats = TranscriptStats()
        mock_git = Mock(spec=GitInfo)
        type(mock_git).last_commit_message = PropertyMock(
            return_value="feat: add authentication\n\nDetailed description here\nWith multiple lines"
        )

        # Act
        result = generate_accomplishments(stats, mock_git)

        # Assert
        assert "feat: add authentication" in result
        assert "Detailed description" not in result
        assert "multiple lines" not in result

    def test_generate_with_git_info_but_no_commit(self):
        """Should handle GitInfo with no commit message gracefully."""
        # Arrange
        stats = TranscriptStats(tasks_completed=1)
        mock_git = Mock(spec=GitInfo)
        type(mock_git).last_commit_message = PropertyMock(return_value=None)

        # Act
        result = generate_accomplishments(stats)

        # Assert
        assert "Completed 1 task" in result
        # Should not crash or include None

    def test_generate_with_empty_commit_message(self):
        """Should handle empty string commit message gracefully."""
        # Arrange
        stats = TranscriptStats(tasks_completed=2)
        mock_git = Mock(spec=GitInfo)
        type(mock_git).last_commit_message = PropertyMock(return_value="")

        # Act
        result = generate_accomplishments(stats)

        # Assert
        assert "Completed 2 tasks" in result
        # Should not include empty commit message

    def test_generate_with_only_files_modified(self):
        """Should work with only file modifications."""
        # Arrange
        stats = TranscriptStats()
        stats.files_modified = {"/path/to/file1.py", "/path/to/file2.py"}

        # Act
        result = generate_accomplishments(stats)

        # Assert
        assert "Modified 2 files" in result

    def test_generate_with_zero_tasks_completed(self):
        """Should not mention tasks when zero tasks completed."""
        # Arrange
        stats = TranscriptStats(tasks_completed=0)
        stats.files_modified = {"/path/to/file1.py"}

        # Act
        result = generate_accomplishments(stats)

        # Assert
        assert "tasks" not in result.lower()
        assert "Modified 1 file" in result

    def test_generate_singular_vs_plural(self):
        """Should use correct singular/plural forms."""
        # Test single task
        stats = TranscriptStats(tasks_completed=1)
        result = generate_accomplishments(stats)
        assert "Completed 1 task" in result

        # Test single file
        stats = TranscriptStats()
        stats.files_modified = {"/path/to/file.py"}
        result = generate_accomplishments(stats)
        assert "Modified 1 file" in result

        # Test single subagent
        stats = TranscriptStats(subagents_launched=1)
        result = generate_accomplishments(stats)
        assert "Launched 1 subagent" in result
