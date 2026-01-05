import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QLocale, QTranslator, QLibraryInfo
from gui.main_window import MainWindow
from fio.config_loader import loadConfig

def main():
    init()
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


def init():
    loadConfig()

if __name__ == "__main__":
    main()