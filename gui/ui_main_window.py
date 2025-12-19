from PySide6.QtCore import (
    Qt,
    QObject
)
from PySide6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QWidget
    )

class UiMainWindow(QObject):
    def setupUi(self, mainWindow):
        if not mainWindow.objectName():
            mainWindow.setObjectName(u"mainWindow")
        # Set window size
        mainWindow.resize(1200, 800)
        mainWindow.setMinimumSize(800, 600)

        
        # Create central area
        self.centralwidget = QWidget(mainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setEnabled(True)
        mainWindow.setCentralWidget(self.centralwidget)
        
        # Create status bar
        self.statusBar = QStatusBar(mainWindow)
        self.statusBar.setObjectName(u"statusBar")
        mainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(mainWindow)
        
    def retranslateUi(self, mainWindow):
        mainWindow.setWindowTitle(self.tr(u"Molten Meta"))