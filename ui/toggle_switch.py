
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QCheckBox


class ToggleSwitch(QCheckBox):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(165, 30)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    #region DRAWING

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        enabled = self.isEnabled()
        checked = self.isChecked()

        # Track
        if not enabled:
            track_color = QColor("#356047" if checked else "#353535")
        elif checked:
            track_color = QColor("#00FF41" if self.underMouse() else "#00C853")
        else:
            track_color = QColor("#606060" if self.underMouse() else "#454545")

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(track_color)

        track = QRectF(2, 4, 42, 22)
        painter.drawRoundedRect(track, 11, 11)

        # Knob
        knob_x = 24 if checked else 5

        painter.setBrush(
            QColor("#FFFFFF" if enabled else "#AAAAAA")
        )

        painter.drawEllipse(
            QRectF(knob_x, 7, 16, 16)
        )

        # Label
        font = painter.font()
        font.setFamily("Segoe UI")
        font.setPixelSize(13)
        painter.setFont(font)

        painter.setPen(
            QColor("#D1D5DB" if enabled else "#737373")
        )

        text_rect = QRectF(
            54, 0, self.width() - 54, self.height()
        )

        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter,
            self.text()
        )

        painter.end()

    #endregion

    #region INTERACTION

    def enterEvent(self, event):
        super().enterEvent(event)
        self.update()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.update()

    #endregion
