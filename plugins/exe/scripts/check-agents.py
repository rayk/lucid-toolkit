#!/usr/bin/env python3
"""
Verify all agents assigned in an execution plan are available.

Checks:
- Built-in agents (always available): general-purpose, Explore, Plan
- Plugin agents: verifies plugin directory and agent file exist

Exit codes:
    0 - All agents available
    1 - Missing agents detected
    2 - Usage error or file not found
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import NamedTuple


# Built-in Claude Code agents that are always available
BUILTIN_AGENTS = {'general-purpose', 'Explore', 'Plan'}


class AgentCheckResult(NamedTuple):
    valid: bool
    errors: list[str]
    warnings: list[str]
    agents_found: list[str]
    agents_missing: list[str]


def find_plugins_dir(start_path: Path) -> Path | None:
    """Find the plugins directory by walking up from start_path."""
    current = start_path.resolve()

    # Check if we're already in or near plugins
    if current.name == 'plugins':
        return current

    # Walk up looking for plugins directory
    for parent in [current] + list(current.parents):
        plugins_dir = parent / 'plugins'
        if plugins_dir.is_dir():
            return plugins_dir

    return None


def parse_agents_from_plan(content: str) -> set[str]:
    """Extract all agent references from an execution plan."""
    agents = set()

    # Pattern for tasks array rows: Action,{id},{name},{type},{complexity},{model},{agent},...
    # Agent is the 7th field (index 6)
    task_pattern = re.compile(r'^Action,([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+)')

    in_tasks_block = False

    for line in content.split('\n'):
        stripped = line.strip()

        # Detect tasks array header
        if re.match(r'^\s*tasks\[\d+,?\]', line):
            in_tasks_block = True
            continue

        # End block on new section
        if re.match(r'^\s*\w+\[.*?\]:', line) and 'tasks[' not in line:
            in_tasks_block = False

        # Parse task rows
        if in_tasks_block:
            match = task_pattern.match(stripped)
            if match:
                agent = match.group(6).strip()
                if agent:
                    agents.add(agent)

    return agents


def check_agent_available(agent: str, plugins_dir: Path | None) -> tuple[bool, str | None]:
    """
    Check if an agent is available.

    Returns:
        (available, error_message)
    """
    # Built-in agents are always available
    if agent in BUILTIN_AGENTS:
        return True, None

    # Plugin agents have format: {plugin}:{agent}
    if ':' not in agent:
        return False, f"Invalid agent format '{agent}' - expected 'plugin:agent' or built-in name"

    plugin_name, agent_name = agent.split(':', 1)

    if not plugins_dir:
        return False, f"Cannot verify plugin agent '{agent}' - plugins directory not found"

    plugin_dir = plugins_dir / plugin_name

    # Check plugin exists
    if not plugin_dir.is_dir():
        return False, f"Plugin '{plugin_name}' not found at {plugin_dir}"

    # Check plugin.json exists and declares the agent
    plugin_json = plugin_dir / 'plugin.json'
    if not plugin_json.exists():
        return False, f"Plugin '{plugin_name}' missing plugin.json"

    try:
        config = json.loads(plugin_json.read_text())
    except json.JSONDecodeError as e:
        return False, f"Plugin '{plugin_name}' has invalid plugin.json: {e}"

    # Check if agent is declared
    declared_agents = config.get('agents', [])
    agent_file = f"./agents/{agent_name}.md"

    if agent_file not in declared_agents and f"agents/{agent_name}.md" not in declared_agents:
        # Also check if file exists even if not declared
        agent_path = plugin_dir / 'agents' / f'{agent_name}.md'
        if agent_path.exists():
            return False, f"Agent '{agent_name}' exists but not declared in {plugin_name}/plugin.json"
        else:
            return False, f"Agent '{agent_name}' not found in plugin '{plugin_name}'"

    # Verify agent file actually exists
    agent_path = plugin_dir / 'agents' / f'{agent_name}.md'
    if not agent_path.exists():
        return False, f"Agent declared but file missing: {agent_path}"

    return True, None


def check_agents(content: str, filepath: Path, plugins_dir: Path | None) -> AgentCheckResult:
    """Check all agents in an execution plan are available."""
    errors = []
    warnings = []
    agents_found = []
    agents_missing = []

    agents = parse_agents_from_plan(content)

    if not agents:
        warnings.append("No agents found in execution plan")
        return AgentCheckResult(True, errors, warnings, agents_found, agents_missing)

    for agent in sorted(agents):
        available, error = check_agent_available(agent, plugins_dir)

        if available:
            agents_found.append(agent)
        else:
            agents_missing.append(agent)
            errors.append(error or f"Agent not available: {agent}")

    return AgentCheckResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        agents_found=agents_found,
        agents_missing=agents_missing
    )


def main():
    parser = argparse.ArgumentParser(
        description='Verify all agents assigned in an execution plan are available',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s execution-plan.toon
    %(prog)s specs/auth-plan.toon --plugins-dir ./plugins
    %(prog)s *.toon --list
        """
    )
    parser.add_argument('files', nargs='+', type=Path, help='Execution plan file(s) to check')
    parser.add_argument(
        '--plugins-dir', '-p', type=Path,
        help='Path to plugins directory (auto-detected if not specified)'
    )
    parser.add_argument('--list', '-l', action='store_true', help='List all agents found')
    parser.add_argument('--quiet', '-q', action='store_true', help='Only output on error')

    args = parser.parse_args()

    # Determine plugins directory
    plugins_dir = args.plugins_dir
    if not plugins_dir:
        # Try to auto-detect from first file's location
        if args.files:
            plugins_dir = find_plugins_dir(args.files[0])
        if not plugins_dir:
            plugins_dir = find_plugins_dir(Path.cwd())

    if plugins_dir and not plugins_dir.is_dir():
        print(f"ERROR: Plugins directory not found: {plugins_dir}", file=sys.stderr)
        sys.exit(2)

    all_valid = True

    for filepath in args.files:
        if not filepath.exists():
            print(f"ERROR: File not found: {filepath}", file=sys.stderr)
            all_valid = False
            continue

        try:
            content = filepath.read_text(encoding='utf-8')
        except Exception as e:
            print(f"ERROR: Failed to read {filepath}: {e}", file=sys.stderr)
            all_valid = False
            continue

        result = check_agents(content, filepath, plugins_dir)

        if not result.valid:
            all_valid = False
            print(f"INVALID: {filepath}", file=sys.stderr)
            for error in result.errors:
                print(f"  ERROR: {error}", file=sys.stderr)
            for warning in result.warnings:
                print(f"  WARNING: {warning}", file=sys.stderr)
            if args.list and result.agents_found:
                print(f"  Available: {', '.join(result.agents_found)}", file=sys.stderr)
            if result.agents_missing:
                print(f"  Missing: {', '.join(result.agents_missing)}", file=sys.stderr)
        elif not args.quiet:
            print(f"VALID: {filepath}")
            if args.list:
                print(f"  Agents ({len(result.agents_found)}): {', '.join(result.agents_found)}")
            for warning in result.warnings:
                print(f"  WARNING: {warning}")

    sys.exit(0 if all_valid else 1)


if __name__ == '__main__':
    main()
