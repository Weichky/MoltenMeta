import logging

from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QObject, QCoreApplication

from application import AppContext
from application.service.user_db_service import UserDbService

from .ui import UiDataPage
from .model import DataTableModel
from .tables import TABLE_TO_REPO_PROPERTY


_logger = logging.getLogger(__name__)


def _translate(context: str, text: str) -> str:
    return QCoreApplication.translate(context, text)


class DataController(QObject):
    def __init__(self, ui: UiDataPage, context: AppContext, group_tree=None):
        super().__init__()
        self.ui = ui
        self._context = context
        self._db_manager = context.user_db.db_manager
        self._user_db_service: UserDbService = context.user_db
        self._logger = context.log.getLogger(__name__)
        self._group_tree = group_tree

        self._model: DataTableModel | None = None

        self.ui.table_view.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked
            | QtWidgets.QAbstractItemView.EditTrigger.EditKeyPressed
            | QtWidgets.QAbstractItemView.EditTrigger.AnyKeyPressed
        )

        # Enable stretching for the last section of the horizontal header
        self.ui.table_view.horizontalHeader().setStretchLastSection(True)

    def connectSignals(self):
        self._loadTableList()
        self._loadGroups()

        self.ui.table_combo.currentIndexChanged.connect(self._onTableSelected)
        self.ui.refresh_button.clicked.connect(self._onRefreshClicked)
        self.ui.save_button.clicked.connect(self._onSaveClicked)
        self.ui.cancel_button.clicked.connect(self._onCancelClicked)
        self.ui.add_button.clicked.connect(self._onAddClicked)
        self.ui.import_button.clicked.connect(self._onImportClicked)

        if self._group_tree:
            self._group_tree.groupSelectionChanged.connect(
                self._onGroupSelectionChanged
            )
            self._group_tree.controller.connectSignals()

        self._context.i18n.language_changed.connect(self.ui.retranslateUi)

        if self.ui.table_combo.count() > 0:
            self._onTableSelected(0)

    def _getRepository(self, table_name: str):
        """Get the repository for a predefined table, or None if not found."""
        repo_property = TABLE_TO_REPO_PROPERTY.get(table_name)
        if repo_property:
            return getattr(self._user_db_service, repo_property, None)
        return None

    def _loadGroups(self) -> None:
        if self._group_tree:
            try:
                groups = self._user_db_service.data_groups_repo.findAll()
                group_tuples = [(g.id, g.name) for g in groups if g.id is not None]
                self._group_tree.loadGroups(group_tuples)
            except Exception as e:
                self._logger.warning(f"Failed to load groups: {e}")

    def _onGroupSelectionChanged(self, group_id: int | None) -> None:
        if self._model and self._model.getTableName() == "property_values":
            self._model.setGroupFilter(group_id)

    def _onImportClicked(self) -> None:
        from PySide6.QtWidgets import QFileDialog, QMessageBox

        file_path, _ = QFileDialog.getOpenFileName(
            self.ui.table_view,
            self.tr("Import CSV"),
            "",
            self.tr("CSV Files (*.csv);;All Files (*.*)"),
        )

        if not file_path:
            return

        result = self._user_db_service.importPropertyValuesFromCsv(file_path)

        if result.success:
            self._logger.info(
                f"Imported {result.imported_count} values from {file_path} into group '{result.group_name}'"
            )
            QMessageBox.information(
                self.ui.table_view,
                self.tr("Import Successful"),
                self.tr(
                    f"Imported {result.imported_count} values.\n"
                    f"Group: {result.group_name}"
                ),
            )
            self._loadGroups()
        else:
            error_details = "\n".join(
                f"Row {e.row}: {e.message}" + (f" - {e.detail}" if e.detail else "")
                for e in result.errors
            )
            self._logger.warning(f"Import failed from {file_path}: {error_details}")
            QMessageBox.critical(
                self.ui.table_view,
                self.tr("Import Failed"),
                error_details,
            )

    def _loadTableList(self) -> None:
        conn = self._db_manager.connection
        if not conn:
            return

        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
        tables = cursor.fetchall()

        self.ui.table_combo.clear()
        for row in tables:
            table_name = row["name"]
            self.ui.table_combo.addItem(table_name, table_name)

        if self.ui.table_combo.count() > 0:
            self.ui.table_combo.setCurrentIndex(0)

    def _onTableSelected(self, index: int) -> None:
        if index < 0:
            return

        table_name = self.ui.table_combo.itemData(index)
        if not table_name:
            return

        if self._model:
            self._model.dataChanged.disconnect(self._onDataChanged)

        self._model = DataTableModel(self._db_manager, self._user_db_service)
        self._model.setTable(table_name)
        self._model.dataChanged.connect(self._onDataChanged)

        self.ui.table_view.setModel(self._model)
        self.ui.table_view.resizeColumnsToContents()

        # Reapply header settings for the new model
        self.ui.table_view.horizontalHeader().setStretchLastSection(True)

    def _onDataChanged(
        self,
        top_left: QtCore.QModelIndex,
        bottom_right: QtCore.QModelIndex,
        roles: list[int],
    ) -> None:
        if self._model and self._model.hasPendingChanges():
            self.ui.save_button.setEnabled(True)
            self.ui.cancel_button.setEnabled(True)
        else:
            self.ui.save_button.setEnabled(False)
            self.ui.cancel_button.setEnabled(False)

    def _onRefreshClicked(self) -> None:
        if self._model:
            self._model.refreshAll()
            self._updateRowCountLabel()

    def _onSaveClicked(self) -> None:
        if not self._model:
            return

        changes = self._model.getPendingChanges()
        if not changes:
            return

        conn = self._db_manager.connection
        if not conn:
            return

        table_name = self._model.getTableName()
        primary_key = self._model.getPrimaryKey()

        if not table_name or not primary_key:
            return

        try:
            for row_idx, row_changes in changes.items():
                if row_idx >= len(self._model._data):
                    continue

                current_row = self._model._data[row_idx]

                set_clauses = []
                values = []
                for col_name, new_value in row_changes.items():
                    set_clauses.append(f"{col_name} = ?")
                    values.append(new_value)

                if not set_clauses:
                    continue

                pk_value = current_row.get(primary_key)
                if pk_value is None:
                    continue

                sql = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE {primary_key} = ?"
                values.append(pk_value)

                conn.execute(sql, values)

            conn.commit()

            self._model.refreshAll()

            self._model._pending_changes.clear()

            self.ui.save_button.setEnabled(False)
            self.ui.cancel_button.setEnabled(False)

            self._logger.info(f"Saved {len(changes)} row(s) in table {table_name}")

        except Exception as e:
            conn.rollback()
            self._logger.error(f"Failed to save changes: {e}")
            error_title = _translate("DataController", "Error")
            error_msg = _translate("DataController", "Failed to save changes:")
            QtWidgets.QMessageBox.critical(
                self.ui.table_view,
                error_title,
                error_msg + f" {e}",
            )

    def _onCancelClicked(self) -> None:
        if not self._model:
            return

        reply = QtWidgets.QMessageBox.question(
            self.ui.table_view,
            _translate("DataController", "Discard changes?"),
            _translate(
                "DataController",
                "Are you sure you want to discard all unsaved changes?",
            ),
            QtWidgets.QMessageBox.StandardButton.Yes
            | QtWidgets.QMessageBox.StandardButton.No,
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self._model.discardChanges()
            self.ui.save_button.setEnabled(False)
            self.ui.cancel_button.setEnabled(False)

    def _onAddClicked(self) -> None:
        from .dialogs import AddDialog

        dialog = AddDialog(self._db_manager, self._user_db_service, self.ui.table_view)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self._onRefreshClicked()

    def _updateRowCountLabel(self) -> None:
        rows_label = _translate("DataController", "Rows:")
        if self._model:
            total = self._model.getTotalCount()
            self.ui.row_count_label.setText(f"{rows_label} {total}")
        else:
            self.ui.row_count_label.setText(f"{rows_label} 0")
