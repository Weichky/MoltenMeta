from PySide6 import QtWidgets
import PySide6QtAds as QtAds

from gui.pages.home_page import HomePage
from gui.pages.settings_page import SettingsPage

from core.log import getLogger

from dataclasses import dataclass
from typing import Callable

class PageController:

    def __init__(self, dock_manager: QtAds.CDockManager, background_layer: QtWidgets.QWidget):

        self.logger = getLogger(__name__)

        # page_spec
        self._home_spec = DockPageSpec(
            "home",
            "Home",
            HomePage,
            self._connectHomeSignals
        )

        self._settings_spec = DockPageSpec(
            "settings",
            "Settings",
            SettingsPage
        )

        self.dock_manager = dock_manager
        self.background_layer = background_layer
        self.pages = {}  # Page cache

    def showHome(self):
        self._showPage(self._home_spec)

    def showSettings(self):
        self._showPage(self._settings_spec)

    def showProject(self):
        self.logger.debug("Project page not implemented yet")

    def showDatabase(self):
        self.logger.debug("Database page not implemented yet")

    def showSimulation(self):
        self.logger.debug("Simulation page not implemented yet")


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

    # Get the dock area
    # Btw notice QtADS's C++ src code to learn more about the api
    # The Python version documents are in need of improvement and even not complete
    def _getArea(self):
        containers = self.dock_manager.dockContainers()

        area = None
        if containers:
            areas = containers[0].openedDockAreas()
            if areas:
                area = areas[0]

        return area
    
    def _showPage(self, spec: DockPageSpec):
        dock = self.pages.get(spec.key)

        if dock is None:
            widget = spec.factory()
            dock = QtAds.CDockWidget(spec.title)
            dock.setWidget(widget)

            dock.visibilityChanged.connect(self._onDockVisibilityChanged)

            if spec.onCreate:
                spec.onCreate(widget)

            self.pages[spec.key] = dock

            self.dock_manager.addDockWidget(
                QtAds.DockWidgetArea.CenterDockWidgetArea,
                dock,
                self._getArea()
            )

            return
        
        if not dock.isVisible():
            dock.setVisible(True)
            dock.toggleView()
        
        dock.raise_()

    def _connectHomeSignals(self, page: HomePage):
        page.projectButtonClicked.connect(self.showProject)
        page.databaseButtonClicked.connect(self.showDatabase)
        page.simulationButtonClicked.connect(self.showSimulation)
        page.settingsButtonClicked.connect(self.showSettings)
    
###############################################################################

@dataclass
class DockPageSpec:
    key: str
    title: str
    factory: Callable[[], QtWidgets.QWidget]
    onCreate: Callable[[QtWidgets.QWidget], None] | None = None

