# This page only shows when all of pages in dock is invisible or floating

from PySide6 import QtWidgets
from PySide6.QtCore import Signal, QCoreApplication

from i18n import I18nService

from .ui import UiBackgroundLayer

class BackgroundLayer(QtWidgets.QWidget):
    def __init__(self, parent, i18nService: I18nService):
        super().__init__(parent)
        self.i18nService = i18nService
        self.ui = UiBackgroundLayer()
        self.ui.setupUi(self)
        self.ui.retranslateUi()

        # i18n
        self.i18nService.language_changed.connect(self.retranslateUi)

    def retranslateUi(self):
        self.ui.retranslateUi()