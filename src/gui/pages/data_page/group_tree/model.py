from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt

from .ui import GroupItem


class GroupTreeModel(QAbstractItemModel):
    COLUMN_COUNT = 1

    def __init__(self, parent=None):
        super().__init__(parent)
        self._root = GroupItem("Root")
        self._groups: list[GroupItem] = []
        self._ungrouped_item = GroupItem.ungroupedItem()
        self._all_data_item = GroupItem.allDataItem()

        self._root.appendChild(self._all_data_item)
        self._root.appendChild(self._ungrouped_item)

    def index(
        self, row: int, column: int, parent: QModelIndex = QModelIndex()
    ) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        parent_item = self._root
        if parent.isValid():
            parent_item = parent.internalPointer()

        child = parent_item.child(row)
        if child:
            return self.createIndex(row, column, child)
        return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent

        if parent_item is None or parent_item is self._root:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if not parent.isValid():
            return self._root.childCount()

        parent_item = parent.internalPointer()
        return parent_item.childCount()

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return self.COLUMN_COUNT

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        item = index.internalPointer()
        return item.data(index.column(), role)

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        item = index.internalPointer()
        if item.is_category:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

        return (
            Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEditable
        )

    def setData(
        self, index: QModelIndex, value: str, role: int = Qt.ItemDataRole.EditRole
    ) -> bool:
        if role != Qt.ItemDataRole.EditRole:
            return False

        if not index.isValid():
            return False

        item = index.internalPointer()
        if item.is_category:
            return False

        item.name = value
        self.dataChanged.emit(index, index, [role])
        return True

    def loadGroups(self, groups: list[tuple[int, str]]) -> None:
        self.beginResetModel()
        self._groups.clear()
        for group_id, name in groups:
            item = GroupItem(name, group_id=group_id)
            self._groups.append(item)
            self._ungrouped_item.appendChild(item)
        self.endResetModel()

    def addGroup(self, name: str) -> GroupItem:
        self.beginResetModel()
        item = GroupItem(name)
        self._groups.append(item)
        self._ungrouped_item.appendChild(item)
        self.endResetModel()
        return item

    def removeGroup(self, group_id: int) -> bool:
        item = next((g for g in self._groups if g.group_id == group_id), None)
        if not item:
            return False

        self.beginResetModel()
        self._groups.remove(item)
        self._ungrouped_item.children.remove(item)
        self.endResetModel()
        return True

    def renameGroup(self, group_id: int, new_name: str) -> bool:
        item = next((g for g in self._groups if g.group_id == group_id), None)
        if not item:
            return False

        item.name = new_name
        for row in range(self._ungrouped_item.childCount()):
            child = self._ungrouped_item.child(row)
            if child is item:
                idx = self.index(row, 0)
                self.dataChanged.emit(idx, idx, [Qt.ItemDataRole.DisplayRole])
                break
        return True

    def getSelectedGroupId(self, index: QModelIndex) -> int | None:
        if not index.isValid():
            return None
        item = index.internalPointer()
        return item.group_id

    def getItemAtIndex(self, index: QModelIndex) -> GroupItem | None:
        if not index.isValid():
            return None
        return index.internalPointer()

    def getAllGroups(self) -> list[GroupItem]:
        return list(self._groups)

    def getAllDataIndex(self) -> QModelIndex:
        return self.index(0, 0)

    def getUngroupedIndex(self) -> QModelIndex:
        return self.index(1, 0)

    def getGroupIndex(self, group_id: int) -> QModelIndex | None:
        for row in range(self._ungrouped_item.childCount()):
            child = self._ungrouped_item.child(row)
            if child.group_id == group_id:
                return self.index(row, 0, self.getUngroupedIndex())
        return None
