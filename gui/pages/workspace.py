from PySide6 import QtWidgets
import PySide6QtAds as QtAds

from gui.pages.page_controller import PageController

class Workspace(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.dock_manager = QtAds.CDockManager(self)
        layout.addWidget(self.dock_manager)

        # 控制器
        self.controller = PageController(self.dock_manager)
