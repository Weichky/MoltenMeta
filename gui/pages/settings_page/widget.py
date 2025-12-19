from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QLocale, QTranslator, QCoreApplication

from .ui import UiSettingsPage

class SettingsPage(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = UiSettingsPage()
        self.ui.setupUi(self)
        self.ui.retranslateUi()

        # Connect signals
        self.ui._connect_signals()