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
        # 设置窗口大小
        mainWindow.resize(1200, 800)
        
        # 创建中央区域
        self.centralwidget = QWidget(mainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setEnabled(True)
        mainWindow.setCentralWidget(self.centralwidget)
        
        # 创建状态栏
        self.statusBar = QStatusBar(mainWindow)
        self.statusBar.setObjectName(u"statusBar")
        mainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(mainWindow)
        
    def retranslateUi(self, mainWindow):
        mainWindow.setWindowTitle(self.tr(u"Molten Meta"))