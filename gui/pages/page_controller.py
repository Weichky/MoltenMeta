from PySide6 import QtWidgets
import PySide6QtAds as QtAds

from gui.pages.home_page import HomePage

class PageController:

    def __init__(self, dock_manager: QtAds.CDockManager):
        self.dock_manager = dock_manager
        self.pages = {}  # 页面缓存

    def show_home(self):
        # 如果 dock 被删除或关闭，或者第一次
        if "home" not in self.pages or self.pages["home"] is None:
            home_page = HomePage()
            dock = QtAds.CDockWidget("Home")
            dock.setWidget(home_page)

            self.dock_manager.addDockWidget(QtAds.DockWidgetArea.CenterDockWidgetArea, dock)
            self.pages["home"] = dock
        else:
            dock = self.pages["home"]
            dock.raise_()
            dock.setVisible(True)
            dock.toggleView()

    def _on_dock_closed(self, name: str):
        # 用户关闭 dock 时清理引用
        self.pages[name] = None

