from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QCoreApplication, Signal


class Tile(QtWidgets.QPushButton):

    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)

        self.setMinimumSize(120, 80)
        
    def set_title(self, title):
        self.setText(title)
        
    def retranslateUi(self, title):
        self.setText(QCoreApplication.translate("homepage", title, None))


class HomePage(QtWidgets.QWidget):
    # Define custom signals
    projectButtonClicked = Signal()
    databaseButtonClicked = Signal()
    simulationButtonClicked = Signal()
    settingsButtonClicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.tiles = []

        self.root_layout = QtWidgets.QVBoxLayout(self)
        self.root_layout.setSpacing(16)
        self.root_layout.setContentsMargins(24, 24, 24, 24)

        self.root_layout.addStretch()

        # ===== Top Title =====
        self.title = QtWidgets.QLabel()
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        # self.title.setStyleSheet("font-size: 24px; font-weight: 600;")

        self.root_layout.addWidget(self.title)

        # ===== Middle 4x4 Grid =====
        self.grid_container = QtWidgets.QWidget(self)
        self.grid = QtWidgets.QGridLayout(self.grid_container)
        self.grid.setSpacing(12)

        tile_names = ["Project", "Database", "Simulation", "Settings"]
        self.tiles = [Tile(name) for name in tile_names]

        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for tile, (r, c) in zip(self.tiles, positions):
            self.grid.addWidget(tile, r, c)

        # Center the grid
        self.grid.setRowStretch(2, 1)
        self.grid.setColumnStretch(2, 1)

        self.root_layout.addWidget(self.grid_container, alignment=QtCore.Qt.AlignCenter)

        # ===== Bottom Description Text =====
        self.description = QtWidgets.QLabel()
        self.description.setWordWrap(True)
        self.description.setAlignment(QtCore.Qt.AlignCenter)

        self.root_layout.addWidget(self.description)

        self.root_layout.addStretch()
        
        # Connect button signals
        self._connect_signals()
        
        # Initialize translation
        self.retranslateUi()

    def _connect_signals(self):
        PROJECT_INDEX = 0
        DATABASE_INDEX = 1
        SIMULATION_INDEX = 2
        SETTINGS_INDEX = 3
        
        self.tiles[PROJECT_INDEX].clicked.connect(self.projectButtonClicked.emit)
        self.tiles[DATABASE_INDEX].clicked.connect(self.databaseButtonClicked.emit)
        self.tiles[SIMULATION_INDEX].clicked.connect(self.simulationButtonClicked.emit)
        self.tiles[SETTINGS_INDEX].clicked.connect(self.settingsButtonClicked.emit)

    def retranslateUi(self):
        welcome_text = QCoreApplication.translate("homepage", "Welcome", None)
        self.title.setText("<h1>"+welcome_text+"</h1>")
        software_description = QCoreApplication.translate(
            "homepage", 
            "This software provides an integrated environment for "
            "data management, simulation, and analysis. "
            "All modules are designed to be extensible and reproducible.",
            None)
        self.description.setText("<h6>"+software_description+"</h6>")
            
        # Translate tiles
        tile_titles = ["Project", "Database", "Simulation", "Settings"]
        for tile, title in zip(self.tiles, tile_titles):
            tile.retranslateUi(title)

    def resizeEvent(self, event):
        super().resizeEvent(event)