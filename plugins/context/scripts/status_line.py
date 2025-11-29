#!/usr/bin/env python3
"""
Status line script for Claude Code context plugin.
Displays session-aware information including focused outcomes, token usage, and git status.

Usage: Configure in Claude Code settings as the status line script.
Input: JSON from stdin with session context
Output: Multi-line status display
"""

import sys
import json
import subprocess
from pathlib import Path


# ANSI color codes matching Claude Code CLI theme
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Primary colors
    CYAN = "\033[36m"
    BLUE = "\033[34m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    MAGENTA = "\033[35m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"

    # Bright variants
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_GREEN = "\033[92m"


# Icons for status line labels
class Icons:
    FOCUS = ">"
    SESSION = "T"
    EFFICIENCY = "%"
    BRANCH = "B"
    TREE = "W"
    CHANGES = "M"
    CWD = "D"
    UP = "^"
    DOWN = "v"
    CACHE = "$"
    DATABASE = "C"
    CONTEXT = "X"
    COMMITS = "#"
    LINES = "L"
    HIT = "H"
    ROI = "R"


def load_sessions_summary(workspace_root: Path):
    """Load sessions summary data."""
    try:
        summary_file = workspace_root / "status/sessions_summary.json"
        if summary_file.exists():
            with open(summary_file) as f:
                return json.load(f)
    except Exception:
        pass
    return None


def get_focused_outcome(context_data):
    """Get currently focused outcome name."""
    if not context_data:
        return None
    outcome = context_data.get("summary", {}).get("currentFocusedOutcome", "No Focus Set")
    return outcome if outcome != "No Focus Set" else None


def get_git_branch(cwd: Path):
    """Get current git branch name."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=1,
            cwd=cwd
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


def get_git_worktree_name(cwd: Path):
    """Get current git worktree name."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
            timeout=1,
            cwd=cwd
        )
        if result.returncode == 0:
            git_dir = result.stdout.strip()
            if "/worktrees/" in git_dir:
                worktree_name = git_dir.split("/worktrees/")[-1]
                return worktree_name
            return "none"
    except Exception:
        pass
    return "none"


def get_git_changes(cwd: Path):
    """Get count of changed files."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=1,
            cwd=cwd
        )
        if result.returncode == 0:
            lines = [line for line in result.stdout.strip().split('\n') if line]
            return len(lines) if lines else 0
    except Exception:
        pass
    return 0


def get_commits_today(cwd: Path):
    """Get count of commits in the last 24 hours."""
    try:
        result = subprocess.run(
            ["git", "log", "--since=1 day ago", "--format=%h"],
            capture_output=True,
            text=True,
            timeout=1,
            cwd=cwd
        )
        if result.returncode == 0:
            commits = [line for line in result.stdout.strip().split('\n') if line]
            return len(commits)
    except Exception:
        pass
    return 0


def format_duration(ms):
    """Format milliseconds into human-readable duration."""
    if ms < 60000:
        return f"{int(ms/1000)}s"
    elif ms < 3600000:
        return f"{int(ms/60000)}m"
    else:
        hours = int(ms/3600000)
        minutes = int((ms % 3600000)/60000)
        return f"{hours}h{minutes}m"


def format_tokens(count):
    """Format token count to human-readable format."""
    if count >= 1_000_000:
        return f"{count/1_000_000:.1f}M"
    elif count >= 1_000:
        return f"{count/1_000:.1f}k"
    else:
        return str(count)


def parse_transcript_tokens(transcript_path):
    """Parse transcript file to extract token usage."""
    try:
        if not Path(transcript_path).exists():
            return None

        input_tokens = 0
        output_tokens = 0
        cache_read_tokens = 0
        cache_creation_tokens = 0
        context_length = 0
        most_recent_timestamp = None

        with open(transcript_path, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    usage = data.get("message", {}).get("usage", {})

                    if usage:
                        input_tokens += usage.get("input_tokens", 0)
                        output_tokens += usage.get("output_tokens", 0)
                        cache_read_tokens += usage.get("cache_read_input_tokens", 0)
                        cache_creation_tokens += usage.get("cache_creation_input_tokens", 0)

                        is_sidechain = data.get("isSidechain", False)
                        timestamp = data.get("timestamp")
                        is_error = data.get("isApiErrorMessage", False)

                        if not is_sidechain and timestamp and not is_error:
                            if most_recent_timestamp is None or timestamp > most_recent_timestamp:
                                most_recent_timestamp = timestamp
                                context_length = (
                                    usage.get("input_tokens", 0) +
                                    usage.get("cache_read_input_tokens", 0) +
                                    usage.get("cache_creation_input_tokens", 0)
                                )
                except (json.JSONDecodeError, AttributeError):
                    continue

        total_cache = cache_read_tokens + cache_creation_tokens

        return {
            "input": input_tokens,
            "output": output_tokens,
            "cache": total_cache,
            "total": input_tokens + output_tokens + total_cache,
            "context": context_length,
            "total_cached": cache_creation_tokens
        }
    except Exception:
        return None


def main():
    """Generate status line from Claude Code session context."""
    try:
        input_data = json.loads(sys.stdin.read())

        cost_data = input_data.get("cost", {})
        total_duration_ms = cost_data.get("total_duration_ms", 0)
        total_api_duration_ms = cost_data.get("total_api_duration_ms", 0)

        workspace = input_data.get("workspace", {})
        cwd = workspace.get("current_dir", "/unknown")
        cwd_path = Path(cwd)

        transcript_path = input_data.get("transcript_path", "")
        tokens = parse_transcript_tokens(transcript_path) if transcript_path else None

        # Try to load sessions summary from workspace
        context_data = load_sessions_summary(cwd_path)

        focused = get_focused_outcome(context_data)
        focus_text = focused if focused else "No Focus Set"

        session_time = format_duration(total_duration_ms) if total_duration_ms > 0 else "0s"

        if total_duration_ms > 0 and total_api_duration_ms > 0:
            efficiency = int((total_api_duration_ms / total_duration_ms) * 100)
            efficiency_text = f"{efficiency}%"
        else:
            efficiency_text = "0%"

        git_branch = get_git_branch(cwd_path)
        git_worktree = get_git_worktree_name(cwd_path)
        git_changes = get_git_changes(cwd_path)
        commits_today = get_commits_today(cwd_path)

        lines_added = cost_data.get("total_lines_added", 0)
        lines_removed = cost_data.get("total_lines_removed", 0)

        # Build line 1: Focus | Context | Cache stats | Up Down | (Time Efficiency)
        focus_color = Colors.MAGENTA if focused else Colors.GRAY
        efficiency_num = int(efficiency_text.rstrip('%')) if efficiency_text != "0%" else 0
        efficiency_color = Colors.GREEN if efficiency_num >= 30 else Colors.YELLOW if efficiency_num > 0 else Colors.GRAY

        line1_parts = [
            f"{Colors.CYAN}{Icons.FOCUS}{Colors.RESET} {focus_color}{focus_text}{Colors.RESET}"
        ]

        if tokens:
            context_tokens = format_tokens(tokens["context"])
            total_cached = format_tokens(tokens["total_cached"])
            cache_tokens = tokens["cache"]
            up_tokens = format_tokens(tokens["input"])
            down_tokens = format_tokens(tokens["output"])

            total_input = tokens["input"] + cache_tokens
            cache_hit_rate = int((cache_tokens / total_input * 100)) if total_input > 0 else 0
            cache_usage = int((cache_tokens / tokens["total_cached"] * 100)) if tokens["total_cached"] > 0 else 0

            line1_parts.append(
                f"{Colors.CYAN}{Icons.CONTEXT}{Colors.RESET}{Colors.BRIGHT_BLUE}{context_tokens}{Colors.RESET}"
            )

            line1_parts.append(
                f"{Colors.CYAN}{Icons.DATABASE}{Colors.RESET}{Colors.MAGENTA}{total_cached}{Colors.RESET}"
                f"{Colors.GRAY}({Colors.CYAN}{Icons.HIT} {Colors.GREEN}{cache_hit_rate}%"
                f"{Colors.GRAY} / {Colors.CYAN}{Icons.ROI} {Colors.YELLOW}{cache_usage}%{Colors.GRAY}){Colors.RESET}"
            )

            line1_parts.append(
                f"{Colors.CYAN}{Icons.UP}{Colors.RESET}{Colors.BLUE}{up_tokens}{Colors.RESET} "
                f"{Colors.CYAN}{Icons.DOWN}{Colors.RESET}{Colors.GREEN}{down_tokens}{Colors.RESET}"
            )

        line1_parts.append(
            f"({Colors.CYAN}{Icons.SESSION}{Colors.RESET} {Colors.BLUE}{session_time}{Colors.RESET} "
            f"{Colors.CYAN}{Icons.EFFICIENCY}{Colors.RESET} {efficiency_color}{efficiency_text}{Colors.RESET})"
        )

        line1 = f" {Colors.GRAY}|{Colors.RESET} ".join(line1_parts)

        # Line 2: Branch, Tree, Lines changed, Commits
        tree_color = Colors.BRIGHT_CYAN if git_worktree != "none" else Colors.GRAY
        lines_display = f"+{lines_added}/-{lines_removed}"
        lines_color = Colors.GREEN if lines_added > lines_removed else Colors.YELLOW if lines_added > 0 else Colors.GRAY

        line2 = (
            f"{Colors.CYAN}{Icons.BRANCH}{Colors.RESET} {Colors.BLUE}{git_branch}{Colors.RESET} "
            f"{Colors.GRAY}|{Colors.RESET} "
            f"{Colors.CYAN}{Icons.TREE}{Colors.RESET} {tree_color}{git_worktree}{Colors.RESET} "
            f"{Colors.GRAY}|{Colors.RESET} "
            f"{Colors.CYAN}{Icons.LINES}{Colors.RESET} {lines_color}{lines_display}{Colors.RESET} "
            f"{Colors.GRAY}|{Colors.RESET} "
            f"{Colors.CYAN}{Icons.COMMITS}{Colors.RESET} {Colors.MAGENTA}{commits_today}{Colors.RESET}"
        )

        # Line 3: Current directory
        line3 = f"{Colors.CYAN}{Icons.CWD}{Colors.RESET} {Colors.WHITE}{cwd}{Colors.RESET}"

        print(f"{line1}\n{line2}\n{line3}")

    except json.JSONDecodeError:
        print("context\nNo data\nNo cwd")
    except Exception as e:
        print(f"context\nerr: {type(e).__name__}\nNo cwd")


if __name__ == "__main__":
    main()
