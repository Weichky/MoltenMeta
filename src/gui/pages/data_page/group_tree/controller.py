import logging

from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QObject, Signal

from application import AppContext
from domain import DataGroupSnapshot

from .context_menu import ContextMenuFactory
from .model import NodeType, TreeNodeData, PAGE_SIZE


_logger = logging.getLogger(__name__)


def _translate(context: str, text: str) -> str:
    return QtCore.QCoreApplication.translate(context, text)


class GroupTreeController(QObject):
    selectionChanged = Signal(object)
    # PySide6 Signal: use `list` instead of `list[int]` due to type hint registration issues
    dataMoved = Signal(list, object)

    def __init__(self, model, tree_view, context: AppContext):
        super().__init__()
        self._model = model
        self._tree_view = tree_view
        self._context = context
        self._user_db_service = context.user_db
        self._logger = context.log.getLogger(__name__)

        self._selected_node: TreeNodeData | None = None
        self._selected_data_ids: list[int] = []
        self._context_menu_factory = ContextMenuFactory(self)
        self._connectSignals()

    def connectSignals(self) -> None:
        pass

    def _connectSignals(self) -> None:
        self._tree_view.selectionModel().selectionChanged.connect(
            self._onSelectionChanged
        )
        self._tree_view.setContextMenuPolicy(
            QtCore.Qt.ContextMenuPolicy.CustomContextMenu
        )
        self._tree_view.customContextMenuRequested.connect(self._onContextMenu)
        self._tree_view.setSelectionMode(
            QtWidgets.QTreeView.SelectionMode.ExtendedSelection
        )

    def loadGroups(self) -> None:
        # Full reload pattern: after any group membership change (create/delete/move),
        # we call loadGroups() which rebuilds the entire tree via loadGroupsWithData().
        # This ensures both the source and destination nodes are correctly refreshed.
        # Individual node updates (like fetchDataForNode) are insufficient because
        # data may exist in multiple groups simultaneously during transitions.
        groups = self._user_db_service.data_groups_repo.findAll()

        ungrouped_count = self._user_db_service.property_value_repo.countUngrouped()

        group_counts = []
        for g in groups:
            if g.id is not None:
                cnt = self._user_db_service.property_value_repo.countByGroupId(g.id)
                group_counts.append((g.id, g.name, cnt))

        ungrouped_items = (
            self._user_db_service.property_value_repo.findUngroupedPaginated(
                PAGE_SIZE, 0
            )
        )
        ungrouped_data = []
        for item in ungrouped_items:
            system_label = self._getSystemLabel(item.system_id)
            ungrouped_data.append(
                {
                    "id": item.id,
                    "system_label": system_label,
                    "value": item.value,
                }
            )

        all_data = {None: ungrouped_data}
        for group_id, name, count in group_counts:
            items = self._user_db_service.property_value_repo.findByGroupIdPaginated(
                group_id, PAGE_SIZE, 0
            )
            data_items = []
            for item in items:
                system_label = self._getSystemLabel(item.system_id)
                data_items.append(
                    {
                        "id": item.id,
                        "system_label": system_label,
                        "value": item.value,
                    }
                )
            all_data[group_id] = data_items

        self._model.loadGroupsWithData(group_counts, ungrouped_count, all_data)

    def _onSelectionChanged(
        self,
        selected: QtCore.QItemSelection,
        deselected: QtCore.QItemSelection,
    ) -> None:
        indexes = selected.indexes()
        if not indexes:
            self._selected_node = None
            self._selected_data_ids = []
            self.selectionChanged.emit(None)
            return

        index = indexes[0]
        node = self._model.getNodeAtIndex(index)

        if node is None:
            return

        if node.node_type == NodeType.DATA:
            self._selected_node = node
            self._selected_data_ids = self._getSelectedDataIds()
        else:
            self._selected_node = node
            self._selected_data_ids = []

        self.selectionChanged.emit(node.id)

    def _getSelectedDataIds(self) -> list[int]:
        data_ids = []
        for index in self._tree_view.selectionModel().selectedIndexes():
            node = self._model.getNodeAtIndex(index)
            if node and node.node_type == NodeType.DATA and node.id is not None:
                data_ids.append(node.id)
        return data_ids

    def _onContextMenu(self, pos: QtCore.QPoint) -> None:
        index = self._tree_view.indexAt(pos)
        if not index.isValid():
            return

        node = self._model.getNodeAtIndex(index)
        menu = self._context_menu_factory.createForNode(node)
        if menu:
            menu.exec(self._tree_view.mapToGlobal(pos))

    def triggerRename(self) -> None:
        if self._selected_node and self._selected_node.node_type == NodeType.GROUP:
            for i, n in enumerate(
                self._model.index(i, 0) for i in range(self._model.rowCount())
            ):
                node = self._model.getNodeAtIndex(n)
                if node is self._selected_node:
                    self._tree_view.setCurrentIndex(n)
                    self._tree_view.edit(n)
                    break

    def triggerDelete(self) -> None:
        if (
            self._selected_node is None
            or self._selected_node.node_type != NodeType.GROUP
        ):
            return

        reply = QtWidgets.QMessageBox.question(
            self._tree_view,
            _translate("GroupTree", "Delete Group"),
            _translate(
                "GroupTree",
                f"Delete group '{self._selected_node.name}'? Data will be moved to Ungrouped.",
            ),
            QtWidgets.QMessageBox.StandardButton.Yes
            | QtWidgets.QMessageBox.StandardButton.No,
        )

        if reply != QtWidgets.QMessageBox.StandardButton.Yes:
            return

        self._deleteGroup(self._selected_node.id)

    def _deleteGroup(self, group_id: int) -> bool:
        try:
            self._user_db_service.property_value_repo.updateGroupIdBatch([], group_id)

            ids = [d["id"] for d in self._getDataForGroup(group_id)]
            if ids:
                self._user_db_service.property_value_repo.updateGroupIdBatch(ids, None)

            self._user_db_service.data_groups_repo.delete(group_id)
            self._model.removeGroupNode(group_id)
            self.loadGroups()
            self._logger.info(f"Deleted group {group_id}")
            self._selected_node = None
            return True
        except Exception as e:
            self._logger.error(f"Failed to delete group: {e}")
            QtWidgets.QMessageBox.critical(
                self._tree_view,
                _translate("GroupTree", "Error"),
                _translate("GroupTree", f"Failed to delete group: {e}"),
            )
            return False

    def _getDataForGroup(self, group_id: int | None) -> list[dict]:
        repo = self._user_db_service.property_value_repo
        if group_id is None:
            items = repo.findUngroupedPaginated(PAGE_SIZE, 0)
        else:
            items = repo.findByGroupIdPaginated(group_id, PAGE_SIZE, 0)

        result = []
        for item in items:
            system_label = self._getSystemLabel(item.system_id)
            result.append(
                {
                    "id": item.id,
                    "system_label": system_label,
                    "value": item.value,
                }
            )
        return result

    def _getSystemLabel(self, system_id: int) -> str:
        try:
            conn = self._user_db_service.db_manager.connection
            cursor = conn.execute("SELECT label FROM systems WHERE id = ?", [system_id])
            row = cursor.fetchone()
            return row["label"] if row else f"System {system_id}"
        except Exception:
            return f"System {system_id}"

    def _showNewGroupDialog(self) -> str | None:
        dialog = QtWidgets.QDialog(self._tree_view)
        dialog.setWindowTitle(_translate("GroupTree", "New Group"))
        dialog.setMinimumSize(350, 150)
        dialog.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum
        )

        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        label = QtWidgets.QLabel(_translate("GroupTree", "Group Name:"))
        layout.addWidget(label)

        line_edit = QtWidgets.QLineEdit()
        line_edit.setPlaceholderText(_translate("GroupTree", "Enter group name..."))
        line_edit.setMinimumHeight(30)
        layout.addWidget(line_edit)

        layout.addSpacing(10)

        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        button_box.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setText(
            _translate("GroupTree", "Create")
        )
        button_box.button(QtWidgets.QDialogButtonBox.StandardButton.Cancel).setText(
            _translate("GroupTree", "Cancel")
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return None

        return line_edit.text().strip()

    def triggerAddToNewGroup(self) -> None:
        data_ids = self._getSelectedDataIds()
        if not data_ids:
            data_ids = (
                [self._selected_node.id]
                if self._selected_node
                and self._selected_node.node_type == NodeType.DATA
                else []
            )

        if not data_ids:
            return

        name = self._showNewGroupDialog()
        if not name:
            return

        if self._user_db_service.data_groups_repo.findByName(name):
            QtWidgets.QMessageBox.warning(
                self._tree_view,
                _translate("GroupTree", "Warning"),
                _translate("GroupTree", "Group name already exists"),
            )
            return

        try:
            snapshot = self._user_db_service.data_groups_repo.save(
                DataGroupSnapshot(name=name)
            )
            self._user_db_service.property_value_repo.updateGroupIdBatch(
                data_ids, snapshot.id
            )
            self.loadGroups()
            self._logger.info(f"Created group '{name}' with {len(data_ids)} items")
            self.dataMoved.emit(data_ids, snapshot.id)
        except Exception as e:
            self._logger.error(f"Failed to create group: {e}")
            QtWidgets.QMessageBox.critical(
                self._tree_view,
                _translate("GroupTree", "Error"),
                _translate("GroupTree", f"Failed to create group: {e}"),
            )

    def triggerRemoveFromGroup(self) -> None:
        data_ids = self._getSelectedDataIds()
        if not data_ids:
            if self._selected_node and self._selected_node.node_type == NodeType.DATA:
                data_ids = [self._selected_node.id]
            else:
                return

        try:
            self._user_db_service.property_value_repo.updateGroupIdBatch(data_ids, None)
            self._logger.info(f"Removed {len(data_ids)} items from group")
            self.dataMoved.emit(data_ids, None)
            self.loadGroups()
        except Exception as e:
            self._logger.error(f"Failed to remove from group: {e}")
            QtWidgets.QMessageBox.critical(
                self._tree_view,
                _translate("GroupTree", "Error"),
                _translate("GroupTree", f"Failed to remove: {e}"),
            )

    def renameGroup(self, group_id: int, new_name: str) -> bool:
        if self._user_db_service.data_groups_repo.findByName(new_name):
            QtWidgets.QMessageBox.warning(
                self._tree_view,
                _translate("GroupTree", "Warning"),
                _translate("GroupTree", "Group name already exists"),
            )
            return False

        try:
            snapshot = self._user_db_service.data_groups_repo.findById(group_id)
            if snapshot is None:
                return False
            updated = DataGroupSnapshot(
                id=group_id,
                name=new_name,
                priority=snapshot.priority,
                created_at=snapshot.created_at,
            )
            self._user_db_service.data_groups_repo.save(updated)
            self._model.renameGroupNode(group_id, new_name)
            self._logger.info(f"Renamed group {group_id} to '{new_name}'")
            return True
        except Exception as e:
            self._logger.error(f"Failed to rename group: {e}")
            QtWidgets.QMessageBox.critical(
                self._tree_view,
                _translate("GroupTree", "Error"),
                _translate("GroupTree", f"Failed to rename: {e}"),
            )
            return False

    def moveDataToGroup(self, data_ids: list[int], target_group_id: int | None) -> None:
        if not data_ids:
            return

        try:
            self._user_db_service.property_value_repo.updateGroupIdBatch(
                data_ids, target_group_id
            )
            self._logger.info(f"Moved {len(data_ids)} items to group {target_group_id}")
            self.dataMoved.emit(data_ids, target_group_id)
        except Exception as e:
            self._logger.error(f"Failed to move data: {e}")
            QtWidgets.QMessageBox.critical(
                self._tree_view,
                _translate("GroupTree", "Error"),
                _translate("GroupTree", f"Failed to move data: {e}"),
            )

    def fetchDataForNode(self, group_id: int | None) -> None:
        repo = self._user_db_service.property_value_repo
        limit = PAGE_SIZE
        offset = 0

        if group_id is None:
            items = repo.findUngroupedPaginated(limit, offset)
        else:
            items = repo.findByGroupIdPaginated(group_id, limit, offset)

        data_items = []
        for item in items:
            system_label = self._getSystemLabel(item.system_id)
            data_items.append(
                {
                    "id": item.id,
                    "system_label": system_label,
                    "value": item.value,
                }
            )

        self._model.setDataForGroup(group_id, data_items)

    def handleDrop(self, data_ids: list[int], target_node: TreeNodeData) -> None:
        if not data_ids:
            return

        target_group_id = target_node.id

        if target_node.node_type == NodeType.UNGROUPED:
            target_group_id = None
        elif target_node.node_type == NodeType.GROUP:
            target_group_id = target_node.id
        else:
            QtWidgets.QMessageBox.warning(
                self._tree_view,
                _translate("GroupTree", "Warning"),
                _translate("GroupTree", "Cannot drop data onto another data item"),
            )
            return

        self.moveDataToGroup(data_ids, target_group_id)
        self.loadGroups()

    def isGroupLoaded(self, group_id: int | None) -> bool:
        return self._model.isGroupLoaded(group_id)
