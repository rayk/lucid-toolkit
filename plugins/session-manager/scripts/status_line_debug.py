#!/usr/bin/env python3
"""
Debug version of status line that logs the actual input JSON.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Workspace root
workspace_root = Path("/Users/rayk/Projects/lucid_stack")

def main():
    """Capture and log the actual JSON input from Claude Code."""
    try:
        # Read JSON input from Claude Code via stdin
        input_data = json.loads(sys.stdin.read())

        # Log to file
        log_file = workspace_root / ".claude/temp/statusline_input.json"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "input": input_data
            }, f, indent=2)

        # Output simple status line
        print(f"Logged input to {log_file}")

    except Exception as e:
        print(f"Debug error: {type(e).__name__}")


if __name__ == "__main__":
    main()
