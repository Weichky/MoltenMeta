from PySide6.QtWidgets import QMenuBar

from .ui import UiMenubar

from i18n import getI18nService

class MenubarWidget(QMenuBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.ui = UiMenubar()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)
        
        self.ui.action_exit.triggered.connect(parent.close)
        self.ui.action_full_screen.triggered.connect(self.toggleFullScreen)

        # i18n
        getI18nService().languageChanged.connect(self.retranslateUi)

    def toggleFullScreen(self):
        mainWindow = self.parent()
        if mainWindow.isFullScreen():
            mainWindow.showNormal()
        else:
            mainWindow.showFullScreen()

    def retranslateUi(self):
        self.ui.retranslateUi(self)