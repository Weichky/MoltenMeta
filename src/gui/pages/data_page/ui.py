from PySide6 import QtWidgets
from PySide6.QtCore import QObject


class UiDataPage(QObject):
    DEFAULT_PAGE_SIZE = 1000
    DEFAULT_ROW_COUNT = 100

    def setupUi(self, dataPage: QtWidgets.QWidget):
        if not dataPage.objectName():
            dataPage.setObjectName("dataPage")

        self.root_layout = QtWidgets.QVBoxLayout(dataPage)
        self.root_layout.setContentsMargins(16, 16, 16, 16)
        self.root_layout.setSpacing(8)

        self._setupToolbar(dataPage)
        self._setupFilterBar(dataPage)
        self.root_layout.addStretch()
        self._setupTableView(dataPage)
        self.root_layout.addStretch()
        self._setupStatusBar(dataPage)

    def _setupToolbar(self, parent: QtWidgets.QWidget):
        self.toolbar = QtWidgets.QWidget()
        self.toolbar_layout = QtWidgets.QHBoxLayout(self.toolbar)
        self.toolbar_layout.setContentsMargins(0, 0, 0, 0)
        self.toolbar_layout.setSpacing(12)

        self.add_button = QtWidgets.QPushButton()
        self.toolbar_layout.addWidget(self.add_button)

        self.delete_button = QtWidgets.QPushButton()
        self.toolbar_layout.addWidget(self.delete_button)

        self.refresh_button = QtWidgets.QPushButton()
        self.toolbar_layout.addWidget(self.refresh_button)

        self.toolbar_layout.addStretch()

        self.save_button = QtWidgets.QPushButton()
        self.save_button.setEnabled(False)
        self.toolbar_layout.addWidget(self.save_button)

        self.cancel_button = QtWidgets.QPushButton()
        self.cancel_button.setEnabled(False)
        self.toolbar_layout.addWidget(self.cancel_button)

        self.import_button = QtWidgets.QPushButton()
        self.toolbar_layout.addWidget(self.import_button)

        self.export_button = QtWidgets.QPushButton()
        self.toolbar_layout.addWidget(self.export_button)

        self.root_layout.addWidget(self.toolbar)

    def _setupFilterBar(self, parent: QtWidgets.QWidget):
        self.filter_bar = QtWidgets.QWidget()
        self.filter_layout = QtWidgets.QHBoxLayout(self.filter_bar)
        self.filter_layout.setContentsMargins(0, 0, 0, 0)
        self.filter_layout.setSpacing(12)

        self.table_label = QtWidgets.QLabel()
        self.filter_layout.addWidget(self.table_label)

        self.table_combo = QtWidgets.QComboBox()
        self.table_combo.setObjectName("tableCombo")
        self.filter_layout.addWidget(self.table_combo)

        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText(self.tr("Search..."))
        self.filter_layout.addWidget(self.search_input)

        self.filter_button = QtWidgets.QPushButton()
        self.filter_layout.addWidget(self.filter_button)

        self.filter_layout.addStretch()

        self.root_layout.addWidget(self.filter_bar)

    def _setupTableView(self, parent: QtWidgets.QWidget):
        self.table_view = QtWidgets.QTableView()
        self.table_view.setObjectName("dataTableView")
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table_view.setSortingEnabled(True)
        self.table_view.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )

        self.root_layout.addWidget(self.table_view, stretch=1)

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
        self.add_button.setText(self.tr("Add"))
        self.delete_button.setText(self.tr("Delete"))
        self.refresh_button.setText(self.tr("Refresh"))
        self.import_button.setText(self.tr("Import"))
        self.export_button.setText(self.tr("Export"))
        self.table_label.setText(self.tr("Table:"))
        self.filter_button.setText(self.tr("Filter"))
        self.save_button.setText(self.tr("Save"))
        self.cancel_button.setText(self.tr("Cancel"))
        self.loading_label.setText(self.tr("Loading..."))
