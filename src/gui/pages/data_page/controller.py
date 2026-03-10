from typing import Any

from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QObject, Qt, QCoreApplication

from application import AppContext
from db import DatabaseManager

from .ui import UiDataPage


def _translate(context: str, text: str) -> str:
    return QCoreApplication.translate(context, text)


class DataTableModel(QtCore.QAbstractTableModel):
    DEFAULT_PAGE_SIZE = 1000
    DEFAULT_ROW_COUNT = 100

    def __init__(
        self,
        db_manager: DatabaseManager,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        self._db_manager = db_manager
        self._table_name: str | None = None
        self._columns: list[str] = []
        self._primary_key: str | None = None
        self._data: list[dict[str, Any]] = []
        self._total_count: int = 0
        self._page_size = self.DEFAULT_PAGE_SIZE
        self._is_loaded = False

        self._pending_changes: dict[int, dict[str, Any]] = {}
        self._original_data: dict[int, dict[str, Any]] = {}

    def setTable(self, table_name: str) -> None:
        self.beginResetModel()
        self._table_name = table_name
        self._columns = []
        self._primary_key = None
        self._data = []
        self._total_count = 0
        self._is_loaded = False
        self._pending_changes.clear()
        self._original_data.clear()

        if table_name:
            self._loadSchema()
            if self._columns:
                self._loadData(0, self.DEFAULT_PAGE_SIZE)
                self._is_loaded = True

        self.endResetModel()

    def _loadSchema(self) -> None:
        conn = self._db_manager.connection
        if not conn:
            return

        cursor = conn.execute(f"PRAGMA table_info({self._table_name})")
        rows = cursor.fetchall()

        self._columns = [row["name"] for row in rows]

        if self._table_name == "elements":
            if "symbol_id" in self._columns:
                self._columns.remove("symbol_id")
            self._columns.insert(1, "symbol")

        cursor = conn.execute(f"PRAGMA index_list({self._table_name})")
        indexes = cursor.fetchall()

        for idx in indexes:
            if idx.get("origin"):
                cursor = conn.execute(f"PRAGMA index_info({idx['name']})")
                cols = cursor.fetchall()
                if cols and len(cols) == 1:
                    self._primary_key = cols[0]["name"]
                    break

        if not self._primary_key and self._columns:
            self._primary_key = self._columns[0]

    def _loadData(self, offset: int, limit: int) -> None:
        conn = self._db_manager.connection
        if not conn:
            return

        if self._table_name == "elements":
            cursor = conn.execute(
                f"""SELECT e.*, s.symbol 
                    FROM elements e 
                    LEFT JOIN symbols s ON e.symbol_id = s.id 
                    LIMIT {limit} OFFSET {offset}"""
            )
        else:
            cursor = conn.execute(
                f"SELECT * FROM {self._table_name} LIMIT {limit} OFFSET {offset}"
            )
        rows = cursor.fetchall()

        cursor = conn.execute(f"SELECT COUNT(*) as cnt FROM {self._table_name}")
        count_result = cursor.fetchone()
        self._total_count = count_result["cnt"] if count_result else 0

        start_idx = offset
        for row in rows:
            self._data.append(row)
            self._original_data[start_idx] = dict(row)
            start_idx += 1

    def rowCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        if not self._is_loaded:
            return 0
        return len(self._data)

    def columnCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return len(self._columns)

    def data(
        self, index: QtCore.QModelIndex, role: int = Qt.ItemDataRole.DisplayRole
    ) -> Any:
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        if row >= len(self._data):
            return None

        if col >= len(self._columns):
            return None

        column_name = self._columns[col]
        value = self._data[row].get(column_name)

        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return str(value) if value is not None else ""
        elif role == Qt.ItemDataRole.ToolTipRole:
            return str(value) if value is not None else ""

        return None

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            if section < len(self._columns):
                return self._columns[section]

        return None

    def flags(self, index: QtCore.QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        column_name = self._columns[index.column()]

        if column_name == "symbol":
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

        return (
            Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEditable
        )

    def setData(
        self,
        index: QtCore.QModelIndex,
        value: Any,
        role: int = Qt.ItemDataRole.EditRole,
    ) -> bool:
        if not index.isValid():
            return False

        if role != Qt.ItemDataRole.EditRole:
            return False

        row = index.row()
        col = index.column()

        if row >= len(self._data) or col >= len(self._columns):
            return False

        column_name = self._columns[col]

        if column_name not in self._data[row]:
            return False

        if self._data[row][column_name] == value:
            return True

        self._data[row][column_name] = value

        if row not in self._pending_changes:
            self._pending_changes[row] = {}
        self._pending_changes[row][column_name] = value

        self.dataChanged.emit(index, index, [role])
        return True

    def canFetchMore(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> bool:
        if not self._is_loaded:
            return False
        return len(self._data) < self._total_count

    def fetchMore(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> None:
        if not self._is_loaded:
            return

        if len(self._data) >= self._total_count:
            return

        self.beginInsertRows(
            QtCore.QModelIndex(), len(self._data), len(self._data) + self._page_size - 1
        )

        offset = len(self._data)
        self._loadData(offset, self._page_size)

        self.endInsertRows()

    def getPendingChanges(self) -> dict[int, dict[str, Any]]:
        return dict(self._pending_changes)

    def hasPendingChanges(self) -> bool:
        return bool(self._pending_changes)

    def discardChanges(self) -> None:
        self.beginResetModel()

        for row, original in self._original_data.items():
            if row < len(self._data):
                self._data[row] = dict(original)

        self._pending_changes.clear()
        self.endResetModel()

    def getTotalCount(self) -> int:
        return self._total_count

    def getPrimaryKey(self) -> str | None:
        return self._primary_key

    def getTableName(self) -> str | None:
        return self._table_name

    def refreshAll(self) -> None:
        self.beginResetModel()
        self._data.clear()
        self._original_data.clear()
        self._loadData(0, self._page_size)
        self.endResetModel()


class DataController(QObject):
    def __init__(self, ui: UiDataPage, context: AppContext):
        super().__init__()
        self.ui = ui
        self._context = context
        self._db_manager = context.user_db._db_manager
        self._logger = context.log.getLogger(__name__)

        self._model: DataTableModel | None = None

        self.ui.table_view.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked
            | QtWidgets.QAbstractItemView.EditTrigger.EditKeyPressed
            | QtWidgets.QAbstractItemView.EditTrigger.AnyKeyPressed
        )

    def connectSignals(self):
        self._loadTableList()

        self.ui.table_combo.currentIndexChanged.connect(self._onTableSelected)
        self.ui.refresh_button.clicked.connect(self._onRefreshClicked)
        self.ui.save_button.clicked.connect(self._onSaveClicked)
        self.ui.cancel_button.clicked.connect(self._onCancelClicked)
        self.ui.add_button.clicked.connect(self._onAddClicked)

        self._context.i18n.language_changed.connect(self.ui.retranslateUi)

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

        self._model = DataTableModel(self._db_manager)
        self._model.setTable(table_name)
        self._model.dataChanged.connect(self._onDataChanged)

        self.ui.table_view.setModel(self._model)
        self.ui.table_view.resizeColumnsToContents()

        self._updateRowCountLabel()

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

        dialog = AddDialog(self._db_manager, self.ui.table_view)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self._onRefreshClicked()

    def _updateRowCountLabel(self) -> None:
        rows_label = _translate("DataController", "Rows:")
        if self._model:
            total = self._model.getTotalCount()
            self.ui.row_count_label.setText(f"{rows_label} {total}")
        else:
            self.ui.row_count_label.setText(f"{rows_label} 0")
