"""
workspace_info.core - Core WorkspaceInfo class for managing workspace-info.toon files.
"""
from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TYPE_CHECKING

from lucid_cli_commons.toon_parser import parse_toon, to_toon
from lucid_cli_commons.locking import atomic_write

from .constants import WORKSPACE_INFO_PATH, DEFAULTS, VALID_ACTION_STATUS

if TYPE_CHECKING:
    from .hook import HookContext


class WorkspaceInfo:
    """
    Manage workspace-info.toon file.

    This class provides read/write access to workspace-info.toon,
    which tracks workspace state including projects, capabilities,
    outcomes, and current focus.
    """

    def __init__(self, workspace_root: Path | str | None = None):
        """Initialize with workspace root."""
        if workspace_root is not None:
            self.workspace_root = Path(workspace_root)
        else:
            self.workspace_root = self._find_workspace_root()

        self.file_path = self.workspace_root / WORKSPACE_INFO_PATH

    @staticmethod
    def _find_workspace_root(start: Path = None) -> Path:
        """Search upward for .claude/ directory."""
        current = start or Path.cwd()
        while current != current.parent:
            if (current / '.claude').is_dir():
                return current
            current = current.parent
        raise ValueError(
            f"Could not find workspace root (.claude/ directory) "
            f"starting from {start or Path.cwd()}"
        )

    # --- File Operations ---
    def exists(self) -> bool:
        """Check if workspace-info.toon exists."""
        return self.file_path.exists()

    def load(self) -> dict:
        """
        Load and parse workspace-info.toon.

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is corrupted
        """
        if not self.exists():
            raise FileNotFoundError(f"workspace-info.toon not found at {self.file_path}")

        try:
            content = self.file_path.read_text()
            return parse_toon(content)
        except Exception as e:
            raise ValueError(f"Failed to parse workspace-info.toon: {e}") from e

    def save(self, data: dict) -> None:
        """
        Save data to workspace-info.toon atomically.

        Creates .claude/ directory if it doesn't exist.
        Uses atomic_write for concurrent safety.
        """
        # Ensure .claude directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to TOON and write atomically
        content = to_toon(data)
        with atomic_write(self.file_path) as f:
            f.write(content)

    def create(self, workspace_name: str, repo_url: str | None = None) -> dict:
        """
        Create new workspace-info.toon with defaults.

        Args:
            workspace_name: Name for the workspace
            repo_url: Git repository URL (auto-detected if None)

        Returns:
            The created data structure
        """
        now = datetime.now(timezone.utc).isoformat()

        data = DEFAULTS.copy()
        data["@id"] = f"workspace/{workspace_name}"
        data["dateCreated"] = now
        data["dateModified"] = now
        data["workspace.name"] = workspace_name
        data["workspace.codeRepository"] = repo_url or self._get_git_remote()
        data["workspace.version"] = self._get_git_commit()
        data["workspace.dateModified"] = self._get_git_commit_date()

        # Add outcome summary rows
        data["outcomes.summary"] = [
            {"stage": "queued", "count": 0, "path": "outcomes/queued/"},
            {"stage": "ready", "count": 0, "path": "outcomes/ready/"},
            {"stage": "in-progress", "count": 0, "path": "outcomes/in-progress/"},
            {"stage": "blocked", "count": 0, "path": "outcomes/blocked/"},
            {"stage": "completed", "count": 0, "path": "outcomes/completed/"},
        ]

        self.save(data)
        return data

    # --- Generic Field Access ---
    def get(self, path: str) -> Any:
        """
        Get field by dot-notation path.

        Args:
            path: Dot-notation path (e.g., "focus.name", "workspace.version")

        Returns:
            Field value

        Raises:
            FileNotFoundError: If workspace-info.toon doesn't exist
            KeyError: If path doesn't match any field
        """
        data = self.load()

        # Direct key match (e.g., "@context", "dateModified")
        if path in data:
            return data[path]

        raise KeyError(f"Path '{path}' not found in workspace-info.toon")

    def set(self, path: str, value: Any) -> None:
        """Set field by dot-notation path."""
        data = self.load()
        data[path] = value
        data["dateModified"] = datetime.now(timezone.utc).isoformat()
        self.save(data)

    # --- Focus Management ---
    def set_focus(self, name: str | None, target: str | None, status: str = "ActiveActionStatus") -> None:
        """
        Set the current focus.

        Args:
            name: Outcome name (e.g., "005-my-outcome")
            target: Path to outcome (e.g., "outcomes/in-progress/005-my-outcome")
            status: Action status (default: "ActiveActionStatus")

        Raises:
            ValueError: If status is not a valid ActionStatusType
        """
        if status not in VALID_ACTION_STATUS:
            raise ValueError(
                f"Invalid actionStatus '{status}'. "
                f"Must be one of: {', '.join(sorted(VALID_ACTION_STATUS))}"
            )

        data = self.load()
        data["focus.name"] = name
        data["focus.target"] = target
        data["focus.actionStatus"] = status
        data["dateModified"] = datetime.now(timezone.utc).isoformat()
        self.save(data)

    def clear_focus(self) -> None:
        """
        Clear the current focus.

        Sets:
            focus.name = None
            focus.target = None
            focus.actionStatus = "PotentialActionStatus"
        """
        self.set_focus(None, None, "PotentialActionStatus")

    # --- Session Tracking ---
    def record_session(self, ctx: 'HookContext') -> None:
        """
        Record session info from hook context.

        Updates lastSession.id, lastSession.timestamp, lastSession.event.
        """
        data = self.load()
        data["lastSession.id"] = ctx.session_id
        data["lastSession.timestamp"] = datetime.now(timezone.utc).isoformat()
        data["lastSession.event"] = ctx.hook_event
        data["dateModified"] = data["lastSession.timestamp"]
        self.save(data)

    # --- Convenience Methods ---
    def update_timestamp(self) -> None:
        """Update dateModified to current time."""
        data = self.load()
        data["dateModified"] = datetime.now(timezone.utc).isoformat()
        self.save(data)

    def update_git_info(self, timeout: int = 5) -> None:
        """
        Update workspace.version and workspace.dateModified from git.

        Args:
            timeout: Maximum seconds to wait for git commands.

        Notes:
            - Silently skips if git fails or times out
            - Does not raise exceptions
        """
        try:
            commit = self._get_git_commit(timeout)
            commit_date = self._get_git_commit_date(timeout)

            if commit:
                data = self.load()
                data["workspace.version"] = commit
                if commit_date:
                    data["workspace.dateModified"] = commit_date
                data["dateModified"] = datetime.now(timezone.utc).isoformat()
                self.save(data)
        except Exception:
            pass  # Silently skip on any error

    # --- Git Helpers ---
    def _get_git_commit(self, timeout: int = 5) -> str | None:
        """Get current git commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    def _get_git_commit_date(self, timeout: int = 5) -> str | None:
        """Get current git commit date in ISO format."""
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%cI"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    def _get_git_remote(self, timeout: int = 5) -> str | None:
        """Get git remote URL."""
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    # --- Section Readers ---
    def get_metadata(self) -> dict:
        """Get metadata fields (@context, @type, @id, dates, version)."""
        data = self.load()
        return {
            "@context": data.get("@context"),
            "@type": data.get("@type"),
            "@id": data.get("@id"),
            "dateCreated": data.get("dateCreated"),
            "dateModified": data.get("dateModified"),
            "softwareVersion": data.get("softwareVersion"),
        }

    def get_workspace(self) -> dict:
        """Get workspace section fields."""
        data = self.load()
        return {
            "@type": data.get("workspace@type"),
            "name": data.get("workspace.name"),
            "codeRepository": data.get("workspace.codeRepository"),
            "version": data.get("workspace.version"),
            "dateModified": data.get("workspace.dateModified"),
        }

    def get_projects(self) -> list[dict]:
        """Get list.md of projects from tabular array."""
        data = self.load()
        return data.get("project", [])

    def get_capabilities(self) -> list[dict]:
        """Get list.md of capabilities from tabular array."""
        data = self.load()
        return data.get("capability", [])

    def get_outcomes(self) -> dict:
        """Get outcomes summary by stage."""
        data = self.load()
        summary = data.get("outcomes.summary", [])
        # Convert list.md to dict keyed by stage
        return {item["stage"]: item for item in summary}

    def get_focus(self) -> dict:
        """Get focus section fields."""
        data = self.load()
        return {
            "@type": data.get("focus@type"),
            "name": data.get("focus.name"),
            "target": data.get("focus.target"),
            "actionStatus": data.get("focus.actionStatus"),
        }

    def get_ide(self) -> dict:
        """Get IDE configuration."""
        data = self.load()
        return {
            "@type": data.get("ide@type"),
            "name": data.get("ide.name"),
            "configPath": data.get("ide.configPath"),
            "sdkName": data.get("ide.sdkName"),
            "languageLevel": data.get("ide.languageLevel"),
            "modules": data.get("ide.modules", []),
            "vcsRoots": data.get("ide.vcsRoots", []),
        }

    # --- Section Writers ---
    def set_metadata(self, **kwargs) -> None:
        """Update metadata fields."""
        data = self.load()
        for key, value in kwargs.items():
            if key in ("@context", "@type", "@id", "dateCreated", "dateModified", "softwareVersion"):
                data[key] = value
        data["dateModified"] = datetime.now(timezone.utc).isoformat()
        self.save(data)

    def set_workspace(self, **kwargs) -> None:
        """Update workspace section fields."""
        data = self.load()
        field_map = {
            "name": "workspace.name",
            "codeRepository": "workspace.codeRepository",
            "version": "workspace.version",
            "dateModified": "workspace.dateModified",
        }
        for key, value in kwargs.items():
            if key in field_map:
                data[field_map[key]] = value
        data["dateModified"] = datetime.now(timezone.utc).isoformat()
        self.save(data)

    def set_projects(self, projects: list[dict]) -> None:
        """Set the projects list.md."""
        data = self.load()
        data["project"] = projects
        data["projects.numberOfItems"] = len(projects)
        data["dateModified"] = datetime.now(timezone.utc).isoformat()
        self.save(data)

    def set_capabilities(self, capabilities: list[dict]) -> None:
        """Set the capabilities list.md."""
        data = self.load()
        data["capability"] = capabilities
        data["capabilities.numberOfItems"] = len(capabilities)
        data["dateModified"] = datetime.now(timezone.utc).isoformat()
        self.save(data)

    def set_outcomes(self, summary: dict) -> None:
        """Set outcome counts by stage."""
        data = self.load()
        # Convert dict back to list.md format
        stages = ["queued", "ready", "in-progress", "blocked", "completed"]
        data["outcomes.summary"] = [
            {"stage": stage, "count": summary.get(stage, {}).get("count", 0),
             "path": summary.get(stage, {}).get("path", f"outcomes/{stage}/")}
            for stage in stages
        ]
        data["dateModified"] = datetime.now(timezone.utc).isoformat()
        self.save(data)

    def set_ide(self, **kwargs) -> None:
        """Update IDE configuration."""
        data = self.load()
        field_map = {
            "name": "ide.name",
            "configPath": "ide.configPath",
            "sdkName": "ide.sdkName",
            "languageLevel": "ide.languageLevel",
        }
        for key, value in kwargs.items():
            if key in field_map:
                data[field_map[key]] = value
            elif key == "modules":
                data["ide.modules"] = value
            elif key == "vcsRoots":
                data["ide.vcsRoots"] = value
        data["dateModified"] = datetime.now(timezone.utc).isoformat()
        self.save(data)

    # --- Convenience Methods for Collections ---
    def add_project(self, project: dict) -> None:
        """Add a project to the projects list.md."""
        projects = self.get_projects()
        # Check if project already exists by name
        existing = [p for p in projects if p.get("name") != project.get("name")]
        existing.append(project)
        self.set_projects(existing)

    def remove_project(self, name: str) -> None:
        """Remove a project by name."""
        projects = self.get_projects()
        filtered = [p for p in projects if p.get("name") != name]
        self.set_projects(filtered)

    def add_capability(self, capability: dict) -> None:
        """Add a capability to the capabilities list.md."""
        capabilities = self.get_capabilities()
        # Check if capability already exists by identifier
        existing = [c for c in capabilities if c.get("identifier") != capability.get("identifier")]
        existing.append(capability)
        self.set_capabilities(existing)

    def update_capability_maturity(self, identifier: str, maturity: int) -> None:
        """Update a capability's maturity level."""
        capabilities = self.get_capabilities()
        for cap in capabilities:
            if cap.get("identifier") == identifier:
                cap["maturityLevel"] = maturity
                break
        self.set_capabilities(capabilities)

    def update_outcome_counts(self, counts: dict) -> None:
        """Update outcome counts by stage.

        Args:
            counts: Dict mapping stage name to count, e.g., {"queued": 5, "completed": 10}
        """
        outcomes = self.get_outcomes()
        for stage, count in counts.items():
            if stage in outcomes:
                outcomes[stage]["count"] = count
            else:
                outcomes[stage] = {"count": count, "path": f"outcomes/{stage}/"}
        self.set_outcomes(outcomes)
