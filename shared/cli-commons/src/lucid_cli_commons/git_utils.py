"""
Git repository information utilities.
Captures branch, commit, and status information.
"""
import subprocess
from pathlib import Path
from typing import Optional


class GitInfo:
    """
    Captures git repository information.

    Safe to use in both git and non-git environments.
    """

    def __init__(self, cwd: Optional[Path] = None):
        """
        Initialize git info capture.

        Args:
            cwd: Working directory (defaults to current directory)
        """
        self.cwd = cwd or Path.cwd()
        self._branch: Optional[str] = None
        self._commit_hash: Optional[str] = None
        self._is_git_repo = self._check_git_repo()

    def _check_git_repo(self) -> bool:
        """Check if current directory is in a git repository."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.cwd,
                capture_output=True,
                check=False
            )
            return result.returncode == 0
        except Exception:
            return False

    def _run_git(self, *args) -> Optional[str]:
        """
        Run git command and return output.

        Returns None if not a git repo or command fails.
        """
        if not self._is_git_repo:
            return None

        try:
            result = subprocess.run(
                ["git"] + list(args),
                cwd=self.cwd,
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except Exception:
            return None

    @property
    def branch(self) -> Optional[str]:
        """Current git branch name, or None if not in git repo."""
        if self._branch is None:
            self._branch = self._run_git("rev-parse", "--abbrev-ref", "HEAD")
        return self._branch

    @property
    def commit_hash(self) -> Optional[str]:
        """Current commit SHA, or None if not in git repo."""
        if self._commit_hash is None:
            self._commit_hash = self._run_git("rev-parse", "HEAD")
        return self._commit_hash

    @property
    def is_clean(self) -> bool:
        """True if working tree is clean (no uncommitted changes)."""
        status = self._run_git("status", "--porcelain")
        if status is None:
            return True  # Not a git repo = considered clean
        return len(status) == 0

    @property
    def uncommitted_count(self) -> int:
        """Number of files with uncommitted changes."""
        status = self._run_git("status", "--porcelain")
        if status is None:
            return 0
        lines = [line for line in status.split("\n") if line.strip()]
        return len(lines)

    @property
    def last_commit_message(self) -> Optional[str]:
        """Get last commit message from HEAD."""
        if not self._is_git_repo:
            return None
        return self._run_git("show", "-s", "--format=%B", "HEAD")

    def create_worktree(self, path: Path, branch: str, base_ref: str = "HEAD") -> bool:
        """
        Create a git worktree with a new branch.

        Args:
            path: Directory for worktree
            branch: New branch name to create
            base_ref: Starting point for branch (default: HEAD)

        Returns:
            bool: True if successful

        Raises:
            subprocess.CalledProcessError: If git command fails
        """
        if not self._is_git_repo:
            return False

        result = subprocess.run(
            ["git", "worktree", "add", "-b", branch, str(path), base_ref],
            cwd=self.cwd,
            capture_output=True,
            text=True,
        )
        return result.returncode == 0

    def remove_worktree(self, path: Path, force: bool = False) -> bool:
        """
        Remove a git worktree.

        Args:
            path: Worktree directory to remove
            force: Force removal even if dirty

        Returns:
            bool: True if successful
        """
        if not self._is_git_repo:
            return False

        cmd = ["git", "worktree", "remove", str(path)]
        if force:
            cmd.append("--force")

        result = subprocess.run(cmd, cwd=self.cwd, capture_output=True)
        return result.returncode == 0

    def list_worktrees(self) -> list[dict]:
        """
        List all worktrees in repository.

        Returns:
            List of dicts with keys: path, branch, commit
        """
        if not self._is_git_repo:
            return []

        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            cwd=self.cwd,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return []

        worktrees = []
        current = {}

        for line in result.stdout.strip().split("\n"):
            if line.startswith("worktree "):
                if current:
                    worktrees.append(current)
                current = {"path": line[9:]}
            elif line.startswith("HEAD "):
                current["commit"] = line[5:]
            elif line.startswith("branch "):
                # branch refs/heads/name -> name
                branch_ref = line[7:]
                current["branch"] = branch_ref.replace("refs/heads/", "")
            elif line == "bare":
                current["bare"] = True
            elif line == "detached":
                current["detached"] = True

        if current:
            worktrees.append(current)

        return worktrees
