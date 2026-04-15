from PySide6 import QtWidgets
from PySide6.QtCore import QObject


class UiGroupTree(QObject):
    def setupUi(self, parent: QtWidgets.QWidget) -> None:
        if not parent.objectName():
            parent.setObjectName("groupTree")

        self.layout = QtWidgets.QVBoxLayout(parent)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.tree_view = QtWidgets.QTreeView()
        self.tree_view.setObjectName("groupTreeView")
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.layout.addWidget(self.tree_view, stretch=1)

    def retranslateUi(self) -> None:
        pass
