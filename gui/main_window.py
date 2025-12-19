# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtCore import Qt, QEvent
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, 
)
from PySide6.QtGui import QPalette
import PySide6QtAds as QtAds

# Import the simplified main window UI
from gui.ui_main_window import UiMainWindow
from gui.sidebar import SidebarWidget
from gui.menubar import MenubarWidget
from gui.pages.workspace import Workspace

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)

        # 设置菜单栏
        self.menubar = MenubarWidget(self)
        self.setMenuBar(self.menubar)

        # 设置侧边栏
        self.sidebar = SidebarWidget(self)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.sidebar)

        # 设置工作区
        self.workspace = Workspace(self)
        self.setCentralWidget(self.workspace)

        # 连接信号槽
        self.sidebar.ui.homeButton.clicked.connect(
            self.workspace.controller.show_home
        )
        self.sidebar.ui.settingsButton.clicked.connect(
            self.workspace.controller.show_settings
        )
        
        # 连接菜单栏设置动作
        self.menubar.ui.actionSettings.triggered.connect(
            self.workspace.controller.show_settings
        )
        
        # 启动时自动显示主页
        self.workspace.controller.show_home()

    def changeEvent(self, event):

        if event.type() == QEvent.Type.ThemeChange:
            # 当系统主题变化时，更新应用程序的调色板
            QApplication.setPalette(QApplication.style().standardPalette())
            # 强制更新所有子部件
            self.updateTheme()
        super().changeEvent(event)
    
    def updateTheme(self):

        # 递归更新所有子部件
        self.setStyleSheet("")
        self.updateStylesRecursive(self)
    
    def updateStylesRecursive(self, widget):

        widget.setStyle(widget.style())
        for child in widget.children():
            if isinstance(child, QWidget):
                self.updateStylesRecursive(child)