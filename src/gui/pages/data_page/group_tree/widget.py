from PySide6 import QtWidgets
from PySide6.QtCore import Signal

from application import AppContext
from .ui import UiGroupTree


class GroupTreeWidget(QtWidgets.QWidget):
    groupSelectionChanged = Signal(object)

    def __init__(self, context: AppContext, parent=None):
        super().__init__(parent=parent)
        self._context = context

        self.ui = UiGroupTree()
        self.ui.setupUi(self)

        from .model import GroupTreeModel
        from .controller import GroupTreeController

        self.model = GroupTreeModel()
        self.ui.tree_view.setModel(self.model)
        self.controller = GroupTreeController(self.model, self.ui, context)
        self.controller.selectionChanged.connect(self._onSelectionChanged)

        self.ui.tree_view.expandAll()

    def _onSelectionChanged(self, group_id) -> None:
        self.groupSelectionChanged.emit(group_id)

    def loadGroups(self, groups: list[tuple[int, str]]) -> None:
        self.controller.loadGroups(groups)

    def getSelectedGroupId(self) -> int | None:
        index = self.ui.tree_view.currentIndex()
        return self.model.getSelectedGroupId(index)

    def retranslateUi(self) -> None:
        self.ui.retranslateUi()
