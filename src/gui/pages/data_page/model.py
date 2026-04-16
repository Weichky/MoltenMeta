import logging
from typing import Any

from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt

from db import DatabaseManager

from .tables import TABLE_TO_REPO_PROPERTY, TABLE_TO_SNAPSHOT_CLASS


_logger = logging.getLogger(__name__)


class DataTableModel(QtCore.QAbstractTableModel):
    DEFAULT_PAGE_SIZE = 1000
    DEFAULT_ROW_COUNT = 100

    def __init__(
        self,
        db_manager: DatabaseManager,
        user_db_service=None,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        self._db_manager = db_manager
        self._user_db_service = user_db_service
        self._table_name: str | None = None
        self._columns: list[str] = []
        self._primary_key: str | None = None
        self._data: list[dict[str, Any]] = []
        self._total_count: int = 0
        self._page_size = self.DEFAULT_PAGE_SIZE
        self._is_loaded = False
        self._snapshot_class = None

        self._pending_changes: dict[int, dict[str, Any]] = {}
        self._original_data: dict[int, dict[str, Any]] = {}
        self._group_id: int | None = None

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
        self._snapshot_class = TABLE_TO_SNAPSHOT_CLASS.get(table_name)
        self._group_id = None

        if table_name:
            self._loadSchema()
            if self._columns:
                self._loadData(0, self.DEFAULT_PAGE_SIZE)
                self._is_loaded = True

        self.endResetModel()

    def setGroupFilter(self, group_id: int | None) -> None:
        if self._table_name != "property_values":
            return
        if self._group_id == group_id:
            return
        self._group_id = group_id
        self.beginResetModel()
        self._data = []
        self._total_count = 0
        self._loadData(0, self.DEFAULT_PAGE_SIZE)
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

        if self._user_db_service and self._snapshot_class:
            repo_property = TABLE_TO_REPO_PROPERTY.get(self._table_name)
            if repo_property:
                repo = getattr(self._user_db_service, repo_property, None)
                if repo:
                    try:
                        if (
                            self._table_name == "property_values"
                            and self._group_id is not None
                        ):
                            snapshots = repo.findByGroupIdPaginated(
                                self._group_id, limit, offset
                            )
                            count_method = getattr(repo, "countByGroupId", None)
                            self._total_count = (
                                count_method(self._group_id) if count_method else 0
                            )
                            start_idx = offset
                            for snapshot in snapshots:
                                record = snapshot.toRecord()
                                if snapshot.id is not None:
                                    record["id"] = snapshot.id
                                self._data.append(record)
                                self._original_data[start_idx] = dict(record)
                                start_idx += 1
                            return
                        elif (
                            self._table_name == "property_values"
                            and self._group_id is None
                        ):
                            snapshots = repo.findUngroupedPaginated(limit, offset)
                            count_method = getattr(repo, "countUngrouped", None)
                            self._total_count = count_method() if count_method else 0
                            start_idx = offset
                            for snapshot in snapshots:
                                record = snapshot.toRecord()
                                if snapshot.id is not None:
                                    record["id"] = snapshot.id
                                self._data.append(record)
                                self._original_data[start_idx] = dict(record)
                                start_idx += 1
                            return

                        if self._table_name == "elements":
                            cursor = conn.execute(
                                f"""SELECT e.*, s.symbol
                                    FROM elements e
                                    LEFT JOIN symbols s ON e.symbol_id = s.id
                                    LIMIT {limit} OFFSET {offset}"""
                            )
                            rows = cursor.fetchall()
                            cursor = conn.execute(
                                f"SELECT COUNT(*) as cnt FROM {self._table_name}"
                            )
                            count_result = cursor.fetchone()
                            self._total_count = (
                                count_result["cnt"] if count_result else 0
                            )

                            start_idx = offset
                            for row in rows:
                                self._data.append(row)
                                self._original_data[start_idx] = dict(row)
                                start_idx += 1
                        else:
                            snapshots: list = repo.findAll()
                            self._total_count = len(snapshots)

                            start_idx = offset
                            for snapshot in snapshots[offset : offset + limit]:
                                record = snapshot.toRecord()
                                if snapshot.id is not None:
                                    record["id"] = snapshot.id
                                self._data.append(record)
                                self._original_data[start_idx] = dict(record)
                                start_idx += 1
                        return
                    except Exception as e:
                        _logger.warning(
                            f"Repository query failed for table '{self._table_name}', "
                            f"falling back to direct SQL: {e}"
                        )

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
