from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QLocale, QTranslator, QCoreApplication

from .ui import UiSettingsPage
from .controller import SettingsController

class SettingsPage(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = UiSettingsPage()
        self.ui.setupUi(self)
        self.ui.retranslateUi()

        # Create controller to handle logic
        self.controller = SettingsController(self.ui)
        self.controller.connectSignals()