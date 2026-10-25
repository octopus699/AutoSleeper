"""Entry point for AutoSleeper. Shutdown is disabled during this development phase."""

import os
import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from core.power_events import WindowsPowerEvents
from core.tray_manager import TrayManager
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    root = Path(__file__).resolve().parent

    qss_path = root / "ui" / "styles.qss"
    if qss_path.exists():
        app.setStyleSheet(qss_path.read_text(encoding="utf-8"))

    icon_path = root / "assets" / "AutoSleeper_black.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow()
    if icon_path.exists():
        window.setWindowIcon(QIcon(str(icon_path)))

    tray = TrayManager(app, window)
    window.tray_manager = tray

    if tray.available:
        app.setQuitOnLastWindowClosed(False)

    power_events = None
    if os.name == "nt":
        power_events = WindowsPowerEvents(
            on_suspend=window.cancel_due_to_sleep,
            on_resume=window.cancel_due_to_sleep,
        )
        app.installNativeEventFilter(power_events)

    window.show()
    result = app.exec()

    if power_events is not None:
        app.removeNativeEventFilter(power_events)

    return result


if __name__ == "__main__":
    sys.exit(main())
