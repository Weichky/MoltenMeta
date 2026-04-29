from typing import Any

from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QObject


class PlaceholderTreeItem:
    def __init__(self, name: str):
        self.name = name
        self.children: list["PlaceholderTreeItem"] = []
        self.parent: "PlaceholderTreeItem | None" = None

    def appendChild(self, child: "PlaceholderTreeItem") -> None:
        child.parent = self
        self.children.append(child)

    def child(self, row: int) -> "PlaceholderTreeItem | None":
        if 0 <= row < len(self.children):
            return self.children[row]
        return None

    def childCount(self) -> int:
        return len(self.children)

    def row(self) -> int:
        if self.parent:
            return self.parent.children.index(self)
        return 0

    def columnCount(self) -> int:
        return 1

    def data(
        self, column: int, role: int = QtCore.Qt.ItemDataRole.DisplayRole
    ) -> str | None:
        if column == 0 and role == QtCore.Qt.ItemDataRole.DisplayRole:
            return self.name
        return None


class PlaceholderTreeModel(QtCore.QAbstractItemModel):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self._root = PlaceholderTreeItem("Root")

    def index(
        self, row: int, column: int, parent: QtCore.QModelIndex = QtCore.QModelIndex()
    ) -> QtCore.QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        parent_item = self._itemFromIndex(parent)
        child = parent_item.child(row)
        if child:
            return self.createIndex(row, column, child)
        return QtCore.QModelIndex()

    def parent(self, child: QtCore.QModelIndex) -> QtCore.QModelIndex:
        if not child.isValid():
            return QtCore.QModelIndex()

        child_item = self._itemFromIndex(child)
        parent_item = child_item.parent
        if parent_item == self._root:
            return QtCore.QModelIndex()
        return self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        parent_item = self._itemFromIndex(parent)
        return parent_item.childCount()

    def columnCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return 1

    def data(
        self, index: QtCore.QModelIndex, role: int = QtCore.Qt.ItemDataRole.DisplayRole
    ) -> Any:
        if not index.isValid():
            return None

        item = self._itemFromIndex(index)
        return item.data(index.column(), role)

    def _itemFromIndex(self, index: QtCore.QModelIndex) -> PlaceholderTreeItem:
        if index.isValid():
            return index.internalPointer()
        return self._root


class UiPlaceholderTree(QObject):
    def setupUi(self, parent: QtWidgets.QWidget) -> None:
        if not parent.objectName():
            parent.setObjectName("placeholderTree")

        self.layout = QtWidgets.QVBoxLayout(parent)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.tree_view = QtWidgets.QTreeView()
        self.tree_view.setObjectName("placeholderTreeView")
        self.tree_view.setHeaderHidden(True)
        self.layout.addWidget(self.tree_view, stretch=1)

    def retranslateUi(self) -> None:
        pass
