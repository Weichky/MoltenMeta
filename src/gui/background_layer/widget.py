# This page only shows when all of pages in dock is invisible or floating

from PySide6 import QtWidgets
from PySide6.QtCore import Signal, QCoreApplication

from i18n import getI18nService

from .ui import UiBackgroundLayer

class BackgroundLayer(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = UiBackgroundLayer()
        self.ui.setupUi(self)
        self.ui.retranslateUi()

        # i18n
        getI18nService().languageChanged.connect(self.retranslateUi)

    def retranslateUi(self):
        self.ui.retranslateUi()