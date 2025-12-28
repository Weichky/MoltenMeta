from PySide6 import QtWidgets
import PySide6QtAds as QtAds

from gui.pages.page_controller import PageController

from gui.background_layer import BackgroundLayer

class Workspace(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setLayout(QtWidgets.QStackedLayout())

        # Dock manager
        self.dock_manager = QtAds.CDockManager(self)
        self.layout().addWidget(self.dock_manager)

        # Background layer (NOT inside dock_manager)
        self.background = BackgroundLayer(self)
        self.layout().addWidget(self.background)

        self.background.hide()

        self.controller = PageController(
            self.dock_manager,
            self.background
        )