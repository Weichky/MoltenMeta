import logging
from PySide6 import QtWidgets
from PySide6.QtCore import Qt, QCoreApplication

from ..schemas import ENTITY_TYPES, ENTITY_FIELDS, getFkDisplayColumn
from ..tables import TABLE_TO_REPO_PROPERTY, TABLE_TO_SNAPSHOT_CLASS


_logger = logging.getLogger(__name__)


def _translate(context: str, text: str) -> str:
    return QCoreApplication.translate(context, text)


class AddDialog(QtWidgets.QDialog):
    def __init__(
        self,
        db_manager,
        user_db_service=None,
        parent=None,
        quick_mode: bool = False,
        entity_type: str | None = None,
    ):
        super().__init__(parent)
        self._db_manager = db_manager
        self._user_db_service = user_db_service
        self._quick_mode = quick_mode
        self._selected_type = entity_type
        self._form_widgets: dict[str, QtWidgets.QWidget] = {}
        self._setupUi()
        self._init()

    def _setupUi(self):
        self.setWindowTitle(_translate("AddDialog", "Add Data"))
        if self._quick_mode:
            self.resize(450, 300)
        else:
            self.resize(700, 500)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(8, 8, 8, 8)

        if not self._quick_mode:
            main_layout.addWidget(self._createSidebar())
        else:
            form_area = self._createFormArea()
            form_area.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Expanding,
            )
            main_layout.addWidget(form_area)

        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._onAccepted)
        button_box.rejected.connect(self.reject)
        self.ok_button = button_box.button(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setText(_translate("AddDialog", "Add"))
        main_layout.addWidget(button_box)

    def _createSidebar(self) -> QtWidgets.QWidget:
        content_layout = QtWidgets.QHBoxLayout()
        content_layout.setSpacing(8)

        left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(4)

        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setMinimumHeight(30)
        self.search_input.setPlaceholderText(_translate("AddDialog", "Search..."))
        self.search_input.textChanged.connect(self._onSearchChanged)
        left_layout.addWidget(self.search_input)

        self.type_list = QtWidgets.QListWidget()
        self.type_list.setMaximumWidth(180)
        self.type_list.currentRowChanged.connect(self._onTypeSelected)
        left_layout.addWidget(self.type_list)

        content_layout.addWidget(left_widget)

        right_widget = self._createFormArea()
        content_layout.addWidget(right_widget, 3)

        container = QtWidgets.QWidget()
        container.setLayout(content_layout)
        return container

    def _createFormArea(self) -> QtWidgets.QWidget:
        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        self.form_container = QtWidgets.QWidget()
        self.form_container.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )

        self.form_layout = QtWidgets.QVBoxLayout(self.form_container)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setSpacing(8)

        form_scroll = QtWidgets.QScrollArea()
        form_scroll.setWidget(self.form_container)
        form_scroll.setWidgetResizable(True)
        form_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        right_layout.addWidget(form_scroll, 1)

        return right_widget

    def _init(self):
        if self._quick_mode and self._selected_type:
            self._buildForm()
        elif not self._quick_mode:
            self._loadEntityTypes()

    def _loadEntityTypes(self, filter_text: str = ""):
        self.type_list.clear()
        for type_key, type_label in ENTITY_TYPES:
            if not filter_text or filter_text.lower() in type_label.lower():
                item = QtWidgets.QListWidgetItem(type_label)
                item.setData(Qt.ItemDataRole.UserRole, type_key)
                self.type_list.addItem(item)

        if self.type_list.count() > 0:
            self.type_list.setCurrentRow(0)

    def _onSearchChanged(self, text: str):
        self._loadEntityTypes(text)

    def _onTypeSelected(self, row: int):
        if row < 0:
            return
        item = self.type_list.item(row)
        self._selected_type = item.data(Qt.ItemDataRole.UserRole)
        self._buildForm()

    def _buildForm(self):
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._form_widgets.clear()

        self.form_layout.addStretch(1)

        fields = ENTITY_FIELDS.get(self._selected_type, [])
        for field in fields:
            row_widget = QtWidgets.QWidget()
            row_layout = QtWidgets.QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(8)

            label = QtWidgets.QLabel(field.label_key)
            label.setMinimumWidth(100)
            label.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed
            )
            row_layout.addWidget(label)

            if field.field_type == "fk":
                combo = QtWidgets.QComboBox()
                combo.setObjectName(field.name)
                combo.setMaxVisibleItems(8)
                combo.setMaximumHeight(100)
                combo.setEditable(True)
                self._loadForeignKeyData(combo, field.fk_target)
                row_layout.addWidget(combo, 1)
                self._form_widgets[field.name] = combo

                add_btn = QtWidgets.QPushButton("+")
                # add_btn.setFixedWidth(20)
                add_btn.setToolTip(_translate("AddDialog", "Quick add"))
                add_btn.clicked.connect(
                    lambda checked, fk_target=field.fk_target, combo=combo: (
                        self._quickAdd(fk_target, combo)
                    )
                )
                row_layout.addWidget(add_btn)
            elif field.field_type == "number":
                input_widget = QtWidgets.QLineEdit()
                input_widget.setMinimumHeight(30)
                input_widget.setObjectName(field.name)
                # Add validator for numeric input
                validator = QtWidgets.QDoubleValidator()
                validator.setNotation(
                    QtWidgets.QDoubleValidator.Notation.StandardNotation
                )
                input_widget.setValidator(validator)
                row_layout.addWidget(input_widget, 1)
                self._form_widgets[field.name] = input_widget
            else:
                input_widget = QtWidgets.QLineEdit()
                input_widget.setMinimumHeight(30)
                input_widget.setObjectName(field.name)
                row_layout.addWidget(input_widget, 1)
                self._form_widgets[field.name] = input_widget

            self.form_layout.addWidget(row_widget)

        self.form_layout.addStretch(1)

    def _loadForeignKeyData(self, combo: QtWidgets.QComboBox, fk_table: str):
        combo.blockSignals(True)
        combo.clear()

        conn = self._db_manager.connection
        if not conn:
            combo.blockSignals(False)
            return

        display_column = getFkDisplayColumn(fk_table)

        try:
            cursor = conn.execute(
                f"SELECT id, {display_column} FROM {fk_table} ORDER BY {display_column}"
            )
            rows = cursor.fetchall()
            for row in rows:
                display = (
                    str(row[display_column])
                    if row[display_column]
                    else f"ID:{row['id']}"
                )
                combo.addItem(display, row["id"])
        except Exception as e:
            _logger.warning(
                f"Failed to load display column '{display_column}' for table "
                f"'{fk_table}', falling back to ID display: {e}"
            )
            cursor = conn.execute(f"SELECT id FROM {fk_table} ORDER BY id")
            for row in cursor.fetchall():
                combo.addItem(f"ID:{row['id']}", row["id"])

        combo.blockSignals(False)

    def _quickAdd(self, fk_table: str, combo: QtWidgets.QComboBox):
        dialog = AddDialog(
            self._db_manager,
            parent=self,
            quick_mode=True,
            entity_type=fk_table,
        )
        dialog.setWindowTitle(_translate("AddDialog", f"Add {fk_table.capitalize()}"))
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self._loadForeignKeyData(combo, fk_table)

    def _onAccepted(self):
        if not self._selected_type:
            if not self._quick_mode:
                QtWidgets.QMessageBox.warning(
                    self,
                    _translate("AddDialog", "Warning"),
                    _translate("AddDialog", "Please select an entity type"),
                )
                return
            return
        if not self._form_widgets:
            self._buildForm()
        if not self._form_widgets:
            return

        fields = ENTITY_FIELDS.get(self._selected_type, [])

        # Build data dict from form
        data: dict = {}
        for field in fields:
            widget = self._form_widgets.get(field.name)
            if not widget:
                continue

            if field.field_type == "fk":
                value = widget.currentData()
            else:
                value = widget.text()

            if field.required:
                if field.field_type == "fk":
                    if value is None:
                        QtWidgets.QMessageBox.warning(
                            self,
                            _translate("AddDialog", "Warning"),
                            f"{field.label_key} is required",
                        )
                        return
                else:
                    if not value or not value.strip():
                        QtWidgets.QMessageBox.warning(
                            self,
                            _translate("AddDialog", "Warning"),
                            f"{field.label_key} is required",
                        )
                        return

            if value or not field.required:
                if isinstance(value, str):
                    data[field.name] = value.strip() if value else value
                else:
                    data[field.name] = value

        # Try to use Repository if available
        if self._user_db_service:
            repo_property = TABLE_TO_REPO_PROPERTY.get(self._selected_type)
            snapshot_class = TABLE_TO_SNAPSHOT_CLASS.get(self._selected_type)
            if repo_property and snapshot_class:
                repo = getattr(self._user_db_service, repo_property, None)
                if repo:
                    try:
                        snapshot = snapshot_class.fromRow(data)
                        repo.insert(snapshot)
                        self.accept()
                        return
                    except Exception as e:
                        QtWidgets.QMessageBox.critical(
                            self,
                            _translate("AddDialog", "Error"),
                            _translate("AddDialog", "Failed to add data:") + f" {e}",
                        )
                        return

        # Fallback to direct SQL
        conn = self._db_manager.connection
        columns = list(data.keys())
        values = list(data.values())

        try:
            placeholders = ", ".join(["?" for _ in columns])
            sql = f"INSERT INTO {self._selected_type} ({', '.join(columns)}) VALUES ({placeholders})"
            conn.execute(sql, values)
            conn.commit()
            self.accept()
        except Exception as e:
            conn.rollback()
            QtWidgets.QMessageBox.critical(
                self,
                _translate("AddDialog", "Error"),
                _translate("AddDialog", "Failed to add data:") + f" {e}",
            )
