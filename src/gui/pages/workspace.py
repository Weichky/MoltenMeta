from PySide6 import QtWidgets
import PySide6QtAds as QtAds

from application import AppContext

from gui.pages.page_controller import PageController

from gui.background_layer import BackgroundLayer
from gui.appearance.theme import getAdsStylesheet


class Workspace(QtWidgets.QWidget):
    def __init__(self, parent, context: AppContext):
        super().__init__(parent)

        self.setLayout(QtWidgets.QStackedLayout())

        # Dock manager
        self.dock_manager = QtAds.CDockManager(self)
        self.dock_manager.setStyleSheet(getAdsStylesheet())

        self.layout().addWidget(self.dock_manager)

        # Listen for theme changes
        context.theme.theme_changed.connect(self._onThemeChanged)

        # Background layer (NOT inside dock_manager)
        self.background = BackgroundLayer(self, context.i18n)
        self.layout().addWidget(self.background)

        # default
        self.background.hide()

        self.controller = PageController(
            dock_manager=self.dock_manager,
            background_layer=self.background,
            context=context,
        )

    def _onThemeChanged(self):
        self.dock_manager.setStyleSheet(getAdsStylesheet())
