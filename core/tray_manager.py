"""System tray integration for AutoSleeper (Windows desktop)."""

import math
import time
from pathlib import Path
from core.tray_status import build_tray_display

from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QStyle, QSystemTrayIcon


class TrayManager(QObject):
    def __init__(self, app: QApplication, window):
        super().__init__(window)

        self.app = app
        self.window = window
        self.available = QSystemTrayIcon.isSystemTrayAvailable()

        self.tray_icon = QSystemTrayIcon(self)
        icon_path = Path(__file__).resolve().parent.parent / "assets" / "logo.png"
        icon = QIcon(str(icon_path)) if icon_path.exists() else QIcon()

        if icon.isNull():
            icon = window.windowIcon()
        if icon.isNull():
            icon = app.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)

        self.tray_icon.setIcon(icon)
        self.menu = QMenu()
        self.menu.setStyleSheet("""
            QMenu {
                background: #202020;
                color: #F2F2F2;
                border: 1px solid #343434;
                padding: 5px;
            }
            QMenu::item {
                padding: 7px 22px;
            }
            QMenu::item:selected {
                background: #153822;
                color: #00FF41;
            }
            QMenu::item:disabled {
                color: #777777;
            }
        """)

        self.status_action = QAction(self.menu)
        self.status_action.setEnabled(False)

        self.open_action = QAction(self.menu)
        self.cancel_action = QAction(self.menu)
        self.exit_action = QAction(self.menu)

        self.open_action.triggered.connect(self.open_window)
        self.cancel_action.triggered.connect(self.cancel_timer)
        self.exit_action.triggered.connect(self.exit_application)

        self.menu.addAction(self.status_action)
        self.menu.addSeparator()
        self.menu.addAction(self.open_action)
        self.menu.addAction(self.cancel_action)
        self.menu.addSeparator()
        self.menu.addAction(self.exit_action)

        self.menu.aboutToShow.connect(self.refresh)
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.activated.connect(self.on_activated)
        self.refresh()

        if self.available:
            self.tray_icon.show()

    def on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.open_window()

    def open_window(self):
        self.window.showNormal()
        self.window.raise_()
        self.window.activateWindow()

    def cancel_timer(self):
        if self.window.deadline is not None:
            self.window.cancel_timer()
        self.refresh()

    def exit_application(self):
        # Exit always cancels the countdown before terminating the process.
        if self.window.deadline is not None:
            self.window.cancel_timer()
        self.window._allow_close = True
        self.tray_icon.hide()
        self.app.quit()

    def refresh(self):
        """Update tray texts; only touch Qt when the displayed value changes."""
        labels = (
            (self.open_action, self.window.t("tray_open")),
            (self.cancel_action, self.window.t("tray_cancel")),
            (self.exit_action, self.window.t("tray_exit")),
        )
        for action, label in labels:
            if action.text() != label:
                action.setText(label)

        display = build_tray_display(
            deadline=self.window.deadline,
            status_key=self.window.status_key,
            real_enabled=self.window.shutdown_manager.real_enabled,
            translate=self.window.t,
        )

        if self.cancel_action.isEnabled() != display.can_cancel:
            self.cancel_action.setEnabled(display.can_cancel)

        if self.status_action.text() != display.message:
            self.status_action.setText(display.message)

        tooltip = f"AutoSleeper - {display.message}"
        if self.tray_icon.toolTip() != tooltip:
            self.tray_icon.setToolTip(tooltip)
