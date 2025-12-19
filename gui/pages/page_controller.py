from PySide6 import QtWidgets
import PySide6QtAds as QtAds

from gui.pages.home_page import HomePage
from gui.pages.settings_page.widget import SettingsPage

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

            # 连接主页按钮信号
            home_page.projectButtonClicked.connect(self.show_project)
            home_page.databaseButtonClicked.connect(self.show_database)
            home_page.simulationButtonClicked.connect(self.show_simulation)
            home_page.settingsButtonClicked.connect(self.show_settings)

            self.dock_manager.addDockWidget(QtAds.DockWidgetArea.CenterDockWidgetArea, dock)
            self.pages["home"] = dock
        else:
            dock = self.pages["home"]
            dock.raise_()
            dock.setVisible(True)
            dock.toggleView()

    def show_settings(self):
        """显示设置页面"""
        # 如果 dock 被删除或关闭，或者第一次
        if "settings" not in self.pages or self.pages["settings"] is None:
            settings_page = SettingsPage()
            dock = QtAds.CDockWidget("Settings")
            dock.setWidget(settings_page)

            self.dock_manager.addDockWidget(QtAds.DockWidgetArea.CenterDockWidgetArea, dock)
            self.pages["settings"] = dock
        else:
            dock = self.pages["settings"]
            dock.raise_()
            dock.setVisible(True)
            dock.toggleView()

    def show_project(self):
        """显示项目页面（占位符）"""
        print("Project page opened")

    def show_database(self):
        """显示数据库页面（占位符）"""
        print("Database page opened")

    def show_simulation(self):
        """显示仿真页面（占位符）"""
        print("Simulation page opened")

    def _on_dock_closed(self, name: str):
        # 用户关闭 dock 时清理引用
        self.pages[name] = None