from PySide6 import QtWidgets
import PySide6QtAds as QtAds

from gui.pages.home_page import HomePage
from gui.pages.settings_page import SettingsPage

class PageController:

    def __init__(self, dock_manager: QtAds.CDockManager):
        self.dock_manager = dock_manager
        self.pages = {}  # Page cache

    def show_home(self):
        # If dock is deleted/closed or first time
        if "home" not in self.pages or self.pages["home"] is None:
            home_page = HomePage()
            dock = QtAds.CDockWidget("Home")
            dock.setWidget(home_page)

            # Connect homepage button signals
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
        """Show settings page."""
        # If dock is deleted/closed or first time
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
        """Show project page (placeholder)."""
        print("Project page opened")

    def show_database(self):
        """Show database page (placeholder)."""
        print("Database page opened")

    def show_simulation(self):
        """Show simulation page (placeholder)."""
        print("Simulation page opened")

    def _on_dock_closed(self, name: str):
        # Clean up reference when user closes dock
        self.pages[name] = None