from PySide6 import QtWidgets
from PySide6.QtCore import Signal


from application import AppContext

from .ui import UiTableManagerPage


class TableManagerPage(QtWidgets.QWidget):
    tableChanged = Signal(str)

    def __init__(self, context: AppContext):
        super().__init__(parent=None)
        self.i18n_service = context.i18n

        self.ui = UiTableManagerPage()
        self.ui.setupUi(self)
        self.ui.retranslateUi()

        from .controller import DatabaseController

        self.controller = DatabaseController(self.ui, context)
        self.controller.connectSignals()

        self.i18n_service.language_changed.connect(self.retranslateUi)

    def retranslateUi(self):
        self.ui.retranslateUi()
