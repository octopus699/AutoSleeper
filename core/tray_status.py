"""Build the system-tray status text without depending on Qt.

The window remains the source of truth for timer state, active language and
shutdown mode. No extra timer or background worker is needed here.
"""

from dataclasses import dataclass
import math
import time
from collections.abc import Callable


@dataclass(frozen=True)
class TrayDisplay:
    message: str
    can_cancel: bool
    remaining_seconds: int | None


# These are existing translation keys, supplied by ui/translations.py.
# Other transient UI errors are represented as "No active timer" in the tray.
FINAL_STATUS_KEYS = frozenset({
    "timer_cancelled",
    "timer_finished",
    "sleep_cancelled",
    "shutdown_requested",
    "shutdown_failed_status",
})


def format_remaining(seconds: int) -> str:
    """Format a remaining duration without wrapping at 24 hours."""
    if seconds < 0:
        raise ValueError("Remaining seconds must not be negative")

    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def build_tray_display(
    *,
    deadline: float | None,
    status_key: str,
    real_enabled: bool,
    translate: Callable[..., str],
    now: float | None = None,
) -> TrayDisplay:
    """Return the status for tooltip and tray menu, using the current language.

    The existing MainWindow calls TrayManager.refresh() on every countdown
    tick (~250 ms). The tray manager updates Qt only if the text has changed.
    """
    if deadline is not None:
        current = time.monotonic() if now is None else now
        remaining = max(0, math.ceil(deadline - current))
        key = "tray_remaining_real" if real_enabled else "tray_remaining"
        return TrayDisplay(
            message=translate(key, time=format_remaining(remaining)),
            can_cancel=True,
            remaining_seconds=remaining,
        )

    message_key = status_key if status_key in FINAL_STATUS_KEYS else "tray_idle"
    return TrayDisplay(
        message=translate(message_key),
        can_cancel=False,
        remaining_seconds=None,
    )
