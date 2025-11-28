#!/usr/bin/env python3
"""Pre-commit validation hook for workspace integrity.

Validates workspace configuration and cross-references before commits
to ensure workspace state remains consistent.
"""

import json
import sys
from pathlib import Path
from typing import Optional


def find_workspace_root() -> Optional[Path]:
    """Find workspace root by looking for .lucid directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".lucid").exists():
            return current
        current = current.parent
    return None


def validate_workspace_schema(workspace_path: Path) -> list[str]:
    """Validate workspace.json against schema."""
    errors = []
    workspace_file = workspace_path / ".lucid" / "workspace.json"

    if not workspace_file.exists():
        return []  # No workspace configured, skip validation

    try:
        with open(workspace_file) as f:
            workspace = json.load(f)

        # Required fields
        required = ["id", "name", "type", "projects"]
        for field in required:
            if field not in workspace:
                errors.append(f"Missing required field: {field}")

        # Validate projects
        projects = workspace.get("projects", [])
        if not projects:
            errors.append("Workspace must have at least one project")

        project_ids = set()
        for project in projects:
            pid = project.get("id")
            if not pid:
                errors.append("Project missing required 'id' field")
            elif pid in project_ids:
                errors.append(f"Duplicate project id: {pid}")
            else:
                project_ids.add(pid)

            # Check path exists
            project_path = project.get("path")
            if project_path:
                full_path = workspace_path / project_path
                if not full_path.exists():
                    errors.append(f"Project path does not exist: {project_path}")

    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in workspace.json: {e}")
    except Exception as e:
        errors.append(f"Error reading workspace.json: {e}")

    return errors


def validate_cross_references(workspace_path: Path) -> list[str]:
    """Validate cross-references between workspace projects."""
    errors = []
    workspace_file = workspace_path / ".lucid" / "workspace.json"

    if not workspace_file.exists():
        return []

    try:
        with open(workspace_file) as f:
            workspace = json.load(f)

        projects = workspace.get("projects", [])
        project_ids = {p.get("id") for p in projects if p.get("id")}

        # Check dependencies reference valid projects
        for project in projects:
            deps = project.get("dependencies", [])
            for dep in deps:
                if dep not in project_ids:
                    errors.append(
                        f"Project '{project.get('id')}' references unknown dependency: {dep}"
                    )

    except Exception as e:
        errors.append(f"Error validating cross-references: {e}")

    return errors


def main() -> int:
    """Execute pre-commit validation hook."""
    workspace_root = find_workspace_root()

    if not workspace_root:
        # Not in a workspace, skip validation
        return 0

    errors = []
    errors.extend(validate_workspace_schema(workspace_root))
    errors.extend(validate_cross_references(workspace_root))

    if errors:
        print("Workspace validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print("Workspace validation passed", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
