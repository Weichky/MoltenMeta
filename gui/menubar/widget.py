from PySide6.QtWidgets import QMenuBar

from .ui import UiMenubar

class MenubarWidget(QMenuBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.ui = UiMenubar()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)
        
        # 连接系统操作相关的槽函数
        self.ui.action_exit.triggered.connect(parent.close)
        self.ui.action_full_screen.triggered.connect(self.toggleFullScreen)

    def toggleFullScreen(self):
        mainWindow = self.parent()
        if mainWindow.isFullScreen():
            mainWindow.showNormal()
        else:
            mainWindow.showFullScreen()