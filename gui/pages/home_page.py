from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QCoreApplication


class Tile(QtWidgets.QFrame):
    """一个简单的磁贴组件"""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)

        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)

        layout = QtWidgets.QVBoxLayout(self)

        self.label = QtWidgets.QLabel()
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        # 移除硬编码样式，让系统主题决定外观
        # self.label.setStyleSheet("font-weight: bold;")

        layout.addStretch()
        layout.addWidget(self.label)
        layout.addStretch()

        self.setMinimumSize(120, 80)
        
    def set_title(self, title):
        """设置磁贴标题"""
        self.label.setText(title)
        
    def retranslateUi(self, title):
        """翻译磁贴标题"""
        self.label.setText(QCoreApplication.translate("homepage", title, None))


class HomePage(QtWidgets.QWidget):
    """主页页面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.tiles = []

        self.root_layout = QtWidgets.QVBoxLayout(self)
        self.root_layout.setSpacing(16)
        self.root_layout.setContentsMargins(24, 24, 24, 24)

        # ===== 顶部标题 =====
        self.title = QtWidgets.QLabel()
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        # 移除硬编码样式，让系统主题决定外观
        # self.title.setStyleSheet("font-size: 24px; font-weight: 600;")

        self.root_layout.addWidget(self.title)

        # ===== 中部 4x4 Grid（放 4 个磁贴）=====
        self.grid_container = QtWidgets.QWidget(self)
        self.grid = QtWidgets.QGridLayout(self.grid_container)
        self.grid.setSpacing(12)

        tile_names = ["Project", "Database", "Simulation", "Settings"]
        self.tiles = [Tile(name) for name in tile_names]

        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for tile, (r, c) in zip(self.tiles, positions):
            self.grid.addWidget(tile, r, c)

        # 让 grid 居中
        self.grid.setRowStretch(2, 1)
        self.grid.setColumnStretch(2, 1)

        self.root_layout.addWidget(self.grid_container, alignment=QtCore.Qt.AlignCenter)

        # ===== 底部说明文字 =====
        self.description = QtWidgets.QLabel()
        self.description.setWordWrap(True)
        self.description.setAlignment(QtCore.Qt.AlignCenter)

        self.root_layout.addWidget(self.description)

        self.root_layout.addStretch()
        
        # 初始化翻译
        self.retranslateUi()

    def retranslateUi(self):
        """翻译界面文本"""
        self.title.setText(QCoreApplication.translate("homepage", "Welcome", None))
        self.description.setText(QCoreApplication.translate(
            "homepage", 
            "This software provides an integrated environment for "
            "data management, simulation, and analysis. "
            "All modules are designed to be extensible and reproducible.",
            None))
            
        # 翻译磁贴
        tile_titles = ["Project", "Database", "Simulation", "Settings"]
        for tile, title in zip(self.tiles, tile_titles):
            tile.retranslateUi(title)

    def resizeEvent(self, event):
        """处理窗口大小调整事件，使布局自适应"""
        super().resizeEvent(event)
        # 可以在这里添加特定的响应式逻辑
        # 目前使用GridLayout已经具备了基本的响应式能力