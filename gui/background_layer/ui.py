from PySide6 import QtWidgets
from PySide6.QtCore import (
    Qt,
    QObject,
)

class UiBackgroundLayer(QObject):
    def setupUi(self, background_page: QtWidgets.QWidget):
        layout = QtWidgets.QVBoxLayout(background_page)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = QtWidgets.QLabel(background_page)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.label)
    def retranslateUi(self):
        self.label.setText(u"Background Page")