"""Windows shutdown backend. Never schedules a future OS-level shutdown.

Test mode is ALWAYS the default. The user must explicitly opt in for each
application launch; no live-mode setting is stored on disk.
"""

import os
import subprocess


class ShutdownExecutionError(RuntimeError):
    """Windows rejected or did not complete the shutdown command."""


class ShutdownManager:
    def __init__(self):
        self._real_enabled = True

    @property
    def real_enabled(self) -> bool:
        return self._real_enabled

    def set_real_mode(self, enabled: bool) -> None:
        self._real_enabled = bool(enabled)

    def request_shutdown(self) -> bool:
        """Request immediate Windows shutdown; return False in safe test mode.

        This command is invoked ONLY after Python's countdown expires. /f is
        deliberately omitted: Windows may prompt about unsaved applications.
        """
        if not self._real_enabled:
            return False

        if os.name != "nt":
            raise ShutdownExecutionError("Real shutdown is supported only on Windows.")

        try:
            result = subprocess.run(
                ["shutdown.exe", "/s", "/t", "0"],
                check=False,
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ShutdownExecutionError(str(exc)) from exc

        if result.returncode != 0:
            details = (result.stderr or result.stdout or "").strip()
            raise ShutdownExecutionError(
                details or f"shutdown.exe returned exit code {result.returncode}"
            )

        return True
