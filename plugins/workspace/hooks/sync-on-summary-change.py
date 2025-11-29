#!/usr/bin/env python3
"""
Sync workspace indexes to all member projects when summary files change.

This hook is triggered after Write operations on capability_summary.json
or outcome_summary.json. It updates the indexes section in each project's
.claude/workspace.json file.

Usage:
    python3 sync-on-summary-change.py <changed-file-path>

Exit codes:
    0 - Success (indexes synced or no sync needed)
    1 - Error during sync
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def find_workspace_root(start_path: Path) -> Path | None:
    """Find workspace root by looking for workspace.json."""
    current = start_path
    while current != current.parent:
        if (current / "workspace.json").exists():
            return current
        current = current.parent
    return None


def load_json(path: Path) -> dict | None:
    """Load JSON file, return None if not found or invalid."""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_json(path: Path, data: dict) -> bool:
    """Save JSON file with pretty formatting."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        return True
    except Exception as e:
        print(f"Error saving {path}: {e}", file=sys.stderr)
        return False


def build_capability_index(workspace_root: Path) -> dict:
    """Build capability index from summary file."""
    summary_path = workspace_root / "status" / "capability_summary.json"
    summary = load_json(summary_path)

    if not summary:
        return {
            "path": "capabilities/",
            "description": "Strategic capabilities organized by domain with maturity tracking.",
            "summaryFile": "status/capability_summary.json",
            "count": 0,
            "domains": []
        }

    # Extract domains from indexByDomain
    domains = list(summary.get("indexByDomain", {}).keys())

    return {
        "path": "capabilities/",
        "description": "Strategic capabilities organized by domain with maturity tracking. Each capability has capability_track.json.",
        "summaryFile": "status/capability_summary.json",
        "count": summary.get("summary", {}).get("totalCapabilities", 0),
        "domains": domains,
        "metrics": {
            "averageMaturity": summary.get("summary", {}).get("averageMaturity", 0),
            "activeCount": len(summary.get("indexByActivityState", {}).get("active", [])),
            "stalledCount": len(summary.get("indexByActivityState", {}).get("stalled", []))
        }
    }


def build_outcome_index(workspace_root: Path) -> dict:
    """Build outcome index from summary file."""
    summary_path = workspace_root / "status" / "outcome_summary.json"
    summary = load_json(summary_path)

    if not summary:
        return {
            "path": "outcomes/",
            "description": "Work units organized by state.",
            "summaryFile": "status/outcome_summary.json",
            "states": {
                "queued": "outcomes/queued/",
                "ready": "outcomes/ready/",
                "in-progress": "outcomes/in-progress/",
                "blocked": "outcomes/blocked/",
                "completed": "outcomes/completed/"
            },
            "counts": {
                "queued": 0, "ready": 0, "inProgress": 0,
                "blocked": 0, "completed": 0, "total": 0
            }
        }

    stats = summary.get("summary", {})
    by_state = stats.get("outcomesByState", {})

    return {
        "path": "outcomes/",
        "description": "Work units organized by state. Each outcome has outcome_track.json with tasks and capability contributions.",
        "summaryFile": "status/outcome_summary.json",
        "states": {
            "queued": "outcomes/queued/",
            "ready": "outcomes/ready/",
            "in-progress": "outcomes/in-progress/",
            "blocked": "outcomes/blocked/",
            "completed": "outcomes/completed/"
        },
        "counts": {
            "queued": by_state.get("queued", 0),
            "ready": by_state.get("ready", 0),
            "inProgress": by_state.get("in-progress", 0),
            "blocked": by_state.get("blocked", 0),
            "completed": by_state.get("completed", 0),
            "total": stats.get("totalOutcomes", 0)
        }
    }


def build_plans_index(workspace_root: Path) -> dict:
    """Build plans index by scanning directory."""
    plans_dir = workspace_root / "plans"
    items = []

    if plans_dir.exists():
        for item in plans_dir.iterdir():
            if item.is_file() and item.suffix == ".md":
                items.append({
                    "name": item.name,
                    "path": f"plans/{item.name}",
                    "description": "",
                    "type": "execution"
                })

    return {
        "path": "plans/",
        "description": "Strategic roadmaps and execution plans guiding outcome execution.",
        "items": items
    }


def build_research_index(workspace_root: Path) -> dict:
    """Build research index by scanning directory."""
    research_dir = workspace_root / "research"
    items = []

    if research_dir.exists():
        for item in research_dir.iterdir():
            if item.is_file() and item.suffix == ".md":
                items.append({
                    "name": item.name,
                    "path": f"research/{item.name}",
                    "description": "",
                    "domain": ""
                })

    return {
        "path": "research/",
        "description": "Domain research and technology evaluation informing capability design.",
        "items": items
    }


def build_status_index(workspace_root: Path) -> dict:
    """Build status files index."""
    files = []
    status_dir = workspace_root / "status"

    known_files = [
        ("capability_summary.json", "All capabilities index with maturity metrics"),
        ("outcome_summary.json", "All outcomes index with progress tracking"),
        ("actor_summary.json", "Stakeholder registry")
    ]

    for name, desc in known_files:
        if (status_dir / name).exists():
            files.append({
                "name": name,
                "path": f"status/{name}",
                "description": desc
            })

    return {
        "path": "status/",
        "description": "Summary indexes for quick artifact lookup.",
        "files": files
    }


def sync_project(workspace_root: Path, workspace_config: dict, project: dict) -> bool:
    """Sync indexes to a single project's workspace.json."""
    project_path = Path(project.get("absolutePath", ""))
    if not project_path.exists():
        print(f"  Skipping {project['id']}: directory not found", file=sys.stderr)
        return False

    project_ws_path = project_path / ".claude" / "workspace.json"
    project_ws = load_json(project_ws_path)

    # Calculate relative path from project to workspace
    try:
        rel_path = os.path.relpath(workspace_root, project_path)
    except ValueError:
        rel_path = str(workspace_root)

    # Build indexes
    indexes = {
        "capabilities": build_capability_index(workspace_root),
        "outcomes": build_outcome_index(workspace_root),
        "plans": build_plans_index(workspace_root),
        "research": build_research_index(workspace_root),
        "status": build_status_index(workspace_root)
    }

    # Build projects list with relative paths from this project's perspective
    projects = []

    # Add workspace itself
    projects.append({
        "id": workspace_config["id"],
        "name": workspace_config["name"],
        "path": rel_path,
        "absolutePath": str(workspace_root),
        "type": "workspace",
        "role": "workspace",
        "description": workspace_config.get("description", ""),
        "isWorkspace": True
    })

    # Add all projects
    for p in workspace_config.get("projects", []):
        p_path = Path(p.get("absolutePath", ""))
        try:
            p_rel = os.path.relpath(p_path, project_path)
        except ValueError:
            p_rel = str(p_path)

        projects.append({
            "id": p["id"],
            "name": p["name"],
            "path": p_rel if p["id"] != project["id"] else ".",
            "absolutePath": p.get("absolutePath", ""),
            "type": p["type"],
            "role": p.get("role", "primary"),
            "description": p.get("description", ""),
            "isSelf": p["id"] == project["id"]
        })

    # Create or update project workspace.json
    now = datetime.utcnow().isoformat() + "Z"

    if project_ws:
        # Update existing
        project_ws["indexes"] = indexes
        project_ws["projects"] = projects
        project_ws["sync"] = {
            "lastSync": now,
            "autoSync": project_ws.get("sync", {}).get("autoSync", True),
            "syncedBy": "hook:sync-on-summary-change"
        }
    else:
        # Create new
        project_ws = {
            "$schema": f"{rel_path}/schemas/project_workspace_schema.json",
            "projectId": project["id"],
            "projectName": project["name"],
            "workspaceId": workspace_config["id"],
            "workspaceName": workspace_config["name"],
            "workspacePath": rel_path,
            "workspaceAbsolutePath": str(workspace_root),
            "indexes": indexes,
            "projects": projects,
            "projectMap": {
                "path": "project-map.json",
                "resolvePrefix": project["id"]
            },
            "sync": {
                "lastSync": now,
                "autoSync": True,
                "syncedBy": "hook:sync-on-summary-change"
            },
            "metadata": {
                "joinedAt": now,
                "schemaVersion": "1.0.0"
            }
        }

    return save_json(project_ws_path, project_ws)


def main():
    if len(sys.argv) < 2:
        print("Usage: sync-on-summary-change.py <changed-file-path>", file=sys.stderr)
        sys.exit(1)

    changed_file = Path(sys.argv[1])

    # Find workspace root
    workspace_root = find_workspace_root(changed_file.parent)
    if not workspace_root:
        # Not in a workspace context, nothing to sync
        sys.exit(0)

    # Load workspace configuration
    workspace_config = load_json(workspace_root / "workspace.json")
    if not workspace_config:
        print("Could not load workspace.json", file=sys.stderr)
        sys.exit(1)

    # Check if sync is enabled
    if not workspace_config.get("settings", {}).get("syncOnChange", True):
        sys.exit(0)

    # Sync to all projects
    projects = workspace_config.get("projects", [])
    if not projects:
        sys.exit(0)

    success_count = 0
    for project in projects:
        if sync_project(workspace_root, workspace_config, project):
            success_count += 1

    print(f"Synced indexes to {success_count}/{len(projects)} projects")
    sys.exit(0)


if __name__ == "__main__":
    main()
