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
        # 设置dock widget属性
        if not dock.objectName():
            dock.setObjectName(u"sidebar")
        
        dock.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        dock.setFloating(False)
        dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetFloatable|QDockWidget.DockWidgetFeature.DockWidgetMovable)

        # 创建内容部件和布局
        self.contents = QWidget(dock)
        self.contents.setObjectName(u"dockWidgetContents")
        
        self.verticalLayout = QVBoxLayout(self.contents)
        self.verticalLayout.setObjectName(u"verticalLayout")
        
        # 创建侧边栏布局
        self.sidebarLayout = QVBoxLayout()
        self.sidebarLayout.setSpacing(0)
        self.sidebarLayout.setObjectName(u"sidebarLayout")
        self.sidebarLayout.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)
        
        # 创建主页按钮
        self.homeButton = QPushButton(self.contents)
        self.homeButton.setObjectName(u"homeButton")
        
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.homeButton.sizePolicy().hasHeightForWidth())
        self.homeButton.setSizePolicy(sizePolicy)
        
        self.sidebarLayout.addWidget(self.homeButton)
        
        # 创建设置按钮
        self.settingsButton = QPushButton(self.contents)
        self.settingsButton.setObjectName(u"settingsButton")
        
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.settingsButton.sizePolicy().hasHeightForWidth())
        self.settingsButton.setSizePolicy(sizePolicy)
        
        self.sidebarLayout.addWidget(self.settingsButton)
        
        # 添加垂直间隔器
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.sidebarLayout.addItem(self.verticalSpacer)
        
        self.sidebarLayout.setStretch(0, 1)
        self.sidebarLayout.setStretch(1, 1)
        self.sidebarLayout.setStretch(2, 1)
        
        self.verticalLayout.addLayout(self.sidebarLayout)
        dock.setWidget(self.contents)

    def retranslateUi(self, dock: QDockWidget):
        # 设置按钮文本
        self.homeButton.setText(self.tr(u"Home"))
        self.settingsButton.setText(self.tr(u"Settings"))