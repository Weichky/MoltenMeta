# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, 
)
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
        
        # 启动时自动显示主页
        self.workspace.controller.show_home()