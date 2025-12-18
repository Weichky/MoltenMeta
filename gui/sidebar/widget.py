from PySide6.QtWidgets import (
    QDockWidget
)

from .ui import UiSidebar

class SidebarWidget(QDockWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.ui = UiSidebar()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)