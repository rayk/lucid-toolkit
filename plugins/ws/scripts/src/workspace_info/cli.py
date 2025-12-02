"""
workspace_info.cli - CLI for managing workspace-info.toon files.

This module provides the ws-info command-line interface for:
- Reading and writing workspace-info.toon fields
- Managing focus state
- Updating git metadata
- Initializing new workspace files
"""
import json
import sys
from pathlib import Path

import click

from .core import WorkspaceInfo
from .constants import VALID_ACTION_STATUS


@click.group()
@click.option('--workspace', '-w', type=click.Path(exists=True, path_type=Path),
              help='Workspace root directory (default: auto-detect)')
@click.pass_context
def main(ctx: click.Context, workspace: Path | None) -> None:
    """Manage workspace-info.toon files."""
    ctx.ensure_object(dict)
    ctx.obj['workspace'] = workspace


def get_workspace_info(ctx: click.Context) -> WorkspaceInfo:
    """Get WorkspaceInfo instance from context."""
    workspace = ctx.obj.get('workspace')
    return WorkspaceInfo(workspace)


@main.command()
@click.option('--json', 'as_json', is_flag=True, help='Output as JSON instead of TOON')
@click.pass_context
def read(ctx: click.Context, as_json: bool) -> None:
    """Read entire workspace-info.toon file."""
    ws = get_workspace_info(ctx)

    if not ws.exists():
        click.echo("Error: workspace-info.toon not found", err=True)
        sys.exit(1)

    data = ws.load()

    if as_json:
        click.echo(json.dumps(data, indent=2))
    else:
        from lucid_cli_commons.toon_parser import to_toon
        click.echo(to_toon(data))


@main.command('get')
@click.argument('path')
@click.pass_context
def get_field(ctx: click.Context, path: str) -> None:
    """Get a specific field by path (e.g., focus.name, workspace.version)."""
    ws = get_workspace_info(ctx)

    try:
        value = ws.get(path)
        if value is None:
            click.echo("null")
        elif isinstance(value, (dict, list)):
            click.echo(json.dumps(value, indent=2))
        else:
            click.echo(str(value))
    except FileNotFoundError:
        click.echo("Error: workspace-info.toon not found", err=True)
        sys.exit(1)
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command('set')
@click.argument('path')
@click.argument('value')
@click.pass_context
def set_field(ctx: click.Context, path: str, value: str) -> None:
    """Set a specific field by path."""
    ws = get_workspace_info(ctx)

    # Try to parse value as JSON for complex types
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        # Use as string if not valid JSON
        parsed = value if value != "null" else None

    try:
        ws.set(path, parsed)
        click.echo(f"Set {path} = {value}")
    except FileNotFoundError:
        click.echo("Error: workspace-info.toon not found", err=True)
        sys.exit(1)


@main.command('set-focus')
@click.argument('name')
@click.argument('target')
@click.option('--status', default='ActiveActionStatus',
              type=click.Choice(list(VALID_ACTION_STATUS), case_sensitive=True),
              help='Action status (default: ActiveActionStatus)')
@click.pass_context
def set_focus(ctx: click.Context, name: str, target: str, status: str) -> None:
    """Set the current focus to an outcome."""
    ws = get_workspace_info(ctx)

    try:
        ws.set_focus(name, target, status)
        click.echo(f"Focus set to: {name} ({status})")
    except FileNotFoundError:
        click.echo("Error: workspace-info.toon not found", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command('clear-focus')
@click.pass_context
def clear_focus(ctx: click.Context) -> None:
    """Clear the current focus."""
    ws = get_workspace_info(ctx)

    try:
        ws.clear_focus()
        click.echo("Focus cleared")
    except FileNotFoundError:
        click.echo("Error: workspace-info.toon not found", err=True)
        sys.exit(1)


@main.command('get-focus')
@click.pass_context
def get_focus(ctx: click.Context) -> None:
    """Get the current focus."""
    ws = get_workspace_info(ctx)

    try:
        data = ws.load()
        focus = {
            "name": data.get("focus.name"),
            "target": data.get("focus.target"),
            "actionStatus": data.get("focus.actionStatus")
        }
        click.echo(json.dumps(focus, indent=2))
    except FileNotFoundError:
        click.echo("Error: workspace-info.toon not found", err=True)
        sys.exit(1)


@main.command('update-git')
@click.pass_context
def update_git(ctx: click.Context) -> None:
    """Update workspace.version and workspace.dateModified from git."""
    ws = get_workspace_info(ctx)

    if not ws.exists():
        click.echo("Error: workspace-info.toon not found", err=True)
        sys.exit(1)

    ws.update_git_info()
    click.echo("Git info updated")


@main.command('update-timestamp')
@click.pass_context
def update_timestamp(ctx: click.Context) -> None:
    """Update dateModified to current time."""
    ws = get_workspace_info(ctx)

    if not ws.exists():
        click.echo("Error: workspace-info.toon not found", err=True)
        sys.exit(1)

    ws.update_timestamp()
    click.echo("Timestamp updated")


@main.command('init')
@click.option('--name', required=True, help='Workspace name')
@click.option('--repo', help='Git repository URL (auto-detected if not provided)')
@click.pass_context
def init(ctx: click.Context, name: str, repo: str | None) -> None:
    """Initialize a new workspace-info.toon file."""
    ws = get_workspace_info(ctx)

    if ws.exists():
        click.echo("Error: workspace-info.toon already exists", err=True)
        sys.exit(1)

    ws.create(name, repo)
    click.echo(f"Created workspace-info.toon for '{name}'")


@main.command('validate')
@click.pass_context
def validate(ctx: click.Context) -> None:
    """Validate workspace-info.toon structure."""
    ws = get_workspace_info(ctx)

    if not ws.exists():
        click.echo("Error: workspace-info.toon not found", err=True)
        sys.exit(1)

    try:
        data = ws.load()

        # Check required fields
        required = ["@context", "@type", "workspace.name", "focus.actionStatus"]
        missing = [f for f in required if f not in data]

        if missing:
            click.echo(f"Warning: Missing required fields: {', '.join(missing)}", err=True)
            sys.exit(1)

        # Check action status
        status = data.get("focus.actionStatus")
        if status and status not in VALID_ACTION_STATUS:
            click.echo(f"Warning: Invalid focus.actionStatus: {status}", err=True)
            sys.exit(1)

        click.echo("Validation passed")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
