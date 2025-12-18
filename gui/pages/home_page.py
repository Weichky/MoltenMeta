from PySide6 import QtWidgets, QtCore


class Tile(QtWidgets.QFrame):
    """一个简单的磁贴组件"""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)

        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)

        layout = QtWidgets.QVBoxLayout(self)

        label = QtWidgets.QLabel(title)
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setStyleSheet("font-weight: bold;")

        layout.addStretch()
        layout.addWidget(label)
        layout.addStretch()

        self.setMinimumSize(120, 80)

class HomePage(QtWidgets.QWidget):
    """
    一个 Page：
    - 不知道 ADS
    - 不知道 MainWindow
    - 只负责 UI
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        root_layout = QtWidgets.QVBoxLayout(self)
        root_layout.setSpacing(16)
        root_layout.setContentsMargins(24, 24, 24, 24)

        # ===== 顶部标题 =====
        title = QtWidgets.QLabel("Welcome")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: 600;")

        root_layout.addWidget(title)

        # ===== 中部 4x4 Grid（放 4 个磁贴）=====
        grid_container = QtWidgets.QWidget(self)
        grid = QtWidgets.QGridLayout(grid_container)
        grid.setSpacing(12)

        tiles = [
            Tile("Project"),
            Tile("Database"),
            Tile("Simulation"),
            Tile("Settings"),
        ]

        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for tile, (r, c) in zip(tiles, positions):
            grid.addWidget(tile, r, c)

        # 让 grid 居中
        grid.setRowStretch(2, 1)
        grid.setColumnStretch(2, 1)

        root_layout.addWidget(grid_container, alignment=QtCore.Qt.AlignCenter)

        # ===== 底部说明文字 =====
        description = QtWidgets.QLabel(
            "This software provides an integrated environment for "
            "data management, simulation, and analysis. "
            "All modules are designed to be extensible and reproducible."
        )
        description.setWordWrap(True)
        description.setAlignment(QtCore.Qt.AlignCenter)

        root_layout.addWidget(description)

        root_layout.addStretch()

