#!/usr/bin/env python3
"""
Usage Analysis CLI - Data extraction and processing for usage-analysis subagent.

This script handles deterministic data operations, leaving judgment-based
analysis to the LLM. Outputs JSON for easy consumption by the subagent.

Usage:
    python usage_analysis.py init [--state-file PATH] [--marketplace PATH]
    python usage_analysis.py discover [--from DATE] [--to DATE] [--plugin NAME]
    python usage_analysis.py parse <session_id> [--session_id ...]
    python usage_analysis.py aggregate [--input FILE]
    python usage_analysis.py save [--input FILE]
"""

import argparse
import base64
import json
import os
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Constants
CLAUDE_DIR = Path.home() / ".claude"
HISTORY_FILE = CLAUDE_DIR / "history.jsonl"
PROJECTS_DIR = CLAUDE_DIR / "projects"
DEBUG_DIR = CLAUDE_DIR / "debug"
DEFAULT_STATE_FILE = Path(".claude/data/usage-analysis-state.json")
DEFAULT_SCHEMA_FILE = Path(".claude/schema/usage-analysis-state.schema.json")
DEFAULT_MARKETPLACE = Path(".claude-plugin/marketplace.json")


@dataclass
class PluginBehavior:
    """A single behavior (command/skill/agent/hook) from a plugin."""
    name: str
    type: str  # command, skill, agent, hook
    plugin: str
    version: str
    path: str


@dataclass
class PluginInventory:
    """Complete inventory of plugins and their behaviors."""
    plugins: dict = field(default_factory=dict)
    behaviors: dict = field(default_factory=dict)  # behavior_name -> PluginBehavior

    def to_dict(self):
        return {
            "plugins": self.plugins,
            "behaviors": {k: asdict(v) for k, v in self.behaviors.items()}
        }


@dataclass
class SessionInfo:
    """Metadata about a Claude Code session."""
    session_id: str
    project: str
    project_path: str
    timestamp: str
    log_file: Optional[str] = None


@dataclass
class ToolCall:
    """A single tool invocation extracted from session logs."""
    tool_name: str
    timestamp: str
    parameters: dict
    result: Optional[str] = None
    duration_ms: Optional[int] = None
    tokens_input: Optional[int] = None
    tokens_output: Optional[int] = None
    is_background: bool = False
    is_parallel: bool = False


@dataclass
class SessionAnalysis:
    """Extracted data from a single session."""
    session_id: str
    project: str
    timestamp: str
    tool_calls: list = field(default_factory=list)
    behaviors_invoked: list = field(default_factory=list)
    plugins_detected: list = field(default_factory=list)
    total_tokens_input: int = 0
    total_tokens_output: int = 0
    total_cache_reads: int = 0
    total_cache_writes: int = 0
    duration_ms: int = 0
    execution_patterns: dict = field(default_factory=lambda: {
        "foreground": 0, "background": 0, "parallel": 0, "sequential": 0
    })
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)


@dataclass
class AggregatedMetrics:
    """Aggregated metrics across all analyzed sessions."""
    total_sessions: int = 0
    date_range_start: Optional[str] = None
    date_range_end: Optional[str] = None
    behavior_metrics: dict = field(default_factory=dict)
    plugin_metrics: dict = field(default_factory=dict)


def load_jsonl(path: Path) -> list:
    """Load a JSONL file, returning list of parsed objects."""
    if not path.exists():
        return []

    results = []
    with open(path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Warning: Skipping malformed line {line_num} in {path}: {e}",
                      file=sys.stderr)
    return results


def decode_project_path(encoded: str) -> str:
    """Decode base64 encoded project path from Claude's directory naming."""
    try:
        # Claude uses URL-safe base64 with some modifications
        # Try standard decode first
        decoded = base64.urlsafe_b64decode(encoded + '==').decode('utf-8')
        return decoded
    except Exception:
        # Return as-is if decoding fails
        return encoded


def cmd_init(args) -> dict:
    """
    Initialize analysis state and build plugin inventory.

    Returns JSON with:
    - state: Current state file contents (or new empty state)
    - inventory: Plugin inventory with all behaviors
    - status: Success/error status
    """
    result = {
        "status": "success",
        "state": None,
        "inventory": None,
        "errors": [],
        "warnings": []
    }

    # Load or initialize state file
    state_path = Path(args.state_file)
    if state_path.exists():
        try:
            with open(state_path) as f:
                result["state"] = json.load(f)
        except json.JSONDecodeError as e:
            result["errors"].append(f"State file corrupted: {e}")
            result["status"] = "error"
            return result
    else:
        # Initialize empty state with schema reference
        result["state"] = {
            "$schema": "../schema/usage-analysis-state.schema.json",
            "analysisMetadata": {
                "lastAnalyzedTimestamp": "1970-01-01T00:00:00Z",
                "lastAnalyzedSessionId": None,
                "lastRunTimestamp": datetime.now(timezone.utc).isoformat(),
                "totalSessionsAnalyzed": 0,
                "dateRangeStart": None,
                "dateRangeEnd": None
            },
            "pluginInventory": {},
            "invocationMetrics": {},
            "sessionSummaries": [],
            "findings": {
                "category1_missed": [],
                "category2_suboptimal": [],
                "category3_unused": []
            }
        }
        result["warnings"].append("State file not found, initialized new state")

    # Build plugin inventory
    inventory = PluginInventory()
    marketplace_path = Path(args.marketplace)

    if not marketplace_path.exists():
        result["errors"].append(f"Marketplace file not found: {marketplace_path}")
        result["status"] = "error"
        return result

    try:
        with open(marketplace_path) as f:
            marketplace = json.load(f)
    except json.JSONDecodeError as e:
        result["errors"].append(f"Marketplace file corrupted: {e}")
        result["status"] = "error"
        return result

    # Process each plugin
    for plugin_entry in marketplace.get("plugins", []):
        plugin_name = plugin_entry.get("name")
        plugin_source = plugin_entry.get("source", "")
        plugin_version = plugin_entry.get("version", "unknown")

        # Find plugin.json
        plugin_json_path = Path(plugin_source) / "plugin.json"
        if not plugin_json_path.exists():
            # Try relative to marketplace
            plugin_json_path = marketplace_path.parent.parent / plugin_source / "plugin.json"

        if not plugin_json_path.exists():
            result["warnings"].append(f"Plugin config not found: {plugin_name}")
            continue

        try:
            with open(plugin_json_path) as f:
                plugin_config = json.load(f)
        except json.JSONDecodeError:
            result["warnings"].append(f"Plugin config corrupted: {plugin_name}")
            continue

        # Extract behaviors
        plugin_data = {
            "name": plugin_name,
            "version": plugin_version,
            "behaviors": {
                "commands": [],
                "skills": [],
                "agents": [],
                "hooks": []
            }
        }

        # Commands
        for cmd_path in plugin_config.get("commands", []):
            cmd_name = Path(cmd_path).stem
            behavior = PluginBehavior(
                name=cmd_name,
                type="command",
                plugin=plugin_name,
                version=plugin_version,
                path=cmd_path
            )
            plugin_data["behaviors"]["commands"].append(cmd_name)
            inventory.behaviors[f"{plugin_name}:{cmd_name}"] = behavior

        # Skills
        for skill_path in plugin_config.get("skills", []):
            skill_name = Path(skill_path).name
            behavior = PluginBehavior(
                name=skill_name,
                type="skill",
                plugin=plugin_name,
                version=plugin_version,
                path=skill_path
            )
            plugin_data["behaviors"]["skills"].append(skill_name)
            inventory.behaviors[f"{plugin_name}:{skill_name}"] = behavior

        # Agents
        for agent_path in plugin_config.get("agents", []):
            agent_name = Path(agent_path).stem
            behavior = PluginBehavior(
                name=agent_name,
                type="agent",
                plugin=plugin_name,
                version=plugin_version,
                path=agent_path
            )
            plugin_data["behaviors"]["agents"].append(agent_name)
            inventory.behaviors[f"{plugin_name}:{agent_name}"] = behavior

        # Hooks
        for hook_path in plugin_config.get("hooks", []):
            hook_name = Path(hook_path).stem
            behavior = PluginBehavior(
                name=hook_name,
                type="hook",
                plugin=plugin_name,
                version=plugin_version,
                path=hook_path
            )
            plugin_data["behaviors"]["hooks"].append(hook_name)
            inventory.behaviors[f"{plugin_name}:{hook_name}"] = behavior

        inventory.plugins[plugin_name] = plugin_data

    result["inventory"] = inventory.to_dict()
    return result


def cmd_discover(args) -> dict:
    """
    Discover sessions to analyze.

    Returns JSON with:
    - sessions: List of session info matching criteria
    - total_found: Count of sessions found
    - filtered_by: Applied filters
    """
    result = {
        "status": "success",
        "sessions": [],
        "total_found": 0,
        "filtered_by": {
            "from_date": args.from_date,
            "to_date": args.to_date,
            "plugin": args.plugin,
            "checkpoint": args.checkpoint
        },
        "errors": [],
        "warnings": []
    }

    # Check history file
    if not HISTORY_FILE.exists():
        result["errors"].append(f"History file not found: {HISTORY_FILE}")
        result["status"] = "error"
        return result

    # Load history
    history = load_jsonl(HISTORY_FILE)
    if not history:
        result["warnings"].append("History file is empty")
        return result

    # Parse filter dates
    from_dt = None
    to_dt = None
    checkpoint_dt = None

    if args.from_date:
        try:
            from_dt = datetime.fromisoformat(args.from_date.replace('Z', '+00:00'))
        except ValueError:
            try:
                from_dt = datetime.strptime(args.from_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                result["errors"].append(f"Invalid from date: {args.from_date}")

    if args.to_date:
        try:
            to_dt = datetime.fromisoformat(args.to_date.replace('Z', '+00:00'))
        except ValueError:
            try:
                to_dt = datetime.strptime(args.to_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                result["errors"].append(f"Invalid to date: {args.to_date}")

    if args.checkpoint:
        try:
            checkpoint_dt = datetime.fromisoformat(args.checkpoint.replace('Z', '+00:00'))
        except ValueError:
            result["warnings"].append(f"Invalid checkpoint, ignoring: {args.checkpoint}")

    # Filter sessions
    sessions = []
    for entry in history:
        # Extract timestamp
        ts_str = entry.get("timestamp") or entry.get("created_at") or entry.get("date")
        if not ts_str:
            continue

        try:
            # Handle both Unix timestamps (int/float) and ISO strings
            if isinstance(ts_str, (int, float)):
                ts = datetime.fromtimestamp(ts_str / 1000.0, tz=timezone.utc)
            else:
                ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                # Ensure timezone-aware
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
        except (ValueError, OSError):
            continue

        # Apply date filters
        if from_dt and ts < from_dt:
            continue
        if to_dt and ts > to_dt:
            continue
        if checkpoint_dt and ts <= checkpoint_dt:
            continue

        # Extract session info
        session_id = entry.get("id") or entry.get("session_id") or entry.get("sessionId") or entry.get("uuid")
        project = entry.get("project") or entry.get("name") or "unknown"
        project_path = entry.get("path") or entry.get("project_path") or entry.get("project") or ""

        if not session_id:
            continue

        # Find corresponding log file
        log_file = None
        if project_path:
            # Try slug format first (newer format): replace / with -
            slug = project_path.replace('/', '-')
            project_dir = PROJECTS_DIR / slug

            # If slug doesn't exist, try base64 (older format)
            if not project_dir.exists():
                encoded = base64.urlsafe_b64encode(project_path.encode()).decode().rstrip('=')
                project_dir = PROJECTS_DIR / encoded

            if project_dir.exists():
                # Find session file
                for f in project_dir.glob("*.jsonl"):
                    if session_id in f.name:
                        log_file = str(f)
                        break

        sessions.append({
            "session_id": session_id,
            "project": project,
            "project_path": project_path,
            "timestamp": ts_str,
            "log_file": log_file
        })

    # Sort by timestamp
    sessions.sort(key=lambda x: x["timestamp"])

    result["sessions"] = sessions
    result["total_found"] = len(sessions)
    return result


def cmd_parse(args) -> dict:
    """
    Parse session log files and extract structured data.

    Handles the current Claude Code log format where:
    - Tool uses are nested in message.content[] with type="tool_use"
    - Token usage is in message.usage
    - Entry types include "assistant", "user", "summary", etc.

    Returns JSON with:
    - sessions: List of SessionAnalysis for each parsed session
    - summary: Quick stats across all parsed sessions
    """
    result = {
        "status": "success",
        "sessions": [],
        "summary": {
            "total_parsed": 0,
            "total_tool_calls": 0,
            "total_behaviors": 0,
            "parse_errors": 0
        },
        "errors": [],
        "warnings": []
    }

    # Load inventory if provided (optional - pattern-discovery doesn't require it)
    inventory = {}
    if args.inventory:
        try:
            inv_data = json.loads(args.inventory)
            # Handle both direct behaviors and nested inventory.behaviors
            inventory = inv_data.get("inventory", {}).get("behaviors", {})
            if not inventory:
                inventory = inv_data.get("behaviors", {})
        except json.JSONDecodeError:
            if Path(args.inventory).exists():
                with open(args.inventory) as f:
                    inv_data = json.load(f)
                    inventory = inv_data.get("inventory", {}).get("behaviors", {})
                    if not inventory:
                        inventory = inv_data.get("behaviors", {})

    for log_file in args.log_files:
        log_path = Path(log_file)
        if not log_path.exists():
            result["warnings"].append(f"Log file not found: {log_file}")
            result["summary"]["parse_errors"] += 1
            continue

        # Parse the session log
        entries = load_jsonl(log_path)
        if not entries:
            result["warnings"].append(f"Empty or corrupted log: {log_file}")
            result["summary"]["parse_errors"] += 1
            continue

        analysis = SessionAnalysis(
            session_id=log_path.stem,
            project=str(log_path.parent.name),
            timestamp=""
        )

        first_timestamp = None

        for entry in entries:
            entry_type = entry.get("type")

            # Extract timestamp from entry
            ts = entry.get("timestamp")
            if ts and not first_timestamp:
                first_timestamp = ts
                analysis.timestamp = ts

            # Get message object (current log format nests content here)
            message = entry.get("message", {})
            message_content = message.get("content", [])
            message_role = message.get("role")

            # Token metrics from message.usage (current format)
            if "usage" in message:
                usage = message["usage"]
                analysis.total_tokens_input += usage.get("input_tokens", 0)
                analysis.total_tokens_output += usage.get("output_tokens", 0)
                analysis.total_cache_reads += usage.get("cache_read_input_tokens", 0)
                analysis.total_cache_writes += usage.get("cache_creation_input_tokens", 0)

            # Also check entry-level usage (legacy format)
            if "usage" in entry and "usage" not in message:
                usage = entry["usage"]
                analysis.total_tokens_input += usage.get("input_tokens", 0)
                analysis.total_tokens_output += usage.get("output_tokens", 0)
                analysis.total_cache_reads += usage.get("cache_read_input_tokens", 0)
                analysis.total_cache_writes += usage.get("cache_creation_input_tokens", 0)

            # Process assistant messages containing tool calls
            if entry_type == "assistant" or message_role == "assistant":
                if isinstance(message_content, list):
                    tool_uses_in_message = []

                    for content_block in message_content:
                        if not isinstance(content_block, dict):
                            continue

                        block_type = content_block.get("type")

                        # Extract tool_use blocks from message.content[]
                        if block_type == "tool_use":
                            tool_name = content_block.get("name", "unknown")
                            tool_input = content_block.get("input", {})

                            tool_call = ToolCall(
                                tool_name=tool_name,
                                timestamp=ts or "",
                                parameters=tool_input
                            )

                            # Detect background execution
                            if tool_name == "Task":
                                if tool_input.get("run_in_background"):
                                    tool_call.is_background = True
                                    analysis.execution_patterns["background"] += 1
                                else:
                                    analysis.execution_patterns["foreground"] += 1
                            elif tool_name == "Bash":
                                if tool_input.get("run_in_background"):
                                    tool_call.is_background = True
                                    analysis.execution_patterns["background"] += 1

                            tool_uses_in_message.append(tool_call)
                            analysis.tool_calls.append(asdict(tool_call))

                            # Detect behavior invocations
                            if tool_name == "Skill":
                                skill = tool_input.get("skill", "")
                                if skill:
                                    analysis.behaviors_invoked.append(f"skill:{skill}")
                            elif tool_name == "SlashCommand":
                                cmd = tool_input.get("command", "")
                                if cmd:
                                    analysis.behaviors_invoked.append(f"command:{cmd}")
                            elif tool_name == "Task":
                                agent = tool_input.get("subagent_type", "")
                                if agent:
                                    analysis.behaviors_invoked.append(f"agent:{agent}")

                    # Track parallel vs sequential execution patterns
                    tool_count = len(tool_uses_in_message)
                    if tool_count > 1:
                        analysis.execution_patterns["parallel"] += tool_count
                        for tc in tool_uses_in_message:
                            tc.is_parallel = True
                    elif tool_count == 1:
                        analysis.execution_patterns["sequential"] += 1

            # Errors - check both entry-level and message content
            if entry_type == "error" or entry.get("is_error"):
                error_msg = entry.get("message", entry.get("error", str(entry)))
                if isinstance(error_msg, dict):
                    error_msg = error_msg.get("message", str(error_msg))
                analysis.errors.append(str(error_msg))

        # Set timestamp
        if not analysis.timestamp and first_timestamp:
            analysis.timestamp = first_timestamp
        elif not analysis.timestamp:
            analysis.timestamp = datetime.now(timezone.utc).isoformat()

        # Deduplicate behaviors
        analysis.behaviors_invoked = list(set(analysis.behaviors_invoked))

        # Match behaviors to plugins (only if inventory provided)
        if inventory:
            for behavior in analysis.behaviors_invoked:
                for key, info in inventory.items():
                    if isinstance(info, dict) and behavior.endswith(info.get("name", "")):
                        plugin_name = info.get("plugin")
                        if plugin_name and plugin_name not in analysis.plugins_detected:
                            analysis.plugins_detected.append(plugin_name)

        result["sessions"].append(asdict(analysis))
        result["summary"]["total_parsed"] += 1
        result["summary"]["total_tool_calls"] += len(analysis.tool_calls)
        result["summary"]["total_behaviors"] += len(analysis.behaviors_invoked)

    return result


def cmd_aggregate(args) -> dict:
    """
    Aggregate metrics from parsed session data.

    Returns JSON with:
    - metrics: Aggregated metrics per behavior and plugin
    - trends: Usage over time
    """
    result = {
        "status": "success",
        "metrics": {
            "behaviors": {},
            "plugins": {},
            "totals": {
                "sessions": 0,
                "tool_calls": 0,
                "tokens_input": 0,
                "tokens_output": 0,
                "cache_reads": 0,
                "behaviors_invoked": 0
            }
        },
        "date_range": {
            "start": None,
            "end": None
        },
        "errors": [],
        "warnings": []
    }

    # Load input data
    if args.input == "-":
        input_data = json.load(sys.stdin)
    elif args.input:
        with open(args.input) as f:
            input_data = json.load(f)
    else:
        result["errors"].append("No input data provided")
        result["status"] = "error"
        return result

    sessions = input_data.get("sessions", [])
    if not sessions:
        result["warnings"].append("No sessions to aggregate")
        return result

    # Aggregate
    behavior_stats = {}
    plugin_stats = {}
    timestamps = []

    for session in sessions:
        result["metrics"]["totals"]["sessions"] += 1
        result["metrics"]["totals"]["tool_calls"] += len(session.get("tool_calls", []))
        result["metrics"]["totals"]["tokens_input"] += session.get("total_tokens_input", 0)
        result["metrics"]["totals"]["tokens_output"] += session.get("total_tokens_output", 0)
        result["metrics"]["totals"]["cache_reads"] += session.get("total_cache_reads", 0)

        ts = session.get("timestamp")
        if ts:
            timestamps.append(ts)

        # Per-behavior stats
        for behavior in session.get("behaviors_invoked", []):
            result["metrics"]["totals"]["behaviors_invoked"] += 1

            if behavior not in behavior_stats:
                behavior_stats[behavior] = {
                    "invocations": 0,
                    "sessions": set(),
                    "tokens_input": 0,
                    "tokens_output": 0,
                    "execution_patterns": {"foreground": 0, "background": 0, "parallel": 0, "sequential": 0}
                }

            behavior_stats[behavior]["invocations"] += 1
            behavior_stats[behavior]["sessions"].add(session.get("session_id"))

        # Per-plugin stats
        for plugin in session.get("plugins_detected", []):
            if plugin not in plugin_stats:
                plugin_stats[plugin] = {
                    "sessions": set(),
                    "behaviors_used": set()
                }
            plugin_stats[plugin]["sessions"].add(session.get("session_id"))
            for b in session.get("behaviors_invoked", []):
                plugin_stats[plugin]["behaviors_used"].add(b)

    # Convert sets to lists for JSON
    for behavior, stats in behavior_stats.items():
        stats["sessions"] = list(stats["sessions"])
        stats["session_count"] = len(stats["sessions"])

    for plugin, stats in plugin_stats.items():
        stats["sessions"] = list(stats["sessions"])
        stats["session_count"] = len(stats["sessions"])
        stats["behaviors_used"] = list(stats["behaviors_used"])

    result["metrics"]["behaviors"] = behavior_stats
    result["metrics"]["plugins"] = plugin_stats

    # Date range
    if timestamps:
        timestamps.sort()
        result["date_range"]["start"] = timestamps[0]
        result["date_range"]["end"] = timestamps[-1]

    return result


def cmd_save(args) -> dict:
    """
    Save updated state to file.

    Returns JSON with:
    - status: Success/error
    - path: Where state was saved
    """
    result = {
        "status": "success",
        "path": str(args.state_file),
        "errors": []
    }

    # Load input data
    if args.input == "-":
        state_data = json.load(sys.stdin)
    elif args.input:
        with open(args.input) as f:
            state_data = json.load(f)
    else:
        result["errors"].append("No input data provided")
        result["status"] = "error"
        return result

    # Update metadata
    state_data.setdefault("analysisMetadata", {})
    state_data["analysisMetadata"]["lastRunTimestamp"] = datetime.now(timezone.utc).isoformat()

    # Write state file
    state_path = Path(args.state_file)
    state_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(state_path, 'w') as f:
            json.dump(state_data, f, indent=2)
    except Exception as e:
        result["errors"].append(f"Failed to write state file: {e}")
        result["status"] = "error"
        return result

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Usage Analysis CLI for Claude Code plugin analysis"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init command
    init_parser = subparsers.add_parser("init", help="Initialize state and build inventory")
    init_parser.add_argument("--state-file", default=str(DEFAULT_STATE_FILE),
                            help="Path to state file")
    init_parser.add_argument("--marketplace", default=str(DEFAULT_MARKETPLACE),
                            help="Path to marketplace.json")

    # discover command
    discover_parser = subparsers.add_parser("discover", help="Discover sessions to analyze")
    discover_parser.add_argument("--from", dest="from_date", help="Start date (YYYY-MM-DD)")
    discover_parser.add_argument("--to", dest="to_date", help="End date (YYYY-MM-DD)")
    discover_parser.add_argument("--plugin", help="Filter by plugin name")
    discover_parser.add_argument("--checkpoint", help="Resume from timestamp")

    # parse command
    parse_parser = subparsers.add_parser("parse", help="Parse session log files")
    parse_parser.add_argument("log_files", nargs="+", help="Session log files to parse")
    parse_parser.add_argument("--inventory", help="Plugin inventory JSON or file path")

    # aggregate command
    agg_parser = subparsers.add_parser("aggregate", help="Aggregate metrics from parsed data")
    agg_parser.add_argument("--input", default="-", help="Input JSON file (- for stdin)")

    # save command
    save_parser = subparsers.add_parser("save", help="Save updated state")
    save_parser.add_argument("--input", default="-", help="State JSON to save (- for stdin)")
    save_parser.add_argument("--state-file", default=str(DEFAULT_STATE_FILE),
                            help="Path to state file")

    args = parser.parse_args()

    # Execute command
    if args.command == "init":
        result = cmd_init(args)
    elif args.command == "discover":
        result = cmd_discover(args)
    elif args.command == "parse":
        result = cmd_parse(args)
    elif args.command == "aggregate":
        result = cmd_aggregate(args)
    elif args.command == "save":
        result = cmd_save(args)
    else:
        result = {"status": "error", "errors": [f"Unknown command: {args.command}"]}

    # Output JSON
    print(json.dumps(result, indent=2, default=str))

    # Exit with error code if failed
    if result.get("status") == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
