"""
File locking utilities for hook scripts.

Provides thread-safe and process-safe file locking using the filelock library.
"""
import time
from pathlib import Path
from filelock import FileLock, Timeout
from typing import Optional
from contextlib import contextmanager


class FileLockManager:
    """
    Context manager for file-based locking.

    Uses filelock library for cross-platform, cross-process locking.

    Usage:
        with FileLockManager('/path/to/file.lock', timeout=30):
            # Do work with exclusive access
            pass
    """

    def __init__(self, lock_path: Path | str, timeout: int = 30):
        """
        Initialize lock manager.

        Args:
            lock_path: Path to lock file (will have .lock appended if needed)
            timeout: Timeout in seconds (default: 30)
        """
        lock_path = Path(lock_path)

        # Ensure .lock extension
        if not str(lock_path).endswith('.lock'):
            lock_path = Path(str(lock_path) + '.lock')

        self.lock_path = lock_path
        self.timeout = timeout
        self.lock = FileLock(str(self.lock_path), timeout=self.timeout)
        self._acquired = False

    def __enter__(self):
        """Acquire lock"""
        try:
            self.lock.acquire(timeout=self.timeout)
            self._acquired = True
            return True
        except Timeout as e:
            raise TimeoutError(
                f"Failed to acquire lock {self.lock_path} within {self.timeout}s"
            ) from e

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release lock"""
        if self._acquired:
            self.lock.release()
            self._acquired = False
        return False  # Don't suppress exceptions


@contextmanager
def atomic_write(
    file_path: Path | str,
    lock_path: Optional[Path | str] = None,
    timeout: int = 30
):
    """
    Context manager for atomic file writes with locking.

    Writes to temporary file first, then renames atomically.
    Uses file locking to prevent concurrent writes.

    Usage:
        with atomic_write('/path/to/file.json') as f:
            json.dump(data, f)

    Args:
        file_path: Path to file to write
        lock_path: Optional lock file path (defaults to file_path + '.lock')
        timeout: Lock timeout in seconds (default: 30)

    Yields:
        File object opened for writing
    """
    file_path = Path(file_path)
    lock_path = Path(lock_path) if lock_path else Path(str(file_path) + '.lock')

    # Ensure parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)

    temp_file = file_path.with_suffix(file_path.suffix + '.tmp')

    with FileLockManager(lock_path, timeout=timeout):
        try:
            with open(temp_file, 'w') as f:
                yield f

            # Atomic rename (POSIX guarantees atomicity)
            temp_file.replace(file_path)
        finally:
            # Clean up temp file if it still exists
            if temp_file.exists():
                temp_file.unlink()
