"""
workspace_info - Python library for managing workspace-info.toon files.

Hook-first design for Claude Code integration.
"""
from .core import WorkspaceInfo
from .hook import HookContext, run_hook

__all__ = ['WorkspaceInfo', 'HookContext', 'run_hook']
__version__ = '0.2.2'
