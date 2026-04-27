from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtCore import QObject


class Tile(QtWidgets.QPushButton):
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.setObjectName("tileButton")
        self.setCursor(QtCore.Qt.PointingHandCursor)


class AccentLine(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(3)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        self.setStyleSheet("background-color: #C62828; border: none;")


class RulerWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(16)

    def paintEvent(self, event):
        # Draw a horizontal ruler with tick marks:
        # - Main line at y=5 across full width
        # - Short ticks every 20px (height 3px)
        # - Long ticks every 40px (height 6px) for emphasis
        painter = QPainter(self)
        painter.setPen(QPen(QColor("#E0E0E0"), 1))
        painter.drawLine(0, 5, self.width(), 5)
        for i in range(0, self.width(), 20):
            painter.drawLine(i, 5, i, 5 + (6 if i % 40 == 0 else 3))


class UiHomePage(QObject):
    BASE_TILE_WIDTH = 70
    BASE_TILE_HEIGHT = 40
    BASE_SPACING = 6

    def setupUi(self, homePage: QtWidgets.QWidget):
        if not homePage.objectName():
            homePage.setObjectName("homePage")

        self.tiles = []

        self.root_layout = QtWidgets.QVBoxLayout(homePage)
        self.root_layout.setSpacing(0)
        self.root_layout.setContentsMargins(80, 64, 0, 64)

        header_widget = QtWidgets.QWidget()
        header_layout = QtWidgets.QVBoxLayout(header_widget)
        header_layout.setSpacing(8)
        header_layout.setContentsMargins(0, 0, 0, 0)

        self.title_label = QtWidgets.QLabel()
        self.title_label.setObjectName("heroTitle")
        header_layout.addWidget(self.title_label)

        self.accent_line = AccentLine()
        header_layout.addWidget(self.accent_line)

        self.subtitle_label = QtWidgets.QLabel()
        self.subtitle_label.setObjectName("heroSubtitle")
        header_layout.addWidget(self.subtitle_label)

        self.root_layout.addWidget(header_widget)

        self.root_layout.addSpacing(56)

        self.section_label = QtWidgets.QLabel()
        self.section_label.setObjectName("sectionLabel")
        self.section_label.setText(self.tr("Quick Access"))
        self.root_layout.addWidget(self.section_label)

        self.root_layout.addSpacing(32)

        tiles_widget = QtWidgets.QWidget()
        tiles_layout = QtWidgets.QGridLayout(tiles_widget)
        tiles_layout.setSpacing(self.BASE_SPACING * 2)
        tiles_layout.setContentsMargins(0, 0, 0, 0)
        tiles_layout.setAlignment(QtCore.Qt.AlignLeft)

        tile_names = [
            self.tr("Project"),
            self.tr("Data"),
            self.tr("Simulation"),
            self.tr("Settings"),
        ]
        self.tiles = [Tile(name) for name in tile_names]

        for tile in self.tiles:
            tile.setMinimumSize(self.BASE_TILE_WIDTH, self.BASE_TILE_HEIGHT)
            tile.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed
            )

        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for tile, (r, c) in zip(self.tiles, positions):
            tiles_layout.addWidget(tile, r, c)

        self.root_layout.addWidget(tiles_widget)

        self.root_layout.addStretch()

        self.description = QtWidgets.QLabel()
        self.description.setObjectName("description")
        self.description.setWordWrap(True)
        self.description.setMaximumWidth(640)
        self.root_layout.addWidget(self.description)

        self.root_layout.addSpacing(16)

        ruler = RulerWidget()
        self.root_layout.addWidget(ruler)

        self.root_layout.addSpacing(32)

    def setupTitleLabel(self, primary_color: str):
        self.title_label.setText(
            f'Molten<span style="color: {primary_color};">M</span>eta'
        )

    def retranslateUi(self):
        self.subtitle_label.setText(self.tr("Material Science Computing Platform"))
        self.description.setText(
            self.tr(
                "Integrated environment for thermodynamic data management, prediction, and analysis of liquid alloys."
            )
        )

        tile_names = [
            self.tr("Project"),
            self.tr("Data"),
            self.tr("Simulation"),
            self.tr("Settings"),
        ]
        tile_tooltips = [
            self.tr("Create and manage projects"),
            self.tr("Import and organize data"),
            self.tr("Run thermodynamic calculations"),
            self.tr("Configure application settings"),
        ]
        for tile, name, tooltip in zip(self.tiles, tile_names, tile_tooltips):
            tile.setText(name)
            tile.setToolTip(tooltip)
