#!/usr/bin/env python3
"""
Initialize/update workspace-info.toon on session start.

This hook runs at SessionStart to ensure workspace-info.toon is current:
- Creates the file if it doesn't exist
- Updates git info (commit hash, date)
- Updates modification timestamp
- Records the session that made changes
"""
from workspace_info import run_hook


@run_hook
def main(ws, ctx):
    """Update workspace info on session start."""
    if not ws.exists():
        # Create with workspace name from directory
        ws.create(workspace_name=ctx.project_dir.name)
        ctx.log.info(f"Created workspace-info.toon for {ctx.project_dir.name}")

    ws.update_git_info()
    ws.update_timestamp()
    ws.record_session(ctx)


if __name__ == "__main__":
    main()
