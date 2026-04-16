from PySide6 import QtWidgets
from PySide6.QtCore import QObject


class UiGroupTree(QObject):
    def setupUi(self, parent: QtWidgets.QWidget) -> None:
        if not parent.objectName():
            parent.setObjectName("groupTree")

        self.layout = QtWidgets.QVBoxLayout(parent)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

    def retranslateUi(self) -> None:
        pass
