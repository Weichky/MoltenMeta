from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Signal
from PySide6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent

from application import AppContext
from .ui import UiGroupTree
from .model import NodeType, MIME_DATA_IDS
from .drag_drop import decodeDragData


class _GroupTreeView(QtWidgets.QTreeView):
    """Custom tree view with proper drag-drop event handling.

    We subclass QTreeView instead of assigning event handlers as instance attributes
    (e.g., self.dropEvent = handler) because Qt's event system requires proper
    method override for events to be processed correctly.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtWidgets.QTreeView.DragDrop)
        self.setDefaultDropAction(QtCore.Qt.DropAction.MoveAction)
        self.setSelectionMode(QtWidgets.QTreeView.SelectionMode.ExtendedSelection)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        mime = event.mimeData()
        if mime.hasFormat(MIME_DATA_IDS):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        mime = event.mimeData()
        if mime.hasFormat(MIME_DATA_IDS):
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        # Skip Qt's internal row-moving logic; we handle drops ourselves in _onDropEvent.
        # Without this, Qt tries to move rows internally which conflicts with our
        # loadGroups() refresh that clears and rebuilds the model, causing crashes.
        pass


class GroupTreeWidget(QtWidgets.QWidget):
    groupSelectionChanged = Signal(object)
    # PySide6 Signal: use `list` instead of `list[int]` due to type hint registration issues
    dataMoved = Signal(list, object)

    def __init__(self, context: AppContext, parent=None):
        super().__init__(parent=parent)
        self._context = context

        self.ui = UiGroupTree()
        self.ui.setupUi(self)

        self._tree_view = _GroupTreeView()
        self.ui.layout.insertWidget(0, self._tree_view)

        from .model import GroupTreeModel
        from .controller import GroupTreeController

        self.model = GroupTreeModel()
        self._tree_view.setModel(self.model)
        self.controller = GroupTreeController(self.model, self._tree_view, context)
        self.controller.selectionChanged.connect(self._onSelectionChanged)
        self.controller.dataMoved.connect(self.dataMoved)
        self.model.dataChanged.connect(self._onModelDataChanged)

        self._tree_view.setAcceptDrops(True)
        self._tree_view.setDragEnabled(True)
        self._tree_view.viewport().setAcceptDrops(True)
        self._tree_view.setDropIndicatorShown(True)
        self._tree_view.dropEvent = self._onDropEvent

    def _onDropEvent(self, event):
        index = self._tree_view.indexAt(event.position().toPoint())
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
        index = self._tree_view.currentIndex()
        node = self.model.getNodeAtIndex(index)
        if node and node.node_type in (NodeType.UNGROUPED, NodeType.GROUP):
            return node.id
        return None

    def retranslateUi(self) -> None:
        self.ui.retranslateUi()
