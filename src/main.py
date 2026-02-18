import sys
from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow

from application.service import bootstrap
def main():

    app = QApplication(sys.argv)
    
    window = MainWindow(bootstrap(app))
    window.show()
    
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()