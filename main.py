
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    icon_path = (
        Path(__file__).resolve().parent
        / "assets"
        / "AutoSleeper_black.ico"
    )

    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    stylesheet_path = (
        Path(__file__).resolve().parent / "ui" / "styles.qss"
    )

    with stylesheet_path.open("r", encoding="utf-8") as file:
        app.setStyleSheet(file.read())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
