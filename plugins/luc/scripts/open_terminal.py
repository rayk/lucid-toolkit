#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# ///
"""Open a new Warp terminal tab with optional name and command."""

import argparse
import subprocess


def open_warp_tab(name: str | None = None, command: str | None = None, directory: str | None = None) -> None:
    """Open a new Warp terminal tab.

    Args:
        name: Optional name for the tab
        command: Optional command to run in the tab
        directory: Optional directory to change to
    """
    script_parts = [
        'tell application "Warp" to activate',
        'delay 0.3',
        'tell application "System Events"',
        '    tell process "Warp"',
        '        keystroke "t" using {command down}',
        '        delay 0.5',
    ]

    if name:
        script_parts.extend([
            '        click menu item "Rename the Current Tab" of menu "Tab" of menu bar 1',
            '        delay 0.3',
            f'        keystroke "{name}"',
            '        delay 0.2',
            '        keystroke return',
            '        delay 0.3',
        ])

    if directory:
        script_parts.extend([
            f'        keystroke "cd {directory}"',
            '        delay 0.2',
            '        keystroke return',
            '        delay 0.3',
        ])

    if command:
        script_parts.extend([
            f'        keystroke "{command}"',
            '        delay 0.2',
            '        keystroke return',
        ])

    script_parts.extend([
        '    end tell',
        'end tell',
    ])

    script = '\n'.join(script_parts)
    subprocess.run(['osascript', '-e', script], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description='Open a new Warp terminal tab')
    parser.add_argument('-n', '--name', help='Name for the tab')
    parser.add_argument('-c', '--command', help='Command to run in the tab')
    parser.add_argument('-d', '--directory', help='Directory to change to')

    args = parser.parse_args()
    open_warp_tab(name=args.name, command=args.command, directory=args.directory)


if __name__ == '__main__':
    main()
