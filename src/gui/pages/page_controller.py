from PySide6 import QtWidgets
from PySide6.QtCore import QCoreApplication
import PySide6QtAds as QtAds

from gui.pages.home_page import HomePage
from gui.pages.settings_page import SettingsPage

from application import AppContext

from dataclasses import dataclass
from typing import Callable


# For more info about dock, see:
# C++ source code:
# src/DockManager.h
# src/DockWidget.h

class PageController:

    def __init__(
        self, 
        dock_manager: QtAds.CDockManager, 
        background_layer: QtWidgets.QWidget, 
        context: AppContext
    ):

        self.logger = context.log.getLogger(__name__)
        self.i18n_service = context.i18n

        # page_spec
        self._home_spec = DockPageSpec(
            key = "home",
            # NOTE:
            # The following titleProvider must appear *here* (line 44, and the next is line 51),
            # otherwise Qt's translation scanner will fail to pick it up.
            #
            # This is a known limitation of Qt's i18n tooling rather than a logic issue.
            # An alternative is to omit <location> entries in the .ts file entirely,
            # which removes the line-number dependency.
            #
            # The trade-off is that the source text ("Home Page", etc.)
            # should then be treated as context-specific and not reused elsewhere.
            #
            # This might be fixed someday, but not today.
            # It is damning, but currently the least fragile approach.
            titleProvider=lambda: QCoreApplication.translate("DockPage", "Home Page"),
            factory = lambda: HomePage(self.i18n_service),
            onCreate = self._connectHomeSignals
        )

        self._settings_spec = DockPageSpec(
            key = "settings",
            titleProvider=lambda: QCoreApplication.translate("DockPage", "Settings"),
            # SettingsPage does not need an i18n_service to be injected
            # Because controller takes over this job
            # See more details in the comment of SettingsPage
            factory = lambda: SettingsPage(context)
        )

        self.dock_manager = dock_manager
        self.background_layer = background_layer
        self.pages = {}  # Page cache

        self.pageSpecs = {
            self._home_spec.key: self._home_spec,
            self._settings_spec.key: self._settings_spec
        }

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
            dock = self._createPage(spec)

            self.pages[spec.key] = dock

            # QtAds.CDockManager.addDockWidget parameters:
            # 1) QtAds.DockWidgetArea      — target dock area
            # 2) QtAds.CDockWidget         — dock widget to add
            # 3) QtAds.CDockAreaWidget     — explicit target area (rarely used)

            self.dock_manager.addDockWidget(
                QtAds.DockWidgetArea.CenterDockWidgetArea,
                dock,
                self._getArea()
            )

            self.retranslateUi()

            return
        

        if not dock.isVisible():
            
            # Notice that QtAds.CDockWidget has a method called setAsCurrentTab        
            # dock.raise_()
            # dock.setVisible(True)
            dock.toggleView()
    
        # dock.setAsCurrentTab()
        
        # For floating windows, try to bring them to front using available methods
        if dock.isFloating():
                dock.raise_()

        self.retranslateUi()

    def _createPage(self, spec: DockPageSpec) -> QtWidgets.QWidget:
        widget = spec.factory()
        dock = QtAds.CDockWidget(self.dock_manager, "")

        # Set the object name
        # See C++ source code src/DockWidget.h line 274 - 279:
        #  * @note The object name of the dock widget is also set to the title. The
        #  * object name is required by the dock manager to properly save and restore
        #  * the state of the dock widget. That means, the title needs to be unique. If
        #  * the title is not unique or if you would like to change the title during
        #  * runtime, you need to set a unique object name explicitly by calling
        #  * setObjectName() after construction.

        dock.setObjectName(spec.key)
        dock.setWidget(widget)
        dock.visibilityChanged.connect(self._onDockVisibilityChanged)
        if spec.onCreate:
            spec.onCreate(widget)

        return dock

    def _connectHomeSignals(self, page: HomePage):
        page.projectButtonClicked.connect(self.showProject)
        page.databaseButtonClicked.connect(self.showDatabase)
        page.simulationButtonClicked.connect(self.showSimulation)
        page.settingsButtonClicked.connect(self.showSettings)

        # i18n
        self.i18n_service.language_changed.connect(self.retranslateUi)

    def retranslateUi(self):

        for key, dock in self.pages.items():
            spec = self.pageSpecs[key]
            dock.setWindowTitle(spec.titleProvider())
            
###############################################################################

@dataclass
class DockPageSpec:
    key: str
    titleProvider: Callable[[], str]
    factory: Callable[[], QtWidgets.QWidget]
    onCreate: Callable[[QtWidgets.QWidget], None] | None = None

