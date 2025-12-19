from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QLocale, QTranslator, QCoreApplication

from .ui import UiSettingsPage

class SettingsPage(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = UiSettingsPage()
        self.ui.setupUi(self)
        self.ui.retranslateUi()

        # 连接信号
        self.ui._connect_signals()
        
        # 连接语言选择信号
        self.ui.lang_combo.currentIndexChanged.connect(self._on_language_changed)
    
    def _on_language_changed(self, index):
        """处理语言更改事件"""
        # 获取选中的语言代码
        lang_code = self.ui.lang_combo.itemData(index)
        
        # 这里应该发送信号通知主窗口更改语言
        # 在实际应用中，你需要实现完整的语言切换机制
        print(f"Language changed to: {lang_code}")