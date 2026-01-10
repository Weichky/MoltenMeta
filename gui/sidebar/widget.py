from PySide6.QtWidgets import (
    QDockWidget
)
from PySide6.QtCore import QEvent, Qt, QObject

from i18n import getI18nService

from .ui import UiSidebar

class ResizeEventFilter(QObject):
    def __init__(self, sidebar):
        super().__init__()
        self.sidebar = sidebar

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            self.sidebar._adjust_sidebar_size()
        return False

class SidebarWidget(QDockWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.ui = UiSidebar()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)
        
        # Install event filter to listen for parent window size changes
        self.resize_event_filter = ResizeEventFilter(self)
        parent.installEventFilter(self.resize_event_filter)
        
        # Initial size adjustment
        self._adjustSidebarSize()

        # i18n
        getI18nService().languageChanged.connect(self.retranslateUi)

    def _adjustSidebarSize(self):
        self.ui.adjustSidebarSize(self)

    def retranslateUi(self):
        self.ui.retranslateUi(self)