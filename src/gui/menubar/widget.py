from PySide6.QtWidgets import QMenuBar
from PySide6.QtCore import Signal

from .ui import UiMenubar

from i18n import I18nService


class MenubarWidget(QMenuBar):
    importRequested = Signal()

    def __init__(self, parent, i18nService: I18nService):
        super().__init__(parent)
        self.i18nService = i18nService
        self.ui = UiMenubar()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)

        self.ui.action_exit.triggered.connect(parent.close)
        self.ui.action_full_screen.triggered.connect(self.toggleFullScreen)
        self.ui.action_import_file.triggered.connect(self.importRequested)

        self.i18nService.language_changed.connect(self.retranslateUi)

    def toggleFullScreen(self):
        mainWindow = self.parent()
        if mainWindow.isFullScreen():
            mainWindow.showNormal()
        else:
            mainWindow.showFullScreen()

    def retranslateUi(self):
        self.ui.retranslateUi(self)
