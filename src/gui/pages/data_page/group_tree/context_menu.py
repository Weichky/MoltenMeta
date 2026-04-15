from PySide6 import QtWidgets
from PySide6.QtCore import QCoreApplication

from .model import NodeType, TreeNodeData


def _translate(context: str, text: str) -> str:
    return QCoreApplication.translate(context, text)


class ContextMenuFactory:
    def __init__(self, controller):
        self._controller = controller

    def createForNode(self, node: TreeNodeData | None) -> QtWidgets.QMenu | None:
        if node is None:
            return None

        menu = QtWidgets.QMenu()

        if node.node_type == NodeType.GROUP:
            menu.addAction(_translate("GroupTree", "Rename"), self._onRename)
            menu.addAction(_translate("GroupTree", "Delete"), self._onDelete)
        elif node.node_type == NodeType.UNGROUPED:
            return None
        elif node.node_type == NodeType.DATA:
            menu.addAction(
                _translate("GroupTree", "Add to New Group..."), self._onAddToNewGroup
            )
            if node.id is not None:
                menu.addAction(
                    _translate("GroupTree", "Remove from Group"),
                    self._onRemoveFromGroup,
                )

        return menu

    def _onRename(self) -> None:
        self._controller.triggerRename()

    def _onDelete(self) -> None:
        self._controller.triggerDelete()

    def _onAddToNewGroup(self) -> None:
        self._controller.triggerAddToNewGroup()

    def _onRemoveFromGroup(self) -> None:
        self._controller.triggerRemoveFromGroup()
