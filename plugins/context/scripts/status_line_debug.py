#!/usr/bin/env python3
"""
Debug version of status line that logs the actual input JSON.
Use this to understand what data Claude Code provides to status line scripts.
"""

import sys
import json
from pathlib import Path
from datetime import datetime


def main():
    """Capture and log the actual JSON input from Claude Code."""
    try:
        input_data = json.loads(sys.stdin.read())

        # Log to temp file
        log_file = Path.home() / ".claude/temp/statusline_input.json"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "input": input_data
            }, f, indent=2)

        print(f"Logged input to {log_file}")

    except Exception as e:
        print(f"Debug error: {type(e).__name__}")


if __name__ == "__main__":
    main()
