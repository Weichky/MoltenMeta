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
    QLayout
)

class UiSidebar(QObject):
    def setupUi(self, dock: QDockWidget):
        # Set dock widget properties
        if not dock.objectName():
            dock.setObjectName("sidebar")
        
        # Set sidebar resizable, but not allowed to dock at top or bottom
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | 
                        QDockWidget.DockWidgetFeature.DockWidgetFloatable |
                        QDockWidget.DockWidgetFeature.DockWidgetClosable)

        dock.DockWidgetClosable = False

        dock.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        dock.setFloating(False)
        dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetFloatable|QDockWidget.DockWidgetFeature.DockWidgetMovable)

        # Create content widget and layout
        self.contents = QWidget(dock)
        self.contents.setObjectName("dockWidgetContents")
        
        self.verticalLayout = QVBoxLayout(self.contents)
        self.verticalLayout.setObjectName("verticalLayout")
        
        # Create sidebar layout
        self.sidebarLayout = QVBoxLayout()
        self.sidebarLayout.setSpacing(0)
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
        sizePolicy.setHeightForWidth(self.settingsButton.sizePolicy().hasHeightForWidth())
        self.settingsButton.setSizePolicy(sizePolicy)
        
        self.sidebarLayout.addWidget(self.settingsButton)
        
        # Add vertical spacer
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.sidebarLayout.addItem(self.verticalSpacer)
        
        self.sidebarLayout.setStretch(0, 1)
        self.sidebarLayout.setStretch(1, 1)
        self.sidebarLayout.setStretch(2, 1)
        
        self.verticalLayout.addLayout(self.sidebarLayout)
        dock.setWidget(self.contents)

    def retranslateUi(self, dock: QDockWidget):
        # Set button texts
        self.homeButton.setText(self.tr("Home"))
        self.settingsButton.setText(self.tr("Settings"))
        
    def adjustSidebarSize(self, sidebar):
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