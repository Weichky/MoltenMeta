import logging

from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QObject, Signal, QCoreApplication

from application import AppContext
from domain import DataGroupSnapshot

_logger = logging.getLogger(__name__)


def _translate(context: str, text: str) -> str:
    return QCoreApplication.translate(context, text)


class GroupTreeController(QObject):
    selectionChanged = Signal(object)

    def __init__(self, model, ui, context: AppContext):
        super().__init__()
        self._model = model
        self._ui = ui
        self._context = context
        self._user_db_service = context.user_db
        self._logger = context.log.getLogger(__name__)

        self._selected_group_id: int | None = None

    def connectSignals(self) -> None:
        self._ui.add_button.clicked.connect(self._onAddClicked)
        self._ui.delete_button.clicked.connect(self._onDeleteClicked)
        self._ui.tree_view.clicked.connect(self._onIndexClicked)
        self._ui.tree_view.selectionModel().selectionChanged.connect(
            self._onSelectionChanged
        )

    def loadGroups(self, groups: list[tuple[int, str]]) -> None:
        self._model.loadGroups(groups)
        self._ui.tree_view.expandAll()
        self._ui.tree_view.setCurrentIndex(self._model.getAllDataIndex())

    def _onAddClicked(self) -> None:
        dialog = QtWidgets.QInputDialog(self._ui.tree_view)
        dialog.setWindowTitle(_translate("GroupTree", "New Group"))
        dialog.setLabelText(_translate("GroupTree", "Group name:"))
        dialog.setOkButtonText(_translate("GroupTree", "Create"))
        dialog.setCancelButtonText(_translate("GroupTree", "Cancel"))

        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            name = dialog.textValue().strip()
            if name:
                self._createGroup(name)

    def _createGroup(self, name: str) -> DataGroupSnapshot | None:
        try:
            snapshot = self._user_db_service.data_groups_repo.save(
                DataGroupSnapshot(name=name)
            )
            self._model.addGroup(name)
            self._logger.info(f"Created group: {name}")
            return snapshot
        except Exception as e:
            self._logger.error(f"Failed to create group: {e}")
            QtWidgets.QMessageBox.critical(
                self._ui.tree_view,
                _translate("GroupTree", "Error"),
                _translate("GroupTree", f"Failed to create group: {e}"),
            )
            return None

    def _onDeleteClicked(self) -> None:
        if self._selected_group_id is None:
            return

        item = self._model.getItemAtIndex(self._ui.tree_view.currentIndex())
        if not item or item.is_category:
            return

        reply = QtWidgets.QMessageBox.question(
            self._ui.tree_view,
            _translate("GroupTree", "Delete Group"),
            _translate(
                "GroupTree",
                "Are you sure you want to delete this group? "
                "Data will be moved to Ungrouped.",
            ),
            QtWidgets.QMessageBox.StandardButton.Yes
            | QtWidgets.QMessageBox.StandardButton.No,
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self._deleteGroup(self._selected_group_id)

    def _deleteGroup(self, group_id: int) -> bool:
        try:
            self._user_db_service.data_groups_repo.delete(group_id)
            self._model.removeGroup(group_id)
            self._logger.info(f"Deleted group {group_id}")
            self._selected_group_id = None
            self._ui.delete_button.setEnabled(False)
            return True
        except Exception as e:
            self._logger.error(f"Failed to delete group: {e}")
            QtWidgets.QMessageBox.critical(
                self._ui.tree_view,
                _translate("GroupTree", "Error"),
                _translate("GroupTree", f"Failed to delete group: {e}"),
            )
            return False

    def _onIndexClicked(self, index: QtCore.QModelIndex) -> None:
        item = self._model.getItemAtIndex(index)
        if item:
            self._selected_group_id = item.group_id
            enable_delete = not item.is_category and item.group_id is not None
            self._ui.delete_button.setEnabled(enable_delete)
            self.selectionChanged.emit(item.group_id)

    def _onSelectionChanged(
        self,
        selected: QtCore.QItemSelection,
        deselected: QtCore.QItemSelection,
    ) -> None:
        indexes = selected.indexes()
        if indexes:
            self._onIndexClicked(indexes[0])
        else:
            self.selectionChanged.emit(None)
