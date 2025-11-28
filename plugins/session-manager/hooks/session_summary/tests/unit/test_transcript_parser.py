"""Tests for TranscriptParser module"""
import pytest
import json
from pathlib import Path
from session_summary.lib.transcript_parser import TranscriptParser, TranscriptStats


class TestParseEmptyTranscript:
    """Test handling of empty or nonexistent transcripts"""

    def test_parse_empty_transcript_file(self, tmp_path):
        """Should return zero stats for empty transcript file"""
        empty_file = tmp_path / "empty.jsonl"
        empty_file.write_text("")

        parser = TranscriptParser(empty_file)
        stats = parser.parse()

        assert stats.tokens_consumed == 0
        assert stats.tool_usage_counts == {}
        assert stats.files_modified == set()
        assert stats.tasks_completed == 0
        assert stats.tasks_failed == 0
        assert stats.subagents_launched == 0
        assert stats.session_ended is False

    def test_parse_nonexistent_transcript(self, tmp_path):
        """Should return zero stats for nonexistent transcript file"""
        nonexistent = tmp_path / "nonexistent.jsonl"

        parser = TranscriptParser(nonexistent)
        stats = parser.parse()

        assert stats.tokens_consumed == 0
        assert stats.tool_usage_counts == {}
        assert stats.files_modified == set()
        assert stats.tasks_completed == 0


class TestExtractTokenUsage:
    """Test token usage extraction from API responses"""

    def test_extract_token_usage_from_api_responses(self, tmp_path):
        """Should sum input_tokens and output_tokens from API response blocks"""
        transcript = tmp_path / "transcript.jsonl"
        transcript.write_text(
            json.dumps({"type": "message", "role": "assistant", "usage": {"input_tokens": 100, "output_tokens": 50}}) + "\n" +
            json.dumps({"type": "message", "role": "assistant", "usage": {"input_tokens": 200, "output_tokens": 75}}) + "\n"
        )

        parser = TranscriptParser(transcript)
        stats = parser.parse()

        assert stats.tokens_consumed == 425  # 100 + 50 + 200 + 75

    def test_extract_multiple_token_blocks(self, tmp_path):
        """Should handle multiple token blocks in transcript"""
        transcript = tmp_path / "transcript.jsonl"
        lines = [
            json.dumps({"type": "message", "role": "user", "content": "Hello"}),
            json.dumps({"type": "message", "role": "assistant", "usage": {"input_tokens": 50, "output_tokens": 25}}),
            json.dumps({"type": "message", "role": "assistant", "usage": {"input_tokens": 100, "output_tokens": 50}}),
        ]
        transcript.write_text("\n".join(lines) + "\n")

        parser = TranscriptParser(transcript)
        stats = parser.parse()

        assert stats.tokens_consumed == 225

    def test_handle_missing_token_fields(self, tmp_path):
        """Should gracefully handle missing token fields"""
        transcript = tmp_path / "transcript.jsonl"
        lines = [
            json.dumps({"type": "message", "role": "assistant", "usage": {"input_tokens": 100}}),
            json.dumps({"type": "message", "role": "assistant", "usage": {"output_tokens": 50}}),
            json.dumps({"type": "message", "role": "assistant"}),
        ]
        transcript.write_text("\n".join(lines) + "\n")

        parser = TranscriptParser(transcript)
        stats = parser.parse()

        assert stats.tokens_consumed == 150  # 100 + 50


class TestExtractToolUsageCounts:
    """Test tool usage counting"""

    def test_extract_tool_usage_counts(self, tmp_path):
        """Should count tool invocations (Read, Write, Edit, Bash, Task, etc.)"""
        transcript = tmp_path / "transcript.jsonl"
        lines = [
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Read", "input": {"file_path": "/test.py"}}
                ]
            }),
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Read", "input": {"file_path": "/test2.py"}},
                    {"type": "tool_use", "name": "Write", "input": {"file_path": "/out.py"}}
                ]
            }),
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Edit", "input": {"file_path": "/edit.py"}}
                ]
            }),
        ]
        transcript.write_text("\n".join(lines) + "\n")

        parser = TranscriptParser(transcript)
        stats = parser.parse()

        assert stats.tool_usage_counts["Read"] == 2
        assert stats.tool_usage_counts["Write"] == 1
        assert stats.tool_usage_counts["Edit"] == 1

    def test_count_bash_tool_usage(self, tmp_path):
        """Should count Bash tool invocations"""
        transcript = tmp_path / "transcript.jsonl"
        lines = [
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Bash", "input": {"command": "ls -la"}}
                ]
            }),
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Bash", "input": {"command": "pwd"}}
                ]
            }),
        ]
        transcript.write_text("\n".join(lines) + "\n")

        parser = TranscriptParser(transcript)
        stats = parser.parse()

        assert stats.tool_usage_counts["Bash"] == 2

    def test_count_diverse_tool_usage(self, tmp_path):
        """Should count various tool types"""
        transcript = tmp_path / "transcript.jsonl"
        lines = [
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Bash"},
                    {"type": "tool_use", "name": "Edit"},
                    {"type": "tool_use", "name": "Read"},
                    {"type": "tool_use", "name": "Grep"},
                    {"type": "tool_use", "name": "Glob"},
                    {"type": "tool_use", "name": "NotebookEdit"},
                ]
            }),
        ]
        transcript.write_text("\n".join(lines) + "\n")

        parser = TranscriptParser(transcript)
        stats = parser.parse()

        assert len(stats.tool_usage_counts) == 6
        assert all(count == 1 for count in stats.tool_usage_counts.values())


class TestExtractFileOperations:
    """Test file operation detection"""

    def test_extract_file_operations(self, tmp_path):
        """Should identify unique files modified via Write/Edit tools"""
        transcript = tmp_path / "transcript.jsonl"
        lines = [
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Write", "input": {"file_path": "/path/to/file1.py"}},
                    {"type": "tool_use", "name": "Write", "input": {"file_path": "/path/to/file1.py"}},  # Duplicate
                ]
            }),
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Edit", "input": {"file_path": "/path/to/file2.py"}},
                ]
            }),
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Read", "input": {"file_path": "/path/to/file3.py"}},  # Should not count
                ]
            }),
        ]
        transcript.write_text("\n".join(lines) + "\n")

        parser = TranscriptParser(transcript)
        stats = parser.parse()

        assert len(stats.files_modified) == 2
        assert "/path/to/file1.py" in stats.files_modified
        assert "/path/to/file2.py" in stats.files_modified
        assert "/path/to/file3.py" not in stats.files_modified

    def test_handle_missing_file_path(self, tmp_path):
        """Should gracefully handle missing file_path in tool input"""
        transcript = tmp_path / "transcript.jsonl"
        lines = [
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Write", "input": {}},
                    {"type": "tool_use", "name": "Edit", "input": {"file_path": "/valid.py"}},
                ]
            }),
        ]
        transcript.write_text("\n".join(lines) + "\n")

        parser = TranscriptParser(transcript)
        stats = parser.parse()

        assert len(stats.files_modified) == 1
        assert "/valid.py" in stats.files_modified


class TestDetectSessionEndMarkers:
    """Test session end detection"""

    def test_detect_session_end_markers(self, tmp_path):
        """Should detect /exit, /logout commands or conversation end patterns"""
        transcript = tmp_path / "transcript.jsonl"
        lines = [
            json.dumps({"type": "message", "role": "user", "content": "Hello"}),
            json.dumps({"type": "message", "role": "assistant", "content": "Got it"}),
            json.dumps({"type": "message", "role": "user", "content": "/exit"}),
        ]
        transcript.write_text("\n".join(lines) + "\n")

        parser = TranscriptParser(transcript)
        stats = parser.parse()

        assert stats.session_ended is True

    def test_detect_logout_command(self, tmp_path):
        """Should detect /logout command"""
        transcript = tmp_path / "transcript.jsonl"
        lines = [
            json.dumps({"type": "message", "role": "user", "content": "Some work"}),
            json.dumps({"type": "message", "role": "user", "content": "/logout"}),
        ]
        transcript.write_text("\n".join(lines) + "\n")

        parser = TranscriptParser(transcript)
        stats = parser.parse()

        assert stats.session_ended is True

    def test_no_session_end_marker(self, tmp_path):
        """Should not detect session end without markers"""
        transcript = tmp_path / "transcript.jsonl"
        lines = [
            json.dumps({"type": "message", "role": "user", "content": "Hello"}),
            json.dumps({"type": "message", "role": "assistant", "content": "Got it"}),
        ]
        transcript.write_text("\n".join(lines) + "\n")

        parser = TranscriptParser(transcript)
        stats = parser.parse()

        assert stats.session_ended is False

    def test_extract_last_activity_timestamp(self, tmp_path):
        """Should extract last activity timestamp from transcript"""
        transcript = tmp_path / "transcript.jsonl"
        lines = [
            json.dumps({"type": "message", "role": "user", "content": "Hello", "timestamp": "2025-11-20T10:00:00Z"}),
            json.dumps({"type": "message", "role": "assistant", "content": "Got it", "timestamp": "2025-11-20T10:00:01Z"}),
        ]
        transcript.write_text("\n".join(lines) + "\n")

        parser = TranscriptParser(transcript)
        stats = parser.parse()

        assert stats.last_activity_timestamp == "2025-11-20T10:00:01Z"


class TestExtractTodoCompletions:
    """Test TodoWrite completion detection"""

    def test_extract_todo_completions(self, tmp_path):
        """Should count TodoWrite items marked as completed"""
        transcript = tmp_path / "transcript.jsonl"
        lines = [
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "name": "TodoWrite",
                        "input": {
                            "todos": [
                                {"content": "Task 1", "status": "completed"},
                                {"content": "Task 2", "status": "in_progress"},
                                {"content": "Task 3", "status": "completed"},
                            ]
                        }
                    }
                ]
            }),
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "name": "TodoWrite",
                        "input": {
                            "todos": [
                                {"content": "Task 4", "status": "completed"},
                            ]
                        }
                    }
                ]
            }),
        ]
        transcript.write_text("\n".join(lines) + "\n")

        parser = TranscriptParser(transcript)
        stats = parser.parse()

        assert stats.tasks_completed == 3

    def test_count_failed_tasks(self, tmp_path):
        """Should count TodoWrite items marked as failed or pending"""
        transcript = tmp_path / "transcript.jsonl"
        lines = [
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "name": "TodoWrite",
                        "input": {
                            "todos": [
                                {"content": "Task 1", "status": "pending"},
                                {"content": "Task 2", "status": "in_progress"},
                            ]
                        }
                    }
                ]
            }),
        ]
        transcript.write_text("\n".join(lines) + "\n")

        parser = TranscriptParser(transcript)
        stats = parser.parse()

        # Pending and in_progress are not failed or completed
        assert stats.tasks_completed == 0
        assert stats.tasks_failed == 0


class TestExtractSubagentLaunches:
    """Test subagent launch detection"""

    def test_extract_subagent_launches(self, tmp_path):
        """Should count Task tool invocations"""
        transcript = tmp_path / "transcript.jsonl"
        lines = [
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Task", "input": {"task": "explore", "prompt": "Find X"}},
                ]
            }),
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Task", "input": {"task": "code-gen", "prompt": "Create Y"}},
                    {"type": "tool_use", "name": "Read", "input": {"file_path": "/test.py"}},
                ]
            }),
        ]
        transcript.write_text("\n".join(lines) + "\n")

        parser = TranscriptParser(transcript)
        stats = parser.parse()

        assert stats.subagents_launched == 2

    def test_no_subagent_launches(self, tmp_path):
        """Should return zero if no Task tools used"""
        transcript = tmp_path / "transcript.jsonl"
        lines = [
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Read", "input": {"file_path": "/test.py"}},
                    {"type": "tool_use", "name": "Write", "input": {"file_path": "/out.py"}},
                ]
            }),
        ]
        transcript.write_text("\n".join(lines) + "\n")

        parser = TranscriptParser(transcript)
        stats = parser.parse()

        assert stats.subagents_launched == 0


class TestHandleMalformedJsonl:
    """Test handling of malformed JSONL"""

    def test_handle_malformed_jsonl(self, tmp_path):
        """Should gracefully skip corrupted lines and continue parsing"""
        transcript = tmp_path / "transcript.jsonl"
        lines = [
            json.dumps({"type": "message", "role": "assistant", "usage": {"input_tokens": 100, "output_tokens": 50}}),
            '{invalid json}',
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Read", "input": {"file_path": "/test.py"}}
                ]
            }),
            '{"incomplete": ',
            json.dumps({"type": "message", "role": "assistant", "usage": {"input_tokens": 50, "output_tokens": 25}}),
        ]
        transcript.write_text("\n".join(lines) + "\n")

        parser = TranscriptParser(transcript)
        stats = parser.parse()

        # Should process valid lines and skip malformed ones
        assert stats.tokens_consumed == 225  # 100 + 50 + 50 + 25
        assert stats.tool_usage_counts["Read"] == 1

    def test_handle_empty_lines(self, tmp_path):
        """Should handle empty lines in JSONL"""
        transcript = tmp_path / "transcript.jsonl"
        lines = [
            json.dumps({"type": "message", "role": "user", "content": "Hello"}),
            "",
            json.dumps({"type": "message", "role": "assistant", "usage": {"input_tokens": 100, "output_tokens": 50}}),
            "",
        ]
        transcript.write_text("\n".join(lines) + "\n")

        parser = TranscriptParser(transcript)
        stats = parser.parse()

        assert stats.tokens_consumed == 150


class TestGitCommitCounting:
    """Test git commit detection in Bash tool invocations"""

    def test_count_git_commit_in_bash_tool(self, tmp_path):
        """Should count git commit commands in Bash tool"""
        transcript = tmp_path / "transcript.jsonl"
        lines = [
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Bash", "input": {"command": "git commit -m 'Initial commit'"}}
                ]
            }),
        ]
        transcript.write_text("\n".join(lines) + "\n")

        parser = TranscriptParser(transcript)
        stats = parser.parse()

        assert stats.git_commits_count == 1

    def test_count_multiple_git_commits(self, tmp_path):
        """Should count multiple git commits in session"""
        transcript = tmp_path / "transcript.jsonl"
        lines = [
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Bash", "input": {"command": "git add . && git commit -m 'First commit'"}}
                ]
            }),
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Bash", "input": {"command": "git commit -m 'Second commit'"}}
                ]
            }),
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Bash", "input": {"command": "git commit --amend -m 'Third commit'"}}
                ]
            }),
        ]
        transcript.write_text("\n".join(lines) + "\n")

        parser = TranscriptParser(transcript)
        stats = parser.parse()

        assert stats.git_commits_count == 3

    def test_ignore_bash_without_commit(self, tmp_path):
        """Should not count non-commit git commands"""
        transcript = tmp_path / "transcript.jsonl"
        lines = [
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Bash", "input": {"command": "git status"}}
                ]
            }),
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Bash", "input": {"command": "git diff"}}
                ]
            }),
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Bash", "input": {"command": "git log"}}
                ]
            }),
        ]
        transcript.write_text("\n".join(lines) + "\n")

        parser = TranscriptParser(transcript)
        stats = parser.parse()

        assert stats.git_commits_count == 0

    def test_detect_various_commit_formats(self, tmp_path):
        """Should detect various git commit command formats"""
        transcript = tmp_path / "transcript.jsonl"
        lines = [
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Bash", "input": {"command": "git commit -m 'msg'"}}
                ]
            }),
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Bash", "input": {"command": "git commit --amend"}}
                ]
            }),
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Bash", "input": {"command": 'git commit -m "$(cat <<\'EOF\'\\nMultiline\\nEOF\\n)"'}}
                ]
            }),
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Bash", "input": {"command": "git add . && git commit -m 'chained'"}}
                ]
            }),
        ]
        transcript.write_text("\n".join(lines) + "\n")

        parser = TranscriptParser(transcript)
        stats = parser.parse()

        assert stats.git_commits_count == 4

    def test_ignore_dry_run_commits(self, tmp_path):
        """Should not count dry-run git commits"""
        transcript = tmp_path / "transcript.jsonl"
        lines = [
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Bash", "input": {"command": "git commit --dry-run -m 'test'"}}
                ]
            }),
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Bash", "input": {"command": "git commit -m 'real commit'"}}
                ]
            }),
        ]
        transcript.write_text("\n".join(lines) + "\n")

        parser = TranscriptParser(transcript)
        stats = parser.parse()

        assert stats.git_commits_count == 1

    def test_no_git_commits_returns_zero(self, tmp_path):
        """Should return zero when no git commits in transcript"""
        transcript = tmp_path / "transcript.jsonl"
        lines = [
            json.dumps({
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Read", "input": {"file_path": "/test.py"}}
                ]
            }),
        ]
        transcript.write_text("\n".join(lines) + "\n")

        parser = TranscriptParser(transcript)
        stats = parser.parse()

        assert stats.git_commits_count == 0


class TestTranscriptStatsDataclass:
    """Test TranscriptStats dataclass"""

    def test_transcript_stats_initialization(self):
        """Should initialize TranscriptStats with all fields"""
        stats = TranscriptStats(
            tokens_consumed=1000,
            tool_usage_counts={"Read": 5, "Write": 3},
            files_modified={"/path/to/file1.py", "/path/to/file2.py"},
            tasks_completed=2,
            tasks_failed=0,
            subagents_launched=1,
            session_ended=True,
            last_activity_timestamp="2025-11-20T10:00:00Z"
        )

        assert stats.tokens_consumed == 1000
        assert stats.tool_usage_counts["Read"] == 5
        assert len(stats.files_modified) == 2
        assert stats.tasks_completed == 2
        assert stats.session_ended is True
