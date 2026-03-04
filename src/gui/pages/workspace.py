from PySide6 import QtWidgets
import PySide6QtAds as QtAds

from i18n import I18nService

from application import AppContext

from gui.pages.page_controller import PageController

from gui.background_layer import BackgroundLayer
from resources.styles import ADS_STYLESHEET


class Workspace(QtWidgets.QWidget):
    def __init__(self, parent, context: AppContext):
        super().__init__(parent)

        self.setLayout(QtWidgets.QStackedLayout())

        # Dock manager
        self.dock_manager = QtAds.CDockManager(self)
        self.dock_manager.setStyleSheet(ADS_STYLESHEET)

        self.layout().addWidget(self.dock_manager)

        # Listen for theme changes
        context.theme.theme_changed.connect(self._on_theme_changed)

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

    def _on_theme_changed(self):
        self.dock_manager.setStyleSheet(ADS_STYLESHEET)
