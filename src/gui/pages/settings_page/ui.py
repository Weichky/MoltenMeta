from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QObject

from core.log import getLogLevelMap
from catalog import getSupportedLanguagesNameMap

from domain.settings import Settings

class UiSettingsPage(QObject):
    def __init__(self, settings: Settings):
        super().__init__()
        self._settings = settings

    def setupUi(self, settingsPage: QtWidgets.QWidget):
        if not settingsPage.objectName():
            settingsPage.setObjectName("settingsPage")

        self.root_layout = QtWidgets.QHBoxLayout(settingsPage)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        # Create resizable splitter
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("settingsSplitter")
        self.splitter.setChildrenCollapsible(False)  # Prevent child widgets from being completely collapsed
        
        # ===== Left Navigation Panel =====
        self.nav_panel = QtWidgets.QWidget()
        self.nav_panel.setObjectName("settingsNavPanel")
        # Set size constraints using relative units
        self._setupNavPanelConstraints(settingsPage)
        
        self.nav_layout = QtWidgets.QVBoxLayout(self.nav_panel)
        self.nav_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area for sidebar buttons
        self.nav_scroll = QtWidgets.QScrollArea()
        self.nav_scroll.setWidgetResizable(True)
        self.nav_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.nav_scroll.setObjectName("navScrollArea")
        
        # Create container widget with buttons
        self.nav_buttons_widget = QtWidgets.QWidget()
        self.nav_buttons_layout = QtWidgets.QVBoxLayout(self.nav_buttons_widget)
        self.nav_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.nav_buttons_layout.setSpacing(5)  # Add spacing between navigation buttons
        self.nav_buttons_layout.setAlignment(QtCore.Qt.AlignTop)  # Align to top
        
        # Add navigation items
        self.general_button = QtWidgets.QPushButton()
        self.log_button = QtWidgets.QPushButton()

        self.general_button.setCheckable(True)
        self.log_button.setCheckable(True)
        self.general_button.setChecked(True)
        self.log_button.setChecked(False)

        self.nav_buttons_layout.addWidget(self.general_button)
        self.nav_buttons_layout.addWidget(self.log_button)
        
        # Set button container as scroll area widget
        self.nav_scroll.setWidget(self.nav_buttons_widget)
        
        # Add scroll area to navigation panel layout
        self.nav_layout.addWidget(self.nav_scroll)
        
        # ===== Middle Main Content Area =====
        self.content_area = QtWidgets.QStackedWidget()
        self.content_area.setObjectName("settingsContentArea")
        
        # Create general settings page
        self.general_page = self._createGeneralPage()
        self.content_area.addWidget(self.general_page)
        
        # Create log settings page
        self.log_page = self._createLogPage()
        self.content_area.addWidget(self.log_page)

        # Add to splitter
        self.splitter.addWidget(self.nav_panel)
        self.splitter.addWidget(self.content_area)
        
        # Set initial size ratio (relative values)
        self._setupSplitterSizes(settingsPage)
        
        # Add splitter to main layout
        self.root_layout.addWidget(self.splitter)
        
        # Connect window resize signal
        settingsPage.installEventFilter(self._createResizeEventFilter(settingsPage))
        
    def _setupNavPanelConstraints(self, parent):
        # Get parent window dimensions
        parent_width = parent.width()
        
        # Set navigation panel min/max width based on parent window width
        # Minimum width is 1/12 of parent window width, but no less than 100 pixels
        min_width = max(int(parent_width / 12), 100)
        # Maximum width is 1/4 of parent window width, but no more than 300 pixels
        max_width = min(int(parent_width / 4), 300)
        
        self.nav_panel.setMinimumWidth(min_width)
        self.nav_panel.setMaximumWidth(max_width)
        
    def _setupSplitterSizes(self, parent):
        # Get parent window dimensions
        parent_width = parent.width()
        
        # Set initial sizes based on parent window width
        nav_width = max(int(parent_width / 8), 150)
        content_width = parent_width - nav_width
        
        self.splitter.setSizes([nav_width, content_width])
        
    def _createResizeEventFilter(self, parent):
        ui_self = self
        
        class ResizeEventFilter(QtCore.QObject):
            def eventFilter(self, obj, event):
                if event.type() == QtCore.QEvent.Resize:
                    # Reset navigation panel constraints when window is resized
                    ui_self._setupNavPanelConstraints(parent)
                    ui_self._setupSplitterSizes(parent)
                return False
                
        return ResizeEventFilter()
        
    def _createGeneralPage(self) -> QtWidgets.QWidget:
        page = QtWidgets.QWidget()
        page.setObjectName("generalPage")
        page_layout = QtWidgets.QVBoxLayout(page)
        page_layout.setSpacing(10)
        page_layout.setContentsMargins(10, 10, 10, 10)
        
        # Language settings
        lang_group = QtWidgets.QGroupBox()
        lang_group.setObjectName("languageGroup")
        lang_layout = QtWidgets.QVBoxLayout(lang_group)
        
        self.lang_label = QtWidgets.QLabel()
        lang_layout.addWidget(self.lang_label)
        
        self.lang_combo = QtWidgets.QComboBox()
        self.lang_combo.setObjectName("languageCombo")

        lang_layout.addWidget(self.lang_combo)
        
        lang_layout.addStretch()
        page_layout.addWidget(lang_group)

        for code, name in getSupportedLanguagesNameMap().items():
            self.lang_combo.addItem(name, code)

        language = self._settings.language

        self.lang_combo.setCurrentIndex(self.lang_combo.findData(language))

        page_layout.addStretch()
        
        return page
        
    def _createLogPage(self) -> QtWidgets.QWidget:
        page = QtWidgets.QWidget()
        page.setObjectName("loggingPage")
        page_layout = QtWidgets.QVBoxLayout(page)
        page_layout.setSpacing(10)
        page_layout.setContentsMargins(10, 10, 10, 10)

        log_level_group = QtWidgets.QGroupBox()
        log_level_group.setObjectName("logLevelGroup")
        log_level_layout = QtWidgets.QVBoxLayout(log_level_group)

        self.log_level_label = QtWidgets.QLabel()
        log_level_layout.addWidget(self.log_level_label)

        self.log_level_combo = QtWidgets.QComboBox()
        self.log_level_combo.setObjectName("logLevelCombo")

        log_level_layout.addWidget(self.log_level_combo)

        log_level_layout.addStretch()
        page_layout.addWidget(log_level_group)

        for level in getLogLevelMap().keys():
            self.log_level_combo.addItem(self.tr(level), level)

        log_level = self._settings.log_level
        self.log_level_combo.setCurrentIndex(self.log_level_combo.findData(log_level))

        page_layout.addStretch()

        return page


    def retranslateUi(self):
        # Navigation buttons
        self.general_button.setText(self.tr("General"))
        self.log_button.setText(self.tr("Log"))
        
        # General settings page
        self.lang_label.setText(self.tr("Language:"))
        
        # Log settings page
        self.log_level_label.setText(self.tr("Log level:"))

        # Group box titles
        for i in range(self.content_area.count()):
            widget = self.content_area.widget(i)
            if widget.objectName() == "generalPage":
                group = widget.findChild(QtWidgets.QGroupBox, "languageGroup")
                if group:
                    group.setTitle(self.tr("Language Settings"))
            if widget.objectName() == "loggingPage":
                group = widget.findChild(QtWidgets.QGroupBox, "logLevelGroup")
                if group:
                    group.setTitle(self.tr("Logging Settings"))