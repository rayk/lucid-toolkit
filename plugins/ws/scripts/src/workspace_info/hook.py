"""
workspace_info.hook - Hook integration for Claude Code.

This module provides utilities for writing Claude Code hooks that interact
with workspace-info.toon files.

Key Classes:
    HookContext: Parses and provides access to hook invocation context

Key Functions:
    run_hook: Decorator for minimal-boilerplate hook functions

Claude Code Hook Contract:
    Hooks receive:
    - stdin: JSON with session_id, transcript_path, cwd, hook_event_name, etc.
    - environment: CLAUDE_PROJECT_DIR, CLAUDE_CODE_REMOTE, CLAUDE_WORKSPACE_ROOT

    Hooks respond:
    - stdout: JSON with continue, stopReason, systemMessage, additionalContext
    - stderr: Diagnostic logging
    - Exit codes: 0=success, 2=blocking, other=warning

Example Hook:
    #!/usr/bin/env python3
    '''Update workspace-info.toon on session start.'''
    from workspace_info import HookContext, WorkspaceInfo

    def main():
        ctx = HookContext.from_stdin()
        ws = WorkspaceInfo(ctx.project_dir)

        if ws.exists():
            ws.update_git_info()
            ws.update_timestamp()
            ws.record_session(ctx)  # Track which session modified the file

        return ctx.success()

    if __name__ == "__main__":
        exit(main())

See Also:
    - workspace_info.core: WorkspaceInfo class
    - Claude Code hooks documentation: https://docs.anthropic.com/claude-code/hooks
"""

from __future__ import annotations

import json
import logging
import os
import sys
from dataclasses import dataclass, field
from functools import wraps
from pathlib import Path
from typing import Any, Callable, NoReturn, TYPE_CHECKING

if TYPE_CHECKING:
    from .core import WorkspaceInfo


def _setup_logger(name: str) -> logging.Logger:
    """Create logger that writes to stderr with hook-style prefix."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter(f'[{name}] %(levelname)s: %(message)s'))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def _read_stdin() -> dict[str, Any]:
    """Read and parse JSON from stdin, returning empty dict on failure."""
    try:
        text = sys.stdin.read()
        if not text.strip():
            return {}
        return json.loads(text)
    except (json.JSONDecodeError, IOError):
        return {}


def _write_response(data: dict[str, Any]) -> None:
    """Write JSON response to stdout."""
    print(json.dumps(data))


@dataclass
class HookContext:
    """Context from Claude Code hook invocation."""

    # From stdin JSON
    session_id: str | None = None
    transcript_path: Path | None = None
    cwd: Path = field(default_factory=Path.cwd)
    hook_event: str | None = None
    tool_name: str | None = None
    tool_input: dict = field(default_factory=dict)

    # From environment
    project_dir: Path = field(default_factory=Path.cwd)
    is_remote: bool = False

    # Logging
    log: logging.Logger = field(default=None)
    _hook_name: str = field(default="workspace_info")

    @classmethod
    def from_stdin(cls, hook_name: str = "workspace_info") -> 'HookContext':
        """Parse stdin JSON and environment into HookContext."""
        data = _read_stdin()

        # Determine project directory (priority order)
        project_dir = (
            os.environ.get('CLAUDE_PROJECT_DIR') or
            os.environ.get('CLAUDE_WORKSPACE_ROOT') or
            data.get('cwd') or
            os.getcwd()
        )

        return cls(
            session_id=data.get('session_id'),
            transcript_path=Path(data['transcript_path']) if data.get('transcript_path') else None,
            cwd=Path(data.get('cwd', os.getcwd())),
            hook_event=data.get('hook_event_name'),
            tool_name=data.get('tool_name'),
            tool_input=data.get('tool_input') or {},
            project_dir=Path(project_dir),
            is_remote=os.environ.get('CLAUDE_CODE_REMOTE') == 'true',
            log=_setup_logger(hook_name),
            _hook_name=hook_name,
        )

    def success(self, context: str | None = None) -> int:
        """Return success (exit code 0)."""
        response = {"continue": True}
        if context:
            response["additionalContext"] = context
        _write_response(response)
        return 0

    def block(self, reason: str) -> int:
        """Return blocking error (exit code 2)."""
        self.log.error(f"BLOCKED: {reason}")
        _write_response({"continue": False, "stopReason": reason})
        return 2

    def warn(self, message: str) -> int:
        """Return warning (exit code 1, non-blocking)."""
        self.log.warning(message)
        _write_response({"continue": True, "systemMessage": message})
        return 1


def run_hook(func: Callable[['WorkspaceInfo', HookContext], int | None]) -> Callable[[], NoReturn]:
    """
    Decorator for hook main functions.

    Handles context parsing, error handling, and response formatting.
    Always calls sys.exit() - never returns normally.
    """
    @wraps(func)
    def wrapper() -> NoReturn:
        from .core import WorkspaceInfo

        ctx = HookContext.from_stdin(hook_name=func.__name__)

        try:
            ws = WorkspaceInfo(ctx.project_dir)
            result = func(ws, ctx)

            # If function returned an exit code, use it
            if isinstance(result, int):
                sys.exit(result)

            # Otherwise, success
            sys.exit(ctx.success())

        except Exception as e:
            ctx.log.error(f"Unexpected error: {e}")
            # Don't block Claude on errors
            sys.exit(ctx.success())

    return wrapper
