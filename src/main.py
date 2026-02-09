import sys
from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow

from application.service import init
def main():

    app = QApplication(sys.argv)

    init(app)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()