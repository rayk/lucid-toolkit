"""
macOS notification support via terminal-notifier.
Provides non-blocking notifications for plan execution completion.
"""
import shutil
import subprocess


class Notifier:
    """macOS notification support via terminal-notifier."""

    @staticmethod
    def is_available() -> bool:
        """
        Check if terminal-notifier is installed.

        Returns:
            bool: True if terminal-notifier found in PATH
        """
        return shutil.which("terminal-notifier") is not None

    @staticmethod
    def notify(
        title: str,
        message: str,
        subtitle: str | None = None,
        sound: str = "Glass",
        group: str = "claude-plan",
    ) -> bool:
        """
        Send macOS notification.

        Args:
            title: Notification title
            message: Notification body
            subtitle: Optional subtitle
            sound: Sound name (Glass, Basso, etc.)
            group: Notification group ID for coalescing

        Returns:
            bool: True if notification sent, False if unavailable
        """
        if not Notifier.is_available():
            return False

        cmd = [
            "terminal-notifier",
            "-title", title,
            "-message", message,
            "-sound", sound,
            "-group", group,
        ]

        if subtitle:
            cmd.extend(["-subtitle", subtitle])

        result = subprocess.run(cmd, capture_output=True)
        return result.returncode == 0
