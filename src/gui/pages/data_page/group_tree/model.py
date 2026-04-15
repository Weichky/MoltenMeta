from dataclasses import dataclass
from enum import Enum, auto

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel


PAGE_SIZE = 100


class NodeType(Enum):
    UNGROUPED = auto()
    GROUP = auto()
    DATA = auto()


@dataclass(frozen=True)
class TreeNodeData:
    id: int | None
    node_type: NodeType
    name: str
    data_count: int | None = None
    system_label: str | None = None
    value: float | None = None


class GroupTreeModel(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._root_item = self.invisibleRootItem()
        self._item_by_group_id: dict[int | None, QStandardItem] = {}
        self._loaded_groups: set[int | None] = set()

    def loadGroupsWithData(
        self,
        groups: list[tuple[int, str, int]],
        ungrouped_count: int,
        all_data: dict[int | None, list[dict]],
    ) -> None:
        self.clear()
        self._item_by_group_id.clear()
        self._loaded_groups.clear()
        self._root_item = self.invisibleRootItem()

        ungrouped_item = QStandardItem("Ungrouped")
        ungrouped_item.setData(
            TreeNodeData(
                id=None,
                node_type=NodeType.UNGROUPED,
                name="Ungrouped",
                data_count=ungrouped_count,
            ),
            Qt.ItemDataRole.UserRole,
        )
        ungrouped_item.setFlags(
            Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsDropEnabled
        )
        self._root_item.appendRow(ungrouped_item)
        self._item_by_group_id[None] = ungrouped_item

        ungrouped_data = all_data.get(None, [])
        for d in ungrouped_data:
            data_item = QStandardItem()
            label = d.get("system_label") or f"Data {d['id']}"
            value = d.get("value")
            text = f"{label}: {value:.4f}" if value is not None else label
            data_item.setText(text)
            data_item.setData(
                TreeNodeData(
                    id=d["id"],
                    node_type=NodeType.DATA,
                    name=f"Data {d['id']}",
                    system_label=d.get("system_label"),
                    value=value,
                ),
                Qt.ItemDataRole.UserRole,
            )
            data_item.setFlags(
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsDragEnabled
            )
            ungrouped_item.appendRow(data_item)

        self._loaded_groups.add(None)

        for group_id, name, count in groups:
            group_item = QStandardItem(name)
            group_item.setData(
                TreeNodeData(
                    id=group_id,
                    node_type=NodeType.GROUP,
                    name=name,
                    data_count=count,
                ),
                Qt.ItemDataRole.UserRole,
            )
            group_item.setFlags(
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsDropEnabled
                | Qt.ItemFlag.ItemIsEditable
            )
            self._root_item.appendRow(group_item)
            self._item_by_group_id[group_id] = group_item

            group_data = all_data.get(group_id, [])
            for d in group_data:
                data_item = QStandardItem()
                label = d.get("system_label") or f"Data {d['id']}"
                value = d.get("value")
                text = f"{label}: {value:.4f}" if value is not None else label
                data_item.setText(text)
                data_item.setData(
                    TreeNodeData(
                        id=d["id"],
                        node_type=NodeType.DATA,
                        name=f"Data {d['id']}",
                        system_label=d.get("system_label"),
                        value=value,
                    ),
                    Qt.ItemDataRole.UserRole,
                )
                data_item.setFlags(
                    Qt.ItemFlag.ItemIsEnabled
                    | Qt.ItemFlag.ItemIsSelectable
                    | Qt.ItemFlag.ItemIsDragEnabled
                )
                group_item.appendRow(data_item)

            self._loaded_groups.add(group_id)

    def addGroupNode(self, group_id: int, name: str, count: int) -> None:
        group_item = QStandardItem(name)
        group_item.setData(
            TreeNodeData(
                id=group_id,
                node_type=NodeType.GROUP,
                name=name,
                data_count=count,
            ),
            Qt.ItemDataRole.UserRole,
        )
        group_item.setFlags(
            Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsDropEnabled
            | Qt.ItemFlag.ItemIsEditable
        )
        self._root_item.appendRow(group_item)
        self._item_by_group_id[group_id] = group_item
        self._loaded_groups.add(group_id)

    def removeGroupNode(self, group_id: int) -> None:
        if group_id in self._item_by_group_id:
            row = self._item_by_group_id[group_id].row()
            self._root_item.removeRow(row)
            del self._item_by_group_id[group_id]
            self._loaded_groups.discard(group_id)

    def renameGroupNode(self, group_id: int, new_name: str) -> None:
        if group_id in self._item_by_group_id:
            item = self._item_by_group_id[group_id]
            item.setText(new_name)
            node_data = item.data(Qt.ItemDataRole.UserRole)
            if node_data:
                new_data = TreeNodeData(
                    id=node_data.id,
                    node_type=node_data.node_type,
                    name=new_name,
                    data_count=node_data.data_count,
                )
                item.setData(new_data, Qt.ItemDataRole.UserRole)

    def getNodeAtIndex(self, index: QModelIndex) -> TreeNodeData | None:
        if not index.isValid():
            return None
        item = self.itemFromIndex(index)
        if item is None:
            return None
        return item.data(Qt.ItemDataRole.UserRole)

    def getUngroupedIndex(self) -> QModelIndex:
        if None in self._item_by_group_id:
            return self._item_by_group_id[None].index()
        return QModelIndex()

    def getNodeById(self, group_id: int | None) -> TreeNodeData | None:
        if group_id in self._item_by_group_id:
            item = self._item_by_group_id[group_id]
            return item.data(Qt.ItemDataRole.UserRole)
        return None

    def isGroupLoaded(self, group_id: int | None) -> bool:
        return group_id in self._loaded_groups

    def setDataForGroup(self, group_id: int | None, data_items: list[dict]) -> None:
        if group_id not in self._item_by_group_id:
            return

        parent_item = self._item_by_group_id[group_id]
        parent_item.removeRows(0, parent_item.rowCount())

        for d in data_items:
            data_item = QStandardItem()
            label = d.get("system_label") or f"Data {d['id']}"
            value = d.get("value")
            text = f"{label}: {value:.4f}" if value is not None else label
            data_item.setText(text)
            data_item.setData(
                TreeNodeData(
                    id=d["id"],
                    node_type=NodeType.DATA,
                    name=f"Data {d['id']}",
                    system_label=d.get("system_label"),
                    value=value,
                ),
                Qt.ItemDataRole.UserRole,
            )
            data_item.setFlags(
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsDragEnabled
            )
            parent_item.appendRow(data_item)

        self._loaded_groups.add(group_id)
