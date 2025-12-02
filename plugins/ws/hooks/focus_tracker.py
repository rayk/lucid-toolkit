#!/usr/bin/env python3
"""
Update focus when outcome files are edited.

This PostToolUse hook detects edits to outcome files and automatically
updates the focus in workspace-info.toon. This keeps the workspace
state synchronized with what the user is working on.

Triggers on:
- Edit tool calls
- File paths containing "outcomes/" and stages (in-progress, ready, queued)

Updates:
- focus.name = outcome directory name
- focus.target = full outcome path
- focus.actionStatus = ActiveActionStatus
"""
import re
from workspace_info import HookContext, WorkspaceInfo


def main() -> int:
    ctx = HookContext.from_stdin("focus_tracker")

    # Only trigger on Edit tool
    if ctx.tool_name != "Edit":
        return ctx.success()

    # Only track outcome file edits
    file_path = ctx.tool_input.get("file_path", "")
    match = re.search(r'outcomes/(in-progress|ready|queued|blocked)/(\d+(?:\.\d+)?-[^/]+)', file_path)
    if not match:
        return ctx.success()

    stage, outcome_dir = match.groups()

    try:
        ws = WorkspaceInfo(ctx.project_dir)
        if ws.exists():
            ws.set_focus(
                name=outcome_dir,
                target=f"outcomes/{stage}/{outcome_dir}",
                status="ActiveActionStatus"
            )
            ws.record_session(ctx)
            ctx.log.info(f"Focus updated to {outcome_dir}")
    except Exception as e:
        ctx.log.error(f"Failed to update focus: {e}")
        # Don't block Claude on errors

    return ctx.success()


if __name__ == "__main__":
    exit(main())
