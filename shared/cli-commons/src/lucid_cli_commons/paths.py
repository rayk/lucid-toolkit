"""
Path resolution and workspace constants.
Ensures consistent path handling across all hooks.
"""
from pathlib import Path
from typing import Optional


class WorkspacePaths:
    """
    Centralized path management for Claude Code hooks.
    All paths are resolved relative to workspace root.
    """

    def __init__(self, workspace_root: Optional[Path] = None):
        """
        Initialize workspace paths.

        Args:
            workspace_root: Override workspace root (defaults to git repo root)
        """
        if workspace_root:
            self.workspace_root = Path(workspace_root).resolve()
        else:
            self.workspace_root = self._find_workspace_root()

    def _find_workspace_root(self) -> Path:
        """
        Find workspace root by searching for .git directory.

        Returns:
            Path to workspace root
        """
        current = Path.cwd()

        # Walk up directory tree looking for .git
        for parent in [current] + list(current.parents):
            if (parent / ".git").exists():
                return parent

        # Fallback to current working directory
        return current

    @property
    def sessions_file(self) -> Path:
        """Path to sessions_summary.json"""
        return self.workspace_root / "status" / "sessions_summary.json"

    @property
    def sessions_lock(self) -> Path:
        """Path to sessions lock file"""
        return self.workspace_root / "status" / ".sessions_summary.lock"

    @property
    def sessions_schema(self) -> Path:
        """Path to session summary schema"""
        return self.workspace_root / ".claude" / "schema" / "session_summary_schema.json"

    @property
    def project_map(self) -> Path:
        """Path to project_map.json"""
        return self.workspace_root / "project_map.json"

    @property
    def capability_summary(self) -> Path:
        """Path to capability_summary.json"""
        return self.workspace_root / "status" / "capability_summary.json"

    @property
    def outcome_summary(self) -> Path:
        """Path to outcome_summary.json"""
        return self.workspace_root / "status" / "outcome_summary.json"

    @property
    def capability_snapshot(self) -> Path:
        """Path to pre-computed capability_snapshot.md"""
        return self.workspace_root / "status" / "capability_snapshot.md"

    @property
    def plan_logs_dir(self) -> Path:
        """Path to plan execution logs."""
        return Path.home() / ".claude" / "plan-logs"

    def worktree_dir_for_plan(self, plan_file: Path) -> Path:
        """
        Derive worktree directory from plan file location.

        Args:
            plan_file: Path to plan.md file

        Returns:
            Path: Sibling 'tree/' directory
        """
        return plan_file.parent / "tree"

    def outcome_track(self, outcome_id: int, state: str) -> Path:
        """
        Construct path to outcome_track.json.

        Args:
            outcome_id: Numeric outcome ID (e.g., 1)
            state: Outcome state (queued, in-progress, completed)

        Returns:
            Path to outcome_track.json (may not exist yet)

        Raises:
            ValueError: If outcomes directory doesn't exist, no outcome found,
                       or multiple outcomes match the ID
        """
        outcomes_dir = self.workspace_root / "outcomes" / state

        if not outcomes_dir.exists():
            raise ValueError(f"Outcomes directory does not exist: {outcomes_dir}")

        # Find outcome directory matching ID
        pattern = f"{outcome_id:03d}-*"
        matches = list(outcomes_dir.glob(pattern))

        if not matches:
            raise ValueError(f"No outcome found with ID {outcome_id} in state {state}")

        if len(matches) > 1:
            raise ValueError(f"Multiple outcomes found with ID {outcome_id} in state {state}")

        return matches[0] / "outcome_track.json"


# Global instance for convenience
_paths: Optional[WorkspacePaths] = None


def get_paths(workspace_root: Optional[Path] = None) -> WorkspacePaths:
    """
    Get global WorkspacePaths instance.

    Args:
        workspace_root: Override workspace root (only used on first call)

    Returns:
        WorkspacePaths instance
    """
    global _paths

    if _paths is None:
        _paths = WorkspacePaths(workspace_root)

    return _paths
