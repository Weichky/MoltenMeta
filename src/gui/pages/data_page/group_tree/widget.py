from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Signal

from application import AppContext
from .ui import UiGroupTree
from .model import NodeType
from .drag_drop import decodeDragData


class GroupTreeWidget(QtWidgets.QWidget):
    groupSelectionChanged = Signal(object)
    dataMoved = Signal(list, object)

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
        self.controller.dataMoved.connect(self.dataMoved)
        self.model.dataChanged.connect(self._onModelDataChanged)

        self.ui.tree_view.dropEvent = self._onDropEvent

    def _onDropEvent(self, event):
        index = self.ui.tree_view.indexAt(event.position().toPoint())
        if not index.isValid():
            event.ignore()
            return

        target_node = self.model.getNodeAtIndex(index)
        if target_node is None or target_node.node_type == NodeType.DATA:
            event.ignore()
            return

        mime = event.mimeData()
        if not mime.hasFormat("application/x-moltenmeta-data-ids"):
            event.ignore()
            return

        _, _, data_ids = decodeDragData(mime)
        if not data_ids:
            event.ignore()
            return

        self.controller.handleDrop(data_ids, target_node)
        event.accept()

    def _onSelectionChanged(self, group_id) -> None:
        self.groupSelectionChanged.emit(group_id)

    def _onNodeExpanded(self, index: QtCore.QModelIndex) -> None:
        node = self.model.getNodeAtIndex(index)
        if node and node.node_type in (NodeType.UNGROUPED, NodeType.GROUP):
            if not self.controller.isGroupLoaded(node.id):
                self.controller.fetchDataForNode(node.id)

    def _onModelDataChanged(
        self, topLeft: QtCore.QModelIndex, bottomRight: QtCore.QModelIndex, roles
    ):
        if QtCore.Qt.ItemDataRole.EditRole in roles:
            node = self.model.getNodeAtIndex(topLeft)
            if node and node.node_type == NodeType.GROUP and node.id is not None:
                self.controller.renameGroup(node.id, node.name)

    def loadGroups(self, groups: list | None = None) -> None:
        self.controller.loadGroups()

    def getSelectedGroupId(self) -> int | None:
        index = self.ui.tree_view.currentIndex()
        node = self.model.getNodeAtIndex(index)
        if node and node.node_type in (NodeType.UNGROUPED, NodeType.GROUP):
            return node.id
        return None

    def retranslateUi(self) -> None:
        self.ui.retranslateUi()
