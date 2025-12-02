"""Tests for workspace_info CLI."""
import json
import pytest
from click.testing import CliRunner
from pathlib import Path

from workspace_info.cli import main


@pytest.fixture
def runner():
    """Create Click test runner."""
    return CliRunner()


@pytest.fixture
def workspace_with_file(tmp_path, valid_toon_content):
    """Create workspace with valid workspace-info.toon."""
    claude_dir = tmp_path / '.claude'
    claude_dir.mkdir()
    toon_file = claude_dir / 'workspace-info.toon'
    toon_file.write_text(valid_toon_content)
    return tmp_path


class TestReadCommand:
    """Tests for read command."""

    def test_read_outputs_toon(self, runner, workspace_with_file):
        result = runner.invoke(main, ['--workspace', str(workspace_with_file), 'read'])
        assert result.exit_code == 0
        assert '@context' in result.output or 'schema.org' in result.output

    def test_read_json_outputs_json(self, runner, workspace_with_file):
        result = runner.invoke(main, ['--workspace', str(workspace_with_file), 'read', '--json'])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert '@context' in data or 'workspace.name' in data

    def test_read_missing_file(self, runner, tmp_path):
        claude_dir = tmp_path / '.claude'
        claude_dir.mkdir()
        result = runner.invoke(main, ['--workspace', str(tmp_path), 'read'])
        assert result.exit_code == 1
        assert 'not found' in result.output.lower()


class TestGetCommand:
    """Tests for get command."""

    def test_get_existing_field(self, runner, workspace_with_file):
        result = runner.invoke(main, ['--workspace', str(workspace_with_file), 'get', 'focus.name'])
        assert result.exit_code == 0

    def test_get_missing_field(self, runner, workspace_with_file):
        result = runner.invoke(main, ['--workspace', str(workspace_with_file), 'get', 'nonexistent.field'])
        assert result.exit_code == 1
        assert 'error' in result.output.lower()


class TestSetCommand:
    """Tests for set command."""

    def test_set_field(self, runner, workspace_with_file):
        result = runner.invoke(main, ['--workspace', str(workspace_with_file), 'set', 'focus.name', 'new-outcome'])
        assert result.exit_code == 0
        assert 'Set' in result.output


class TestFocusCommands:
    """Tests for focus management commands."""

    def test_set_focus(self, runner, workspace_with_file):
        result = runner.invoke(main, [
            '--workspace', str(workspace_with_file),
            'set-focus', 'my-outcome', 'outcomes/in-progress/001-my-outcome'
        ])
        assert result.exit_code == 0
        assert 'Focus set' in result.output

    def test_set_focus_with_status(self, runner, workspace_with_file):
        result = runner.invoke(main, [
            '--workspace', str(workspace_with_file),
            'set-focus', 'my-outcome', 'outcomes/completed/001',
            '--status', 'CompletedActionStatus'
        ])
        assert result.exit_code == 0
        assert 'CompletedActionStatus' in result.output

    def test_clear_focus(self, runner, workspace_with_file):
        result = runner.invoke(main, ['--workspace', str(workspace_with_file), 'clear-focus'])
        assert result.exit_code == 0
        assert 'cleared' in result.output.lower()

    def test_get_focus(self, runner, workspace_with_file):
        result = runner.invoke(main, ['--workspace', str(workspace_with_file), 'get-focus'])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert 'name' in data
        assert 'actionStatus' in data


class TestUpdateCommands:
    """Tests for update commands."""

    def test_update_git(self, runner, workspace_with_file):
        result = runner.invoke(main, ['--workspace', str(workspace_with_file), 'update-git'])
        assert result.exit_code == 0
        assert 'updated' in result.output.lower()

    def test_update_timestamp(self, runner, workspace_with_file):
        result = runner.invoke(main, ['--workspace', str(workspace_with_file), 'update-timestamp'])
        assert result.exit_code == 0
        assert 'updated' in result.output.lower()


class TestInitCommand:
    """Tests for init command."""

    def test_init_creates_file(self, runner, tmp_path):
        claude_dir = tmp_path / '.claude'
        claude_dir.mkdir()
        result = runner.invoke(main, ['--workspace', str(tmp_path), 'init', '--name', 'test-workspace'])
        assert result.exit_code == 0
        assert 'Created' in result.output
        assert (claude_dir / 'workspace-info.toon').exists()

    def test_init_fails_if_exists(self, runner, workspace_with_file):
        result = runner.invoke(main, ['--workspace', str(workspace_with_file), 'init', '--name', 'test'])
        assert result.exit_code == 1
        assert 'already exists' in result.output


class TestValidateCommand:
    """Tests for validate command."""

    def test_validate_valid_file(self, runner, workspace_with_file):
        result = runner.invoke(main, ['--workspace', str(workspace_with_file), 'validate'])
        assert result.exit_code == 0
        assert 'passed' in result.output.lower()
