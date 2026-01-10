from PySide6 import QtWidgets
from PySide6.QtCore import Signal

from i18n import getI18nService

from .ui import UiHomePage


class HomePage(QtWidgets.QWidget):
    # Define custom signals
    projectButtonClicked = Signal()
    databaseButtonClicked = Signal()
    simulationButtonClicked = Signal()
    settingsButtonClicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.ui = UiHomePage()
        self.ui.setupUi(self)
        self.ui.retranslateUi()
        
        # Connect button signals
        self._connect_signals()

    def _connect_signals(self):
        PROJECT_INDEX = 0
        DATABASE_INDEX = 1
        SIMULATION_INDEX = 2
        SETTINGS_INDEX = 3
        
        self.ui.tiles[PROJECT_INDEX].clicked.connect(self.projectButtonClicked.emit)
        self.ui.tiles[DATABASE_INDEX].clicked.connect(self.databaseButtonClicked.emit)
        self.ui.tiles[SIMULATION_INDEX].clicked.connect(self.simulationButtonClicked.emit)
        self.ui.tiles[SETTINGS_INDEX].clicked.connect(self.settingsButtonClicked.emit)

        # i18n
        getI18nService().languageChanged.connect(self.retranslateUi)

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def retranslateUi(self):
        self.ui.retranslateUi()