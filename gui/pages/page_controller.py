from PySide6 import QtWidgets
import PySide6QtAds as QtAds

from gui.pages.home_page import HomePage
from gui.pages.settings_page import SettingsPage

class PageController:

    def __init__(self, dock_manager: QtAds.CDockManager, background_layer: QtWidgets.QWidget):

        self.dock_manager = dock_manager
        self.background_layer = background_layer
        self.pages = {}  # Page cache

    def showHome(self):
        dock = self.pages.get("home")
        if dock is None:
            home_page = HomePage()
            dock = QtAds.CDockWidget("Home")
            dock.setWidget(home_page)

            dock.visibilityChanged.connect(self._onDockVisibilityChanged)

            # Connect homepage button signals
            home_page.projectButtonClicked.connect(self.showProject)
            home_page.databaseButtonClicked.connect(self.showDatabase)
            home_page.simulationButtonClicked.connect(self.showSimulation)
            home_page.settingsButtonClicked.connect(self.showSettings)

            self.dock_manager.addDockWidget(
                QtAds.DockWidgetArea.CenterDockWidgetArea, dock
            )
            self.pages["home"] = dock

            return
        
        if not dock.isVisible():
            dock.setVisible(True)
            dock.toggleView()

        dock.raise_()       

    def showSettings(self):
        dock = self.pages.get("settings")
        if dock is None:
            settings_page = SettingsPage()
            dock = QtAds.CDockWidget("Settings")
            dock.setWidget(settings_page)

            dock.visibilityChanged.connect(self._onDockVisibilityChanged)

            self.dock_manager.addDockWidget(
                QtAds.DockWidgetArea.CenterDockWidgetArea, dock
            )
            self.pages["settings"] = dock

            return

        if not dock.isVisible():
            dock.setVisible(True)
            dock.toggleView()

        dock.raise_()

    def showProject(self):
        """Show project page (placeholder)."""
        print("Project page opened")

    def showDatabase(self):
        """Show database page (placeholder)."""
        print("Database page opened")

    def showSimulation(self):
        """Show simulation page (placeholder)."""
        print("Simulation page opened")

    # A dock is visible if it is not floating or hidden
    def _hasVisibleDock(self) -> bool:
        return any(
            dock and dock.isVisible() and not dock.isFloating()
            for dock in self.pages.values()
        )

    # Variable "visible" is not used
    def _onDockVisibilityChanged(self, visible):
        if self._hasVisibleDock():
            self.background_layer.hide()
        else:
            self.background_layer.show()
            self.background_layer.raise_()