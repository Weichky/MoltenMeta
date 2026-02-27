from PySide6 import QtWidgets, QtCore
from application import AppContext
from .ui import UiSettingsPage
from .controller import SettingsController


class SettingsPage(QtWidgets.QWidget):
    def __init__(self, context: AppContext):
        super().__init__(parent=None)
        self.ui = UiSettingsPage(context.settings)
        self.ui.setupUi(self)
        self.ui.retranslateUi()

        # Create controller to handle logic
        # Notice that signals are connected in the controller
        # In other cases, signals are connected in the widget
        self.controller = SettingsController(self.ui, context, context.theme)
        self.controller.connectSignals()

    def retranslateUi(self):
        self.ui.retranslateUi()
