# This page only shows when all of pages in dock is invisible or floating

from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Signal, QCoreApplication

from .ui import UiBackgroundLayer

class BackgroundLayer(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = UiBackgroundLayer()
        self.ui.setupUi(self)
        self.ui.retranslateUi()