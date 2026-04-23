import sys
from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow

from application.app_startup import initApp


def main():
    QApplication.setStyle("Fusion")
    app = QApplication(sys.argv)

    window = MainWindow(initApp(app))
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
