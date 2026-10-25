"""AutoSleeper application entry point."""

import ctypes
import os
import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from core.bundle_resources import load_qss_with_assets
from core.power_events import WindowsPowerEvents
from core.single_instance import SingleInstanceGuard
from core.tray_manager import TrayManager
from ui.main_window import MainWindow


def main():
    #region WINDOWS APPLICATION IDENTITY

    if sys.platform == "win32":
        app_id = "BlackoutStudios.AutoSleeper"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            ctypes.c_wchar_p(app_id)
        )

    #endregion

    #region APPLICATION

    app = QApplication(sys.argv)
    app.setOrganizationName("BlackoutStudios")
    app.setApplicationName("AutoSleeper")

    root = Path(__file__).resolve().parent

    # Keep the guard alive for the *entire* duration of the application.
    try:
        single_instance = SingleInstanceGuard(app)
    except (OSError, RuntimeError) as exc:
        QMessageBox.critical(None, "AutoSleeper", str(exc))
        return 1

    if not single_instance.is_primary:
        if not single_instance.activate_existing():
            QMessageBox.warning(
                None,
                "AutoSleeper",
                "AutoSleeper is already running, but its window could not "
                "be restored. Check the Windows system tray.",
            )
        return 0

    #endregion

    #region ICON AND STYLES

    icon_path = root / "assets" / "AutoSleeper.ico"
    app_icon = QIcon(str(icon_path)) if icon_path.exists() else QIcon()
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)

    styles = []
    for filename in ("styles.qss", "shutdown_mode_addon.qss"):
        qss_path = root / "ui" / filename
        if qss_path.exists():
            styles.append(load_qss_with_assets(qss_path, root))

    if styles:
        app.setStyleSheet("\n".join(styles))

    #endregion

    #region MAIN WINDOW

    window = MainWindow()
    if not app_icon.isNull():
        window.setWindowIcon(app_icon)

    tray = TrayManager(app, window)
    window.tray_manager = tray

    if tray.available:
        app.setQuitOnLastWindowClosed(False)

    # The second launch uses the SAME restore behavior as the tray menu.
    single_instance.activation_requested.connect(tray.open_window)

    #endregion

    #region WINDOWS POWER EVENTS

    power_events = None
    if os.name == "nt":
        power_events = WindowsPowerEvents(
            on_suspend=window.cancel_due_to_sleep,
            on_resume=window.cancel_due_to_sleep,
        )
        app.installNativeEventFilter(power_events)

    #endregion

    #region EXECUTION

    try:
        window.show()
        return app.exec()
    finally:
        if power_events is not None:
            app.removeNativeEventFilter(power_events)
        single_instance.close()

    #endregion


if __name__ == "__main__":
    sys.exit(main())
