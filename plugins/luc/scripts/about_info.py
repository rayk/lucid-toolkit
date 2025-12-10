#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# ///
"""Gather all info for /luc:about command.

Returns JSON with session, installed plugins, and project plugins.
"""
import json
import os
from pathlib import Path


def get_session_info() -> dict:
    """Get current session ID and paths."""
    debug_dir = Path.home() / ".claude" / "debug"
    latest_link = debug_dir / "latest"

    result = {
        "session_id": "unknown",
        "transcript_path": None,
        "debug_log_path": "unknown"
    }

    try:
        if latest_link.is_symlink():
            debug_log = latest_link.resolve()
            result["debug_log_path"] = str(debug_log)
            result["session_id"] = debug_log.stem

            # Search for transcript
            projects_dir = Path.home() / ".claude" / "projects"
            if projects_dir.exists():
                for project_dir in projects_dir.iterdir():
                    if project_dir.is_dir():
                        transcript = project_dir / "transcripts" / f"{result['session_id']}.jsonl"
                        if transcript.exists():
                            result["transcript_path"] = str(transcript)
                            break
    except Exception:
        pass

    return result


def get_installed_plugins() -> list[dict]:
    """Get installed plugins from registry."""
    registry_path = Path.home() / ".claude" / "plugins" / "installed_plugins.json"
    plugins = []

    try:
        if registry_path.exists():
            with open(registry_path) as f:
                data = json.load(f)

            for key, info in data.get("plugins", {}).items():
                if "@lucid-toolkit" in key:
                    name = key.split("@")[0]
                    plugins.append({
                        "name": name,
                        "version": info.get("version", "unknown"),
                        "installed_at": info.get("installedAt"),
                        "is_local": info.get("isLocal", False)
                    })
    except Exception:
        pass

    return sorted(plugins, key=lambda p: p["name"])


def get_project_plugins() -> list[str]:
    """Get plugins installed in current project."""
    plugins_dir = Path(".claude/plugins")
    plugins = []

    try:
        if plugins_dir.exists():
            for item in plugins_dir.iterdir():
                if item.is_dir():
                    plugins.append(item.name)
    except Exception:
        pass

    return sorted(plugins)


def get_luc_contents() -> dict:
    """Get luc plugin contents (skills, commands, schemas)."""
    # Find luc plugin in cache
    cache_base = Path.home() / ".claude" / "plugins" / "cache" / "lucid-toolkit" / "luc"
    contents = {"skills": [], "commands": [], "schemas": []}

    try:
        if cache_base.exists():
            # Get latest version directory
            versions = [d for d in cache_base.iterdir() if d.is_dir()]
            if versions:
                luc_dir = max(versions, key=lambda d: d.stat().st_mtime)

                # Count skills
                skills_dir = luc_dir / "skills"
                if skills_dir.exists():
                    contents["skills"] = [d.name for d in skills_dir.iterdir() if d.is_dir()]

                # Count commands
                commands_dir = luc_dir / "commands"
                if commands_dir.exists():
                    contents["commands"] = [f.stem for f in commands_dir.glob("*.md")]

                # Count schemas
                schemas_dir = luc_dir / "schemas"
                if schemas_dir.exists():
                    contents["schemas"] = [f.stem for f in schemas_dir.glob("*.json")]
    except Exception:
        pass

    return contents


def main():
    info = {
        "session": get_session_info(),
        "installed_plugins": get_installed_plugins(),
        "project_plugins": get_project_plugins(),
        "luc_contents": get_luc_contents()
    }

    # Get luc version from installed plugins
    for p in info["installed_plugins"]:
        if p["name"] == "luc":
            info["luc_version"] = p["version"]
            break
    else:
        info["luc_version"] = "unknown"

    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
