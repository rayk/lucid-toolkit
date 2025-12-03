#!/usr/bin/env python3
"""
Mark capability indexes as stale when capability files are modified.

This PostToolUse hook detects edits to capability-statement.md files and
marks the workspace indexes as needing regeneration. This is a safety net
for manual edits that bypass the cap/* commands.

Triggers on:
- Edit or Write tool calls
- File paths matching capabilities/*/capability-statement.md

Updates:
- Sets indexStatus.capabilities to "stale" in workspace-info.toon
- Logs which capability was modified

Note: Actual index regeneration is handled by:
1. The capability-index-sync skill (invoked by cap/* commands)
2. The cap/list.md command (checks freshness before listing)
"""
import re
from workspace_info import HookContext, WorkspaceInfo


def main() -> int:
    ctx = HookContext.from_stdin("capability_sync")

    # Only trigger on Edit or Write tool
    if ctx.tool_name not in ("Edit", "Write"):
        return ctx.success()

    # Only track capability file changes
    file_path = ctx.tool_input.get("file_path", "")
    match = re.search(r'capabilities/([^/]+)/capability-statement\.md$', file_path)
    if not match:
        return ctx.success()

    capability_id = match.group(1)

    try:
        ws = WorkspaceInfo(ctx.project_dir)
        if ws.exists():
            ws.mark_indexes_stale("capabilities", capability_id)
            ctx.log.info(f"Marked capability indexes stale: {capability_id} modified")
    except Exception as e:
        ctx.log.error(f"Failed to mark indexes stale: {e}")
        # Don't block Claude on errors

    return ctx.success()


if __name__ == "__main__":
    exit(main())
