import math
import time
from datetime import datetime, timedelta
from pathlib import Path

from PySide6.QtCore import QPoint, QRect, Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPixmap, QPolygon
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ui.translations import TRANSLATIONS


class LanguageComboBox(QComboBox):
    """Draw a small Matrix-green drop-down triangle over the native arrow."""

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        hovered = self.underMouse()
        background = QColor("#153822" if hovered else "#202020")
        arrow_color = QColor("#00FF41" if hovered else "#00E676")
        center_x = self.width() - 14
        center_y = self.height() // 2

        painter.fillRect(QRect(center_x - 9, center_y - 7, 18, 14), background)
        triangle = QPolygon([
            QPoint(center_x - 5, center_y - 2),
            QPoint(center_x + 5, center_y - 2),
            QPoint(center_x, center_y + 4),
        ])
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(arrow_color)
        painter.drawPolygon(triangle)
        painter.end()

    def enterEvent(self, event):
        super().enterEvent(event)
        self.update()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.update()


class TitleBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("titleBar")
        self.setFixedHeight(40)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            handle = self.window().windowHandle()

            if handle is not None and handle.startSystemMove():
                event.accept()
                return

        super().mousePressEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle("AutoSleeper")
        self.setFixedSize(700, 425)

        self.language = "en"
        self.status_key = "ready"
        self.tray_manager = None
        self._allow_close = False

        self.deadline = None
        self.shutdown_time = None
        self.selected_seconds = 0
        self.custom_hours = 0
        self.custom_minutes = 0
        self.custom_seconds = 0

        self.timer = QTimer(self)
        self.timer.setInterval(250)
        self.timer.timeout.connect(self.update_timer)

        self.build_ui()
        self.apply_language()

    #region INTERFACE

    def build_ui(self):
        container = QWidget()
        self.setCentralWidget(container)

        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Custom title bar
        title_bar = TitleBar(self)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 6, 0)
        title_layout.setSpacing(8)

        title_icon = self.create_logo_label("logo.png", 30)
        title_text = QLabel("AutoSleeper")
        title_text.setObjectName("titleBarText")

        minimize_button = QPushButton("—")
        minimize_button.setObjectName("titleBarButton")
        minimize_button.setFixedSize(38, 36)
        minimize_button.setCursor(Qt.CursorShape.PointingHandCursor)
        minimize_button.clicked.connect(self.showMinimized)

        close_button = QPushButton("✕")
        close_button.setObjectName("titleBarClose")
        close_button.setFixedSize(38, 36)
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.clicked.connect(self.close)

        self.minimize_button = minimize_button
        self.close_button = close_button

        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        title_layout.addWidget(minimize_button)
        title_layout.addWidget(close_button)
        main_layout.addWidget(title_bar)

        # Main content
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 10, 24, 6)
        layout.setSpacing(6)
        main_layout.addWidget(content, 1)

        # Application header used on the default page
        title = QLabel("AutoSleeper")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel()
        subtitle.setObjectName("subtitle")
        subtitle.setProperty("i18n", "subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header_text = QVBoxLayout()
        header_text.setSpacing(2)
        header_text.addWidget(title)
        header_text.addWidget(subtitle)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(16)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.create_logo_label("logo.png", 72))
        header_layout.addLayout(header_text)

        self.default_header = QWidget()
        self.default_header.setLayout(header_layout)

        self.header_stack = QStackedWidget()
        self.header_stack.setFixedHeight(85)
        self.header_stack.addWidget(self.default_header)

        self.custom_header = QLabel()
        self.custom_header.setObjectName("dynamicHeader")
        self.custom_header.setProperty("i18n", "custom_title")
        self.custom_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_stack.addWidget(self.custom_header)

        self.running_header = QLabel()
        self.running_header.setObjectName("dynamicHeader")
        self.running_header.setProperty("i18n", "running_title")
        self.running_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_stack.addWidget(self.running_header)

        # Language selector: top-right, balanced to keep the header centered
        self.language_combo = LanguageComboBox()
        self.language_combo.setObjectName("languageSelector")
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("Español", "es")
        self.language_combo.setFixedSize(112, 36)
        self.language_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.language_combo.setCurrentIndex(
            self.language_combo.findData(self.language)
        )
        self.language_combo.currentIndexChanged.connect(self.change_language)

        language_layout = QVBoxLayout()
        language_layout.setContentsMargins(0, 10, 0, 0)
        language_layout.setSpacing(0)
        language_layout.addWidget(self.language_combo)
        language_layout.addStretch()

        left_spacer = QWidget()
        left_spacer.setFixedWidth(112)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(0)
        header_row.addWidget(left_spacer)
        header_row.addWidget(self.header_stack, 1)
        header_row.addLayout(language_layout)
        layout.addLayout(header_row)

        # Pages: default, custom, running
        self.stack = QStackedWidget()
        self.build_default_page()
        self.build_custom_page()
        self.build_running_page()
        self.stack.currentChanged.connect(self.on_page_changed)
        layout.addWidget(self.stack, 1)

        self.status_label = QLabel()
        self.status_label.setObjectName("status")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Footer (brand name is deliberately not translated)
        footer = QFrame()
        footer.setObjectName("footer")
        footer.setFixedHeight(34)

        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 0, 7, 0)
        footer_layout.setSpacing(4)

        footer_label = QLabel("Blackout Studios 2026")
        footer_label.setObjectName("footerText")
        footer_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        footer_layout.addStretch()
        footer_layout.addWidget(footer_label)
        footer_layout.addWidget(
            self.create_logo_label("blackout_logo.png", 26, "companyLogo")
        )
        main_layout.addWidget(footer)

    def create_logo_label(self, filename, size, object_name=None):
        logo = QLabel()
        logo.setFixedSize(size, size)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if object_name is not None:
            logo.setObjectName(object_name)

        logo_path = Path(__file__).resolve().parent.parent / "assets" / filename
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            if not pixmap.isNull():
                logo.setPixmap(
                    pixmap.scaled(
                        size,
                        size,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )

        return logo

    def on_page_changed(self, index):
        self.header_stack.setCurrentIndex(index)
        self.header_stack.setFixedHeight(85 if index == 0 else 50)

    def build_default_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        header = QLabel()
        header.setObjectName("sectionTitle")
        header.setProperty("i18n", "choose_delay")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        presets_layout = QHBoxLayout()
        presets_layout.setSpacing(12)

        for minutes in (15, 30, 45, 60):
            button = QPushButton()
            button.setObjectName("presetButton")
            button.setProperty("presetMinutes", minutes)
            button.setFixedHeight(92)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(
                lambda checked=False, m=minutes: self.start_timer(m * 60)
            )
            presets_layout.addWidget(button, 1)

        custom_button = QPushButton()
        custom_button.setObjectName("secondaryButton")
        custom_button.setProperty("i18n", "set_custom")
        custom_button.setFixedHeight(48)
        custom_button.setCursor(Qt.CursorShape.PointingHandCursor)
        custom_button.clicked.connect(self.open_custom_timer_page)

        layout.addStretch(1)
        layout.addWidget(header)
        layout.addSpacing(8)
        layout.addLayout(presets_layout)
        layout.addWidget(custom_button)
        layout.addStretch(2)

        self.stack.addWidget(page)

    def open_custom_timer_page(self):
        self.custom_hours = 0
        self.custom_minutes = 0
        self.custom_seconds = 0
        self.refresh_custom_timer_labels()
        self.stack.setCurrentIndex(1)

    def build_custom_page(self):
        page = QWidget()
        outer_layout = QVBoxLayout(page)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        card_wrapper = QHBoxLayout()
        card_wrapper.setContentsMargins(0, 0, 0, 0)
        card_wrapper.setSpacing(0)

        card = QFrame()
        card.setObjectName("customCard")
        card.setFixedWidth(530)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 8, 22, 8)
        card_layout.setSpacing(8)

        # Time selectors
        selector_layout = QHBoxLayout()
        selector_layout.setSpacing(14)
        selector_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        hours_widget = self.build_time_selector(
            "hours",
            lambda: self.custom_hours,
            lambda: self.change_custom_time("hours", 1),
            lambda: self.change_custom_time("hours", -1),
            "hours_value_label",
        )
        minutes_widget = self.build_time_selector(
            "minutes",
            lambda: self.custom_minutes,
            lambda: self.change_custom_time("minutes", 1),
            lambda: self.change_custom_time("minutes", -1),
            "minutes_value_label",
        )
        seconds_widget = self.build_time_selector(
            "seconds",
            lambda: self.custom_seconds,
            lambda: self.change_custom_time("seconds", 1),
            lambda: self.change_custom_time("seconds", -1),
            "seconds_value_label",
        )

        colon_1 = QLabel(":")
        colon_1.setObjectName("timeColon")
        colon_1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        colon_2 = QLabel(":")
        colon_2.setObjectName("timeColon")
        colon_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        selector_layout.addWidget(hours_widget)
        selector_layout.addWidget(colon_1)
        selector_layout.addWidget(minutes_widget)
        selector_layout.addWidget(colon_2)
        selector_layout.addWidget(seconds_widget)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        cancel_button = QPushButton()
        cancel_button.setObjectName("secondaryButton")
        cancel_button.setProperty("i18n", "cancel")
        cancel_button.setFixedHeight(50)
        cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_button.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        set_button = QPushButton()
        set_button.setObjectName("primaryButton")
        set_button.setProperty("i18n", "set")
        set_button.setFixedHeight(50)
        set_button.setCursor(Qt.CursorShape.PointingHandCursor)
        set_button.clicked.connect(self.start_custom_timer)

        buttons_layout.addWidget(cancel_button, 1)
        buttons_layout.addWidget(set_button, 1)

        card_layout.addLayout(selector_layout)
        card_layout.addSpacing(30)
        card_layout.addLayout(buttons_layout)

        card_wrapper.addStretch(1)
        card_wrapper.addWidget(card)
        card_wrapper.addStretch(1)

        outer_layout.addSpacing(0)
        outer_layout.addLayout(card_wrapper)
        outer_layout.addStretch(1)

        self.stack.addWidget(page)
        self.refresh_custom_timer_labels()

    def build_time_selector(
        self, unit_key, get_value, on_increase, on_decrease, value_name
    ):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        label = QLabel()
        label.setObjectName("timeUnitLabel")
        label.setProperty("i18n", unit_key)
        label.setFixedHeight(18)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        up_button = QToolButton()
        up_button.setObjectName("arrowButton")
        up_button.setText("▲")
        up_button.setFixedSize(58, 30)
        up_button.setCursor(Qt.CursorShape.PointingHandCursor)
        up_button.clicked.connect(on_increase)

        value_frame = QFrame()
        value_frame.setObjectName("timeValueFrame")
        value_frame.setFixedSize(82, 58)

        value_layout = QVBoxLayout(value_frame)
        value_layout.setContentsMargins(0, 0, 0, 0)
        value_layout.setSpacing(0)

        value_label = QLabel(f"{get_value():02d}")
        value_label.setObjectName("timeValueLabel")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        setattr(self, value_name, value_label)
        value_layout.addWidget(value_label)

        down_button = QToolButton()
        down_button.setObjectName("arrowButton")
        down_button.setText("▼")
        down_button.setFixedSize(58, 30)
        down_button.setCursor(Qt.CursorShape.PointingHandCursor)
        down_button.clicked.connect(on_decrease)

        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(up_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_frame, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(down_button, alignment=Qt.AlignmentFlag.AlignCenter)
        widget.setFixedSize(96, 164)
        return widget

    def change_custom_time(self, unit, delta):
        if unit == "hours":
            self.custom_hours = max(0, min(24, self.custom_hours + delta))
            if self.custom_hours == 24:
                self.custom_minutes = 0
                self.custom_seconds = 0
        elif unit == "minutes":
            if self.custom_hours < 24:
                self.custom_minutes = max(0, min(59, self.custom_minutes + delta))
        elif unit == "seconds":
            if self.custom_hours < 24:
                self.custom_seconds = max(0, min(59, self.custom_seconds + delta))

        self.refresh_custom_timer_labels()

    def refresh_custom_timer_labels(self):
        self.hours_value_label.setText(f"{self.custom_hours:02d}")
        self.minutes_value_label.setText(f"{self.custom_minutes:02d}")
        self.seconds_value_label.setText(f"{self.custom_seconds:02d}")

    def build_running_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)

        self.countdown_label = QLabel("00:00:00")
        self.countdown_label.setObjectName("countdown")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.shutdown_time_label = QLabel("")
        self.shutdown_time_label.setObjectName("subtitle")
        self.shutdown_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        cancel_button = QPushButton()
        cancel_button.setObjectName("dangerButton")
        cancel_button.setProperty("i18n", "cancel_timer")
        cancel_button.setMinimumHeight(48)
        cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_button.clicked.connect(self.cancel_timer)

        layout.addStretch()
        layout.addWidget(self.countdown_label)
        layout.addWidget(self.shutdown_time_label)
        layout.addStretch()
        layout.addWidget(cancel_button)
        self.stack.addWidget(page)

    #endregion

    #region LOCALIZATION

    def t(self, key, **values):
        return TRANSLATIONS[self.language][key].format(**values)

    def change_language(self, index):
        if index < 0:
            return

        language = self.language_combo.itemData(index)
        if language not in TRANSLATIONS:
            return

        self.language = language
        self.apply_language()

    def apply_language(self):
        for label in self.findChildren(QLabel):
            key = label.property("i18n")
            if key:
                label.setText(self.t(key))

        for button in self.findChildren(QPushButton):
            key = button.property("i18n")
            minutes = button.property("presetMinutes")

            if key:
                button.setText(self.t(key))
            elif minutes is not None:
                button.setText(self.t("preset", minutes=minutes))

        self.status_label.setText(self.t(self.status_key))
        self.update_shutdown_time_label()
        self.minimize_button.setToolTip(self.t("minimize"))
        self.close_button.setToolTip(self.t("close"))
        self.language_combo.setToolTip(self.t("choose_language"))
        self.refresh_tray()

    def set_status(self, key):
        self.status_key = key
        self.status_label.setText(self.t(key))
        self.refresh_tray()

    def refresh_tray(self):
        if self.tray_manager is not None:
            self.tray_manager.refresh()

    def update_shutdown_time_label(self):
        if self.shutdown_time is None:
            self.shutdown_time_label.setText("")
            return

        self.shutdown_time_label.setText(
            self.t("shutdown_at", time=self.shutdown_time.strftime("%H:%M"))
        )

    #endregion

    #region TIMER

    def start_custom_timer(self):
        total_seconds = (
            self.custom_hours * 3600
            + self.custom_minutes * 60
            + self.custom_seconds
        )

        if total_seconds <= 0:
            self.set_status("invalid_duration")
            return

        self.start_timer(total_seconds)

    def start_timer(self, seconds):
        self.selected_seconds = seconds
        self.deadline = time.monotonic() + seconds
        self.shutdown_time = datetime.now() + timedelta(seconds=seconds)

        self.update_shutdown_time_label()
        self.set_status("timer_running")
        self.stack.setCurrentIndex(2)
        self.update_timer()
        self.timer.start()

    def update_timer(self):
        if self.deadline is None:
            return

        remaining = max(0, math.ceil(self.deadline - time.monotonic()))
        hours, remainder = divmod(remaining, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.countdown_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

        if remaining == 0:
            self.finish_timer()
        else:
            self.refresh_tray()

    def cancel_timer(self, status_key="timer_cancelled"):
        self.timer.stop()
        self.deadline = None
        self.shutdown_time = None
        self.stack.setCurrentIndex(0)
        self.set_status(status_key)

    def cancel_due_to_sleep(self):
        # Also called on resume as a defensive fallback. Do not restart the timer.
        if self.deadline is not None:
            self.cancel_timer(status_key="sleep_cancelled")

    def closeEvent(self, event):
        if (
            not self._allow_close
            and self.tray_manager is not None
            and self.tray_manager.available
        ):
            event.ignore()
            self.hide()
            return

        # No tray available (or explicit Exit): close normally, cancel countdown.
        self.timer.stop()
        self.deadline = None
        self.shutdown_time = None
        event.accept()

    def finish_timer(self):
        self.timer.stop()
        self.deadline = None
        self.shutdown_time = None
        self.stack.setCurrentIndex(0)
        self.set_status("timer_finished")

    #endregion
