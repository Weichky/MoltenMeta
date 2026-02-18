# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtCore import Qt, QEvent
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, 
)
import PySide6QtAds as QtAds

from application import AppContext

from gui.ui_main_window import UiMainWindow
from gui.sidebar import SidebarWidget
from gui.menubar import MenubarWidget
from gui.pages.workspace import Workspace

class MainWindow(QMainWindow):
    def __init__(self, context: AppContext, parent=None):

        super().__init__(parent)

        self.log = context.log(__name__)

        self.ui = UiMainWindow()
        self.ui.setupUi(self)
            
        # Init CDockManager Configuration Flags
        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.OpaqueSplitterResize, True)

        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.DockAreaHasCloseButton, False)
        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.AllTabsHaveCloseButton, False)
        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.DockAreaHasUndockButton, False)
        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.DockAreaHasTabsMenuButton, False)
        
        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.FocusHighlighting, False)

        QtAds.CDockManager.setAutoHideConfigFlag(QtAds.CDockManager.AutoHideFeatureEnabled, True)
        QtAds.CDockManager.setAutoHideConfigFlag(QtAds.CDockManager.DockAreaHasAutoHideButton, True)

        # SITE: "You must set the configuration flags before creating the dock manager instance
        # otherwise the manager will not be created correctly and will crash upon being created.
        # That means, setting the configurations flags is the first thing you must do,
        # if you use the library."

        # Set menubar
        self.menubar = MenubarWidget(self)
        self.setMenuBar(self.menubar)

        # Set sidebar
        self.sidebar = SidebarWidget(self)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.sidebar)

        # Set workspace
        self.workspace = Workspace(self)
        self.setCentralWidget(self.workspace)

        # Connect signals
        self.sidebar.ui.homeButton.clicked.connect(
            self.workspace.controller.showHome
        )
        self.sidebar.ui.settingsButton.clicked.connect(
            self.workspace.controller.showSettings
        )
        
        # Connect menubar settings action
        self.menubar.ui.action_settings.triggered.connect(
            self.workspace.controller.showSettings
        )
        
        # i18n
        context.i18n.language_changed.connect(self.retranslateUi)

        # Automatically show home page on startup
        self.workspace.controller.showHome()
    def changeEvent(self, event):
        if event.type() == QEvent.Type.ThemeChange:
            # Update application palette when system theme changes
            QApplication.setPalette(QApplication.style().standardPalette())
            # Force update all child widgets
            self.updateTheme()
        super().changeEvent(event)
    
    def updateTheme(self):
        # Recursively update all child widgets
        self.setStyleSheet("")
        self.updateStylesRecursive(self)
    
    def updateStylesRecursive(self, widget):
        widget.setStyle(widget.style())
        for child in widget.children():
            if isinstance(child, QWidget):
                self.updateStylesRecursive(child)

    def retranslateUi(self):
        self.ui.retranslateUi(self)