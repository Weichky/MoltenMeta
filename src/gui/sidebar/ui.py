from PySide6.QtCore import (
    Qt,
    QObject,
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


class UiSidebar(QObject):
    COLLAPSED_WIDTH = 64
    EXPANDED_WIDTH = 200
    BUTTON_HEIGHT = 48
    ICON_SIZE = 24

    def setupUi(self, dock: QDockWidget):
        if not dock.objectName():
            dock.setObjectName("sidebar")

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

        self.contents = QWidget(dock)
        self.contents.setObjectName("dockWidgetContents")

        self.verticalLayout = QVBoxLayout(self.contents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 16, 0, 16)

        self.sidebarLayout = QVBoxLayout()
        self.sidebarLayout.setSpacing(0)
        self.sidebarLayout.setObjectName("sidebarLayout")
        self.sidebarLayout.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)

        self.homeButton = QPushButton(self.contents)
        self.homeButton.setObjectName("sidebarButton")
        self.homeButton.setCheckable(True)

        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.homeButton.sizePolicy().hasHeightForWidth())
        self.homeButton.setSizePolicy(sizePolicy)

        self.sidebarLayout.addWidget(self.homeButton)

        self.simulationButton = QPushButton(self.contents)
        self.simulationButton.setObjectName("sidebarButton")
        self.simulationButton.setCheckable(True)

        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.simulationButton.sizePolicy().hasHeightForWidth())
        self.simulationButton.setSizePolicy(sizePolicy)

        self.sidebarLayout.addWidget(self.simulationButton)

        self.dataButton = QPushButton(self.contents)
        self.dataButton.setObjectName("sidebarButton")
        self.dataButton.setCheckable(True)

        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dataButton.sizePolicy().hasHeightForWidth())
        self.dataButton.setSizePolicy(sizePolicy)

        self.sidebarLayout.addWidget(self.dataButton)

        self.settingsButton = QPushButton(self.contents)
        self.settingsButton.setObjectName("sidebarButton")
        self.settingsButton.setCheckable(True)

        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.settingsButton.sizePolicy().hasHeightForWidth()
        )
        self.settingsButton.setSizePolicy(sizePolicy)

        self.sidebarLayout.addWidget(self.settingsButton)

        self.verticalSpacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        self.sidebarLayout.addItem(self.verticalSpacer)

        self.toggleButton = QPushButton(self.contents)
        self.toggleButton.setObjectName("toggleButton")
        self.toggleButton.setCheckable(True)

        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.toggleButton.setSizePolicy(sizePolicy)

        self.sidebarLayout.addWidget(self.toggleButton)

        self.sidebarLayout.setStretch(0, 0)
        self.sidebarLayout.setStretch(1, 0)
        self.sidebarLayout.setStretch(2, 0)
        self.sidebarLayout.setStretch(3, 0)
        self.sidebarLayout.setStretch(4, 1)
        self.sidebarLayout.setStretch(5, 0)

        self.verticalLayout.addLayout(self.sidebarLayout)
        dock.setWidget(self.contents)

    def retranslateUi(self, dock: QDockWidget):
        self.homeButton.setText(self.tr("Home"))
        self.simulationButton.setText(self.tr("Simulation"))
        self.dataButton.setText(self.tr("Data"))
        self.settingsButton.setText(self.tr("Settings"))

    def adjustSidebarSize(self, sidebar, is_collapsed: bool = False):
        if is_collapsed:
            sidebar.setMinimumWidth(self.COLLAPSED_WIDTH)
            sidebar.setMaximumWidth(self.COLLAPSED_WIDTH)
            return

        sidebar.setMinimumWidth(self.EXPANDED_WIDTH)
        sidebar.setMaximumWidth(self.EXPANDED_WIDTH)
