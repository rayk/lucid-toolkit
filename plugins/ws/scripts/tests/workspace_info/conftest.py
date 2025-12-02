"""
Pytest fixtures for workspace_info tests.
"""
import json
import pytest
from pathlib import Path
from typing import Generator
from io import StringIO
import sys


@pytest.fixture
def fixtures_dir() -> Path:
    """Path to test fixtures directory."""
    return Path(__file__).parent / 'fixtures'


@pytest.fixture
def tmp_workspace(tmp_path: Path) -> Path:
    """Create a temporary workspace with .claude directory."""
    claude_dir = tmp_path / '.claude'
    claude_dir.mkdir()
    return tmp_path


@pytest.fixture
def valid_toon_content(fixtures_dir: Path) -> str:
    """Load valid workspace-info.toon content."""
    return (fixtures_dir / 'valid_workspace_info.toon').read_text()


@pytest.fixture
def minimal_toon_content(fixtures_dir: Path) -> str:
    """Load minimal workspace-info.toon content."""
    return (fixtures_dir / 'minimal_workspace_info.toon').read_text()


@pytest.fixture
def corrupted_toon_content(fixtures_dir: Path) -> str:
    """Load corrupted workspace-info.toon content."""
    return (fixtures_dir / 'corrupted_workspace_info.toon').read_text()


@pytest.fixture
def valid_workspace(tmp_workspace: Path, valid_toon_content: str) -> Path:
    """Create workspace with valid workspace-info.toon."""
    toon_file = tmp_workspace / '.claude' / 'workspace-info.toon'
    toon_file.write_text(valid_toon_content)
    return tmp_workspace


@pytest.fixture
def empty_workspace(tmp_workspace: Path) -> Path:
    """Create workspace without workspace-info.toon."""
    return tmp_workspace


@pytest.fixture
def hook_stdin_session_start(fixtures_dir: Path) -> dict:
    """Load SessionStart hook input."""
    return json.loads((fixtures_dir / 'hook_inputs' / 'session_start.json').read_text())


@pytest.fixture
def hook_stdin_post_tool_use(fixtures_dir: Path) -> dict:
    """Load PostToolUse hook input."""
    return json.loads((fixtures_dir / 'hook_inputs' / 'post_tool_use_edit.json').read_text())


@pytest.fixture
def mock_stdin():
    """Context manager to mock stdin with JSON data."""
    class StdinMocker:
        def __init__(self):
            self._original_stdin = None

        def __call__(self, data: dict) -> 'StdinMocker':
            self._data = data
            return self

        def __enter__(self):
            self._original_stdin = sys.stdin
            sys.stdin = StringIO(json.dumps(self._data))
            return self

        def __exit__(self, *args):
            sys.stdin = self._original_stdin

    return StdinMocker()


@pytest.fixture
def capture_stdout():
    """Context manager to capture stdout."""
    class StdoutCapture:
        def __init__(self):
            self._original_stdout = None
            self.captured = None

        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = StringIO()
            return self

        def __exit__(self, *args):
            self.captured = sys.stdout.getvalue()
            sys.stdout = self._original_stdout

    return StdoutCapture()


@pytest.fixture
def mock_env(monkeypatch):
    """Helper to set environment variables."""
    def _set_env(**kwargs):
        for key, value in kwargs.items():
            if value is None:
                monkeypatch.delenv(key, raising=False)
            else:
                monkeypatch.setenv(key, value)
    return _set_env
