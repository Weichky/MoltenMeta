from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QObject


class GroupItem:
    UNGROUPED = "Ungrouped"
    ALL_DATA = "All Data"

    def __init__(
        self, name: str, group_id: int | None = None, is_category: bool = False
    ):
        self.name = name
        self.group_id = group_id
        self.is_category = is_category
        self.children: list[GroupItem] = []
        self.parent: GroupItem | None = None

    def appendChild(self, child: "GroupItem") -> None:
        child.parent = self
        self.children.append(child)

    def child(self, row: int) -> "GroupItem | None":
        if 0 <= row < len(self.children):
            return self.children[row]
        return None

    def childCount(self) -> int:
        return len(self.children)

    def row(self) -> int:
        if self.parent:
            return self.parent.children.index(self)
        return 0

    def columnCount(self) -> int:
        return 1

    def data(
        self, column: int, role: int = QtCore.Qt.ItemDataRole.DisplayRole
    ) -> str | None:
        if column == 0 and role == QtCore.Qt.ItemDataRole.DisplayRole:
            return self.name
        return None

    @staticmethod
    def ungroupedItem() -> "GroupItem":
        return GroupItem(GroupItem.UNGROUPED, group_id=None, is_category=True)

    @staticmethod
    def allDataItem() -> "GroupItem":
        return GroupItem(GroupItem.ALL_DATA, group_id=None, is_category=True)


class UiGroupTree(QObject):
    def setupUi(self, parent: QtWidgets.QWidget) -> None:
        if not parent.objectName():
            parent.setObjectName("groupTree")

        self.container = QtWidgets.QVBoxLayout(parent)
        self.container.setContentsMargins(0, 0, 0, 0)
        self.container.setSpacing(4)

        self._setupHeader(parent)
        self._setupTreeView(parent)

    def _setupHeader(self, parent: QtWidgets.QWidget) -> None:
        self.header_widget = QtWidgets.QWidget()
        self.header_layout = QtWidgets.QHBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(4)

        self.title_label = QtWidgets.QLabel()
        self.header_layout.addWidget(self.title_label)

        self.header_layout.addStretch()

        self.add_button = QtWidgets.QPushButton()
        self.add_button.setObjectName("addGroupButton")
        self.add_button.setFixedSize(24, 24)
        self.header_layout.addWidget(self.add_button)

        self.delete_button = QtWidgets.QPushButton()
        self.delete_button.setObjectName("deleteGroupButton")
        self.delete_button.setFixedSize(24, 24)
        self.delete_button.setEnabled(False)
        self.header_layout.addWidget(self.delete_button)

        self.container.addWidget(self.header_widget)

    def _setupTreeView(self, parent: QtWidgets.QWidget) -> None:
        self.tree_view = QtWidgets.QTreeView()
        self.tree_view.setObjectName("groupTreeView")
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setAnimated(True)
        self.tree_view.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        self.container.addWidget(self.tree_view, stretch=1)

    def retranslateUi(self) -> None:
        self.title_label.setText(self.tr("Groups"))
        self.add_button.setText("+")
        self.delete_button.setText("-")
