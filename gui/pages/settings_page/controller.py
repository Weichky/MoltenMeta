from PySide6 import QtWidgets
from PySide6.QtCore import QObject, Signal

from .ui import UiSettingsPage


class SettingsController(QObject):
    def __init__(self, ui: UiSettingsPage):
        super().__init__()
        self.ui = ui
        self._setupNavigation()

    def _setupNavigation(self):
        """设置导航按钮和页面切换逻辑"""
        # Use exclusive button group to ensure only one button is checked
        self.button_group = QtWidgets.QButtonGroup()
        self.button_group.addButton(self.ui.general_button)
        self.button_group.addButton(self.ui.log_button)
        self.button_group.setExclusive(True)
        
        # Connect button clicks to page switching
        self.ui.general_button.clicked.connect(lambda: self.ui.content_area.setCurrentIndex(0))
        self.ui.log_button.clicked.connect(lambda: self.ui.content_area.setCurrentIndex(1))

    def connectSignals(self):
        """连接所有信号，如果以后有其他信号需要连接，可以在这里添加"""
        pass