from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QObject, QCoreApplication


class Tile(QtWidgets.QPushButton):

    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)

        self.setMinimumSize(120, 80)
        
    def set_title(self, title):
        self.setText(title)
        
    def retranslateUi(self, title):
        self.setText(QCoreApplication.translate("homepage", title, None))


class UiHomePage(QObject):
    def setupUi(self, homePage: QtWidgets.QWidget):
        if not homePage.objectName():
            homePage.setObjectName("homePage")

        self.tiles = []

        self.root_layout = QtWidgets.QVBoxLayout(homePage)
        self.root_layout.setSpacing(16)
        self.root_layout.setContentsMargins(24, 24, 24, 24)

        self.root_layout.addStretch()

        # ===== Top Title =====
        self.title = QtWidgets.QLabel()
        self.title.setAlignment(QtCore.Qt.AlignCenter)

        self.root_layout.addWidget(self.title)

        # ===== Middle 4x4 Grid =====
        self.grid_container = QtWidgets.QWidget(homePage)
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