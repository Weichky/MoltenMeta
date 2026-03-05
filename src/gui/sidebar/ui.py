from PySide6.QtCore import (
    Qt,
    QObject,
    QSize,
)
from PySide6.QtWidgets import (
    QDockWidget,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QLayout,
)
from PySide6.QtGui import QFont


class UiSidebar(QObject):
    COLLAPSED_WIDTH = 75
    EXPANDED_WIDTH = 0  # 0 means dynamic
    BUTTON_HEIGHT = 48
    ICON_SIZE = 32

    def setupUi(self, dock: QDockWidget):
        # Set dock widget properties
        if not dock.objectName():
            dock.setObjectName("sidebar")

        # Set sidebar resizable, but not allowed to dock at top or bottom
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
        )

        dock.DockWidgetClosable = False

        dock.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        dock.setFloating(False)
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
        )

        # Create content widget and layout
        self.contents = QWidget(dock)
        self.contents.setObjectName("dockWidgetContents")

        self.verticalLayout = QVBoxLayout(self.contents)
        self.verticalLayout.setObjectName("verticalLayout")

        # Create sidebar layout
        self.sidebarLayout = QVBoxLayout()
        self.sidebarLayout.setSpacing(2)
        self.sidebarLayout.setObjectName("sidebarLayout")
        self.sidebarLayout.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)

        # Create home button
        self.homeButton = QPushButton(self.contents)
        self.homeButton.setObjectName("homeButton")

        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.homeButton.sizePolicy().hasHeightForWidth())
        self.homeButton.setSizePolicy(sizePolicy)

        self.sidebarLayout.addWidget(self.homeButton)

        # Create settings button
        self.settingsButton = QPushButton(self.contents)
        self.settingsButton.setObjectName("settingsButton")

        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.settingsButton.sizePolicy().hasHeightForWidth()
        )
        self.settingsButton.setSizePolicy(sizePolicy)

        self.sidebarLayout.addWidget(self.settingsButton)

        # Create database button
        self.databaseButton = QPushButton(self.contents)
        self.databaseButton.setObjectName("databaseButton")

        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.databaseButton.sizePolicy().hasHeightForWidth()
        )
        self.databaseButton.setSizePolicy(sizePolicy)

        self.sidebarLayout.addWidget(self.databaseButton)

        # Add vertical spacer
        self.verticalSpacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        self.sidebarLayout.addItem(self.verticalSpacer)

        # Create toggle button
        self.toggleButton = QPushButton(self.contents)
        self.toggleButton.setObjectName("toggleButton")
        self.toggleButton.setCheckable(True)

        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.toggleButton.setSizePolicy(sizePolicy)

        self.sidebarLayout.addWidget(self.toggleButton)

        self.sidebarLayout.setStretch(0, 1)
        self.sidebarLayout.setStretch(1, 1)
        self.sidebarLayout.setStretch(2, 1)
        self.sidebarLayout.setStretch(3, 1)
        self.sidebarLayout.setStretch(4, 1)
        self.sidebarLayout.setStretch(5, 0)

        self.verticalLayout.addLayout(self.sidebarLayout)
        dock.setWidget(self.contents)

        self._applyButtonStyle()

    def _applyButtonStyle(self):
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)

        buttons = [
            self.homeButton,
            self.settingsButton,
            self.databaseButton,
            self.toggleButton,
        ]
        for btn in buttons:
            btn.setFont(font)
            btn.setMinimumHeight(self.BUTTON_HEIGHT)
            btn.setIconSize(QSize(self.ICON_SIZE, self.ICON_SIZE))
            btn.setStyleSheet("text-align: left; padding-left: 12px;")

    def retranslateUi(self, dock: QDockWidget):
        # Set button texts
        self.homeButton.setText(self.tr("Home"))
        self.settingsButton.setText(self.tr("Settings"))
        self.databaseButton.setText(self.tr("Database"))

    def adjustSidebarSize(self, sidebar, is_collapsed: bool = False):
        if is_collapsed:
            sidebar.setMinimumWidth(self.COLLAPSED_WIDTH)
            sidebar.setMaximumWidth(self.COLLAPSED_WIDTH)
            return

        # Get parent window dimensions
        parent_width = sidebar.parent().width()

        # Set navigation panel minimum and maximum width based on parent window width
        # Minimum width is 1/12 of parent window width, but no less than 100 pixels
        min_width = max(int(parent_width / 12), 100)
        # Maximum width is 1/4 of parent window width, but no more than 300 pixels
        max_width = min(int(parent_width / 4), 300)

        # Apply size constraints to sidebar
        sidebar.setMinimumWidth(min_width)
        sidebar.setMaximumWidth(max_width)
