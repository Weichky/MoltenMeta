from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Signal
from PySide6.QtGui import QDragEnterEvent, QDragMoveEvent

from application import AppContext
from .ui import UiGroupTree
from .model import NodeType, MIME_DATA_IDS
from .drag_drop import decodeDragData


class GroupTreeWidget(QtWidgets.QWidget):
    groupSelectionChanged = Signal(object)
    dataMoved = Signal(list, object)

    def __init__(self, context: AppContext, parent=None):
        super().__init__(parent=parent)
        self._context = context
        self._drag_target_item: QtCore.QModelIndex | None = None

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

        self.ui.tree_view.setAcceptDrops(True)
        self.ui.tree_view.dropEvent = self._onDropEvent
        self.ui.tree_view.dragEnterEvent = self._onDragEnterEvent
        self.ui.tree_view.dragMoveEvent = self._onDragMoveEvent
        self.ui.tree_view.dragLeaveEvent = self._onDragLeaveEvent

    def _onDropEvent(self, event):
        self._clearDragHighlight()
        index = self.ui.tree_view.indexAt(event.position().toPoint())
        if not index.isValid():
            event.ignore()
            return

        target_node = self.model.getNodeAtIndex(index)
        if target_node is None or target_node.node_type == NodeType.DATA:
            event.ignore()
            return

        mime = event.mimeData()
        if not mime.hasFormat(MIME_DATA_IDS):
            event.ignore()
            return

        _, _, data_ids = decodeDragData(mime)
        if not data_ids:
            event.ignore()
            return

        self.controller.handleDrop(data_ids, target_node)
        event.accept()

    def _onDragEnterEvent(self, event: QDragEnterEvent) -> None:
        mime = event.mimeData()
        if not mime.hasFormat(MIME_DATA_IDS):
            event.ignore()
            return

        index = self.ui.tree_view.indexAt(event.position().toPoint())
        if not index.isValid():
            event.ignore()
            return

        target_node = self.model.getNodeAtIndex(index)
        if target_node is None or target_node.node_type == NodeType.DATA:
            event.ignore()
            return

        self._drag_target_item = index
        self._highlightDropTarget(index)
        event.accept()

    def _onDragMoveEvent(self, event: QDragMoveEvent) -> None:
        mime = event.mimeData()
        if not mime.hasFormat(MIME_DATA_IDS):
            event.ignore()
            return

        index = self.ui.tree_view.indexAt(event.position().toPoint())
        if not index.isValid():
            event.ignore()
            return

        target_node = self.model.getNodeAtIndex(index)
        if target_node is None or target_node.node_type == NodeType.DATA:
            if self._drag_target_item is not None:
                self._clearDragHighlight()
                self._drag_target_item = None
            event.ignore()
            return

        if self._drag_target_item != index:
            self._clearDragHighlight()
            self._drag_target_item = index
            self._highlightDropTarget(index)

        event.accept()

    def _onDragLeaveEvent(self, event) -> None:
        self._clearDragHighlight()
        self._drag_target_item = None

    def _highlightDropTarget(self, index: QtCore.QModelIndex) -> None:
        self.ui.tree_view.setExpanded(index, True)

    def _clearDragHighlight(self) -> None:
        if self._drag_target_item is not None:
            self.ui.tree_view.setExpanded(self._drag_target_item, True)

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
