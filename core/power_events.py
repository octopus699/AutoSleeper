"""Receive Windows power broadcasts. No additional Python packages required."""

import ctypes
import os
from ctypes import wintypes
from typing import Callable

from PySide6.QtCore import QAbstractNativeEventFilter

WM_POWERBROADCAST = 0x0218
PBT_APMSUSPEND = 0x0004
PBT_APMRESUMESUSPEND = 0x0007
PBT_APMRESUMEAUTOMATIC = 0x0012


class WindowsPowerEvents(QAbstractNativeEventFilter):
    def __init__(self, on_suspend: Callable[[], None], on_resume: Callable[[], None]):
        super().__init__()
        self.on_suspend = on_suspend
        self.on_resume = on_resume

    def nativeEventFilter(self, event_type, message):
        if os.name != "nt" or bytes(event_type) not in (
            b"windows_generic_MSG",
            b"windows_dispatcher_MSG",
        ):
            return False, 0

        try:
            address = int(message)
            if address == 0:
                return False, 0
            native_msg = ctypes.cast(
                ctypes.c_void_p(address), ctypes.POINTER(wintypes.MSG)
            ).contents
        except (TypeError, ValueError, OSError):
            return False, 0

        if native_msg.message != WM_POWERBROADCAST:
            return False, 0

        if native_msg.wParam == PBT_APMSUSPEND:
            self.on_suspend()
        elif native_msg.wParam in (PBT_APMRESUMESUSPEND, PBT_APMRESUMEAUTOMATIC):
            self.on_resume()

        # Do not consume the native message: Windows and Qt still need to handle it.
        return False, 0
