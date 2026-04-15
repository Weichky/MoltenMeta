from PySide6 import QtWidgets
from PySide6.QtCore import Signal


from application import AppContext

from .ui import UiDataPage
from .group_tree.placeholder import UiPlaceholderTree, PlaceholderTreeModel


class PlaceholderTreeWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.ui = UiPlaceholderTree()
        self.ui.setupUi(self)

        self.model = PlaceholderTreeModel()
        self.ui.tree_view.setModel(self.model)


class DataPage(QtWidgets.QWidget):
    tableChanged = Signal(str)

    def __init__(self, context: AppContext):
        super().__init__(parent=None)
        self.i18n_service = context.i18n

        self.ui = UiDataPage()
        self.ui.setupUi(self)
        self.ui.retranslateUi()

        from .controller import DataController
        from .group_tree import GroupTreeWidget

        self.group_tree = GroupTreeWidget(context, self.ui.tree_widget)
        self.ui.tree_layout.addWidget(self.group_tree)

        self.placeholder_tree = PlaceholderTreeWidget(self.ui.placeholder_widget)
        self.ui.placeholder_layout.addWidget(self.placeholder_tree)

        self.controller = DataController(self.ui, context, self.group_tree)
        self.controller.connectSignals()

        self.i18n_service.language_changed.connect(self.retranslateUi)

    def retranslateUi(self):
        self.ui.retranslateUi()
