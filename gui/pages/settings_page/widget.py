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
        # Notice that signals are connected in the controller
        # In other cases, signals are connected in the widget
        self.controller = SettingsController(self.ui)
        self.controller.connectSignals()

    def retranslateUi(self):
        self.ui.retranslateUi()