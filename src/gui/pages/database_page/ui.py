from PySide6 import QtWidgets
from PySide6.QtCore import QObject


class UiDatabasePage(QObject):
    DEFAULT_PAGE_SIZE = 1000
    DEFAULT_ROW_COUNT = 100

    def setupUi(self, databasePage: QtWidgets.QWidget):
        if not databasePage.objectName():
            databasePage.setObjectName("databasePage")

        self.root_layout = QtWidgets.QVBoxLayout(databasePage)
        self.root_layout.setContentsMargins(16, 16, 16, 16)
        self.root_layout.setSpacing(8)

        self._setupToolbar(databasePage)
        # self.root_layout.addStretch()
        self._setupTableView(databasePage)
        self.root_layout.addStretch()
        self._setupStatusBar(databasePage)

    def _setupToolbar(self, parent: QtWidgets.QWidget):
        self.toolbar = QtWidgets.QWidget()
        self.toolbar_layout = QtWidgets.QHBoxLayout(self.toolbar)
        self.toolbar_layout.setContentsMargins(0, 0, 0, 0)
        self.toolbar_layout.setSpacing(12)

        self.table_label = QtWidgets.QLabel()
        self.toolbar_layout.addWidget(self.table_label)

        self.table_combo = QtWidgets.QComboBox()
        self.table_combo.setObjectName("tableCombo")
        self.toolbar_layout.addWidget(self.table_combo)

        self.toolbar_layout.addStretch()

        self.save_button = QtWidgets.QPushButton()
        self.save_button.setEnabled(False)
        self.toolbar_layout.addWidget(self.save_button)

        self.cancel_button = QtWidgets.QPushButton()
        self.cancel_button.setEnabled(False)
        self.toolbar_layout.addWidget(self.cancel_button)

        self.root_layout.addWidget(self.toolbar)

    def _setupTableView(self, parent: QtWidgets.QWidget):
        self.table_view = QtWidgets.QTableView()
        self.table_view.setObjectName("databaseTableView")
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table_view.setSortingEnabled(True)

        self.root_layout.addWidget(self.table_view)

    def _setupStatusBar(self, parent: QtWidgets.QWidget):
        self.status_bar = QtWidgets.QWidget()
        self.status_layout = QtWidgets.QHBoxLayout(self.status_bar)
        self.status_layout.setContentsMargins(0, 0, 0, 0)
        self.status_layout.setSpacing(8)

        self.row_count_label = QtWidgets.QLabel()
        self.status_layout.addWidget(self.row_count_label)

        self.status_layout.addStretch()

        self.loading_label = QtWidgets.QLabel()
        self.loading_label.setObjectName("loadingLabel")
        self.loading_label.setVisible(False)
        self.status_layout.addWidget(self.loading_label)

        self.root_layout.addWidget(self.status_bar)

    def retranslateUi(self):
        self.table_label.setText(self.tr("Table:"))
        self.save_button.setText(self.tr("Save"))
        self.cancel_button.setText(self.tr("Cancel"))
        self.loading_label.setText(self.tr("Loading..."))
