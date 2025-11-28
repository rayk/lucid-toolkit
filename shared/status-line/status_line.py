#!/usr/bin/env python3
"""
Status line script for lucid_stack workspace.
Displays session-aware information including focused outcomes and active session count.
"""

import sys
import json
import subprocess
from pathlib import Path

# Workspace root
workspace_root = Path("/Users/rayk/Projects/lucid_stack")

# Add to path for SessionManager import
sys.path.insert(0, str(workspace_root / ".claude/shared/hook_scripts"))

# ANSI color codes matching Claude Code CLI theme
class Colors:
    # Claude Code theme colors
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Primary colors
    CYAN = "\033[36m"      # Labels/keys
    BLUE = "\033[34m"      # Primary info
    GREEN = "\033[32m"     # Success/positive states
    YELLOW = "\033[33m"    # Warnings/attention
    RED = "\033[31m"       # Errors/critical
    MAGENTA = "\033[35m"   # Special/focus
    WHITE = "\033[37m"     # Standard text
    GRAY = "\033[90m"      # Dim/secondary

    # Bright variants
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_GREEN = "\033[92m"

# Icons for status line labels
class Icons:
    FOCUS = "🎯"        # Focus/target
    SESSION = "⏱️"      # Session time
    EFFICIENCY = "⚡"   # Efficiency/performance
    BRANCH = "🌿"       # Git branch
    TREE = "🌳"         # Git worktree
    CHANGES = "📝"      # File changes
    CWD = "📂"          # Current directory
    UP = "↑"            # Tokens sent up to API (thin arrow)
    DOWN = "↓"          # Tokens received down from API (thin arrow)
    CACHE = "💾"        # Cached tokens
    DATABASE = "⚙️ "    # Total cached tokens (gear with space)
    CONTEXT = "🧠 "     # Context window usage (brain with space)
    COMMITS = "🔨"      # Commits today
    LINES = "±"         # Lines changed (plus/minus)
    HIT = "◎"           # Cache hit rate (target/bullseye)
    ROI = "⤴"           # Cache ROI (curved arrow up - return on investment)


def load_session_summary():
    """Load session summary data."""
    try:
        summary_file = workspace_root / "status/sessions_summary.json"
        if summary_file.exists():
            with open(summary_file) as f:
                return json.load(f)
    except Exception:
        pass
    return None


def get_focused_outcome(session_data):
    """Get currently focused outcome name."""
    if not session_data:
        return None
    outcome = session_data.get("summary", {}).get("currentFocusedOutcome", "No Focus Set")
    return outcome if outcome != "No Focus Set" else None


def get_git_branch():
    """Get current git branch name."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=1,
            cwd=workspace_root
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


def get_git_worktree_name():
    """Get current git worktree name."""
    try:
        # Check if we're in a worktree
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
            timeout=1,
            cwd=workspace_root
        )
        if result.returncode == 0:
            git_dir = result.stdout.strip()
            # If git-dir ends with .git/worktrees/<name>, extract the name
            if "/worktrees/" in git_dir:
                worktree_name = git_dir.split("/worktrees/")[-1]
                return worktree_name
            # Otherwise, not in a worktree
            return "none"
    except Exception:
        pass
    return "none"


def get_git_changes():
    """Get count of changed files."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=1,
            cwd=workspace_root
        )
        if result.returncode == 0:
            lines = [l for l in result.stdout.strip().split('\n') if l]
            return len(lines) if lines else 0
    except Exception:
        pass
    return 0


def get_commits_today():
    """Get count of commits in the last 24 hours."""
    try:
        result = subprocess.run(
            ["git", "log", "--since=1 day ago", "--format=%h"],
            capture_output=True,
            text=True,
            timeout=1,
            cwd=workspace_root
        )
        if result.returncode == 0:
            commits = [l for l in result.stdout.strip().split('\n') if l]
            return len(commits)
    except Exception:
        pass
    return 0


def format_duration(ms):
    """Format milliseconds into human-readable duration."""
    if ms < 60000:  # Less than 1 minute
        return f"{int(ms/1000)}s"
    elif ms < 3600000:  # Less than 1 hour
        return f"{int(ms/60000)}m"
    else:  # Hours
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

                        # Track most recent main chain entry for context length
                        is_sidechain = data.get("isSidechain", False)
                        timestamp = data.get("timestamp")
                        is_error = data.get("isApiErrorMessage", False)

                        if not is_sidechain and timestamp and not is_error:
                            if most_recent_timestamp is None or timestamp > most_recent_timestamp:
                                most_recent_timestamp = timestamp
                                # Context length = input + cache tokens from most recent message
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
            "total_cached": cache_creation_tokens  # Total tokens stored in cache
        }
    except Exception:
        return None


def main():
    """Generate status line from Claude Code session context."""
    try:
        # Read JSON input from Claude Code via stdin
        input_data = json.loads(sys.stdin.read())

        # Extract cost/usage data
        cost_data = input_data.get("cost", {})
        total_duration_ms = cost_data.get("total_duration_ms", 0)
        total_api_duration_ms = cost_data.get("total_api_duration_ms", 0)

        # Extract workspace data
        workspace = input_data.get("workspace", {})
        cwd = workspace.get("current_dir", "/unknown")

        # Parse token usage from transcript
        transcript_path = input_data.get("transcript_path", "")
        tokens = parse_transcript_tokens(transcript_path) if transcript_path else None

        # Load workspace session data
        session_data = load_session_summary()

        # Get focused outcome
        focused = get_focused_outcome(session_data)
        focus_text = focused if focused else "No Focus Set"

        # Get session time
        session_time = format_duration(total_duration_ms) if total_duration_ms > 0 else "0s"

        # Calculate efficiency
        if total_duration_ms > 0 and total_api_duration_ms > 0:
            efficiency = int((total_api_duration_ms / total_duration_ms) * 100)
            efficiency_text = f"{efficiency}%"
        else:
            efficiency_text = "0%"

        # Get git information
        git_branch = get_git_branch()
        git_worktree = get_git_worktree_name()
        git_changes = get_git_changes()
        commits_today = get_commits_today()

        # Get lines changed from cost data
        lines_added = cost_data.get("total_lines_added", 0)
        lines_removed = cost_data.get("total_lines_removed", 0)

        # Build three lines with colors and icons
        # Line 1: Focus (magenta if set, gray if not), Session (cyan), Efficiency (green/yellow based on %), Tokens
        focus_color = Colors.MAGENTA if focused else Colors.GRAY
        efficiency_num = int(efficiency_text.rstrip('%')) if efficiency_text != "0%" else 0
        efficiency_color = Colors.GREEN if efficiency_num >= 30 else Colors.YELLOW if efficiency_num > 0 else Colors.GRAY

        # Build line 1 with new order: Focus | Context | Database (hit rate) Up Down | (Time Efficiency)
        line1_parts = [
            f"{Colors.CYAN}{Icons.FOCUS}{Colors.RESET} {focus_color}{focus_text}{Colors.RESET}"
        ]

        # Add token info if available
        if tokens:
            context_tokens = format_tokens(tokens["context"])
            total_cached = format_tokens(tokens["total_cached"])
            cache_tokens = tokens["cache"]
            up_tokens = format_tokens(tokens["input"])
            down_tokens = format_tokens(tokens["output"])

            # Calculate cache hit rate (% of input that came from cache)
            total_input = tokens["input"] + cache_tokens
            cache_hit_rate = int((cache_tokens / total_input * 100)) if total_input > 0 else 0

            # Calculate cache usage (tokens read from cache / tokens stored in cache)
            # >100% means you're getting more value than what was cached (multiple hits)
            cache_usage = int((cache_tokens / tokens["total_cached"] * 100)) if tokens["total_cached"] > 0 else 0

            # Context window
            line1_parts.append(
                f"{Colors.CYAN}{Icons.CONTEXT}{Colors.RESET}{Colors.BRIGHT_BLUE}{context_tokens}{Colors.RESET}"
            )

            # Database with hit rate and ROI (◎ hit% / ⤴ roi%)
            line1_parts.append(
                f"{Colors.CYAN}{Icons.DATABASE}{Colors.RESET}{Colors.MAGENTA}{total_cached}{Colors.RESET}"
                f"{Colors.GRAY}({Colors.CYAN}{Icons.HIT} {Colors.GREEN}{cache_hit_rate}%"
                f"{Colors.GRAY} / {Colors.CYAN}{Icons.ROI} {Colors.YELLOW}{cache_usage}%{Colors.GRAY}){Colors.RESET}"
            )

            line1_parts.append(
                f"{Colors.CYAN}{Icons.UP}{Colors.RESET}{Colors.BLUE}{up_tokens}{Colors.RESET} "
                f"{Colors.CYAN}{Icons.DOWN}{Colors.RESET}{Colors.GREEN}{down_tokens}{Colors.RESET}"
            )

        # Add session info at the end
        line1_parts.append(
            f"({Colors.CYAN}{Icons.SESSION}{Colors.RESET} {Colors.BLUE}{session_time}{Colors.RESET} "
            f"{Colors.CYAN}{Icons.EFFICIENCY}{Colors.RESET} {efficiency_color}{efficiency_text}{Colors.RESET})"
        )

        line1 = f" {Colors.GRAY}|{Colors.RESET} ".join(line1_parts)

        # Line 2: Branch, Tree, Commits today, Lines changed
        tree_color = Colors.BRIGHT_CYAN if git_worktree != "none" else Colors.GRAY

        # Format lines changed as +added/-removed
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

        # Line 3: Cwd (dim white for path)
        line3 = f"{Colors.CYAN}{Icons.CWD}{Colors.RESET} {Colors.WHITE}{cwd}{Colors.RESET}"

        # Output status line
        print(f"{line1}\n{line2}\n{line3}")

    except json.JSONDecodeError:
        # Fallback if no valid JSON input
        print("lucid_stack\nNo data\nNo cwd")
    except Exception as e:
        # Fallback with error indication
        print(f"lucid_stack\nerr: {type(e).__name__}\nNo cwd")


if __name__ == "__main__":
    main()
