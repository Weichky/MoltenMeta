from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QObject

class UiSettingsPage(QObject):
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
        self._setup_nav_panel_constraints(settingsPage)
        
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
        self.nav_buttons_layout.setAlignment(QtCore.Qt.AlignTop)  # Align to top
        
        # Add navigation items
        self.general_button = QtWidgets.QPushButton()
        self.general_button.setCheckable(True)
        self.general_button.setChecked(True)
        self.nav_buttons_layout.addWidget(self.general_button)
        
        # Set button container as scroll area widget
        self.nav_scroll.setWidget(self.nav_buttons_widget)
        
        # Add scroll area to navigation panel layout
        self.nav_layout.addWidget(self.nav_scroll)
        
        # ===== Middle Main Content Area =====
        self.content_area = QtWidgets.QStackedWidget()
        self.content_area.setObjectName("settingsContentArea")
        
        # Create general settings page
        self.general_page = self._create_general_page()
        self.content_area.addWidget(self.general_page)
        
        # Add to splitter
        self.splitter.addWidget(self.nav_panel)
        self.splitter.addWidget(self.content_area)
        
        # Set initial size ratio (relative values)
        self._setup_splitter_sizes(settingsPage)
        
        # Add splitter to main layout
        self.root_layout.addWidget(self.splitter)
        
        # Connect window resize signal
        settingsPage.installEventFilter(self._create_resize_event_filter(settingsPage))
        
    def _setup_nav_panel_constraints(self, parent):
        """Set navigation panel size constraints based on parent window size."""
        # Get parent window dimensions
        parent_width = parent.width()
        
        # Set navigation panel min/max width based on parent window width
        # Minimum width is 1/12 of parent window width, but no less than 100 pixels
        min_width = max(int(parent_width / 12), 100)
        # Maximum width is 1/4 of parent window width, but no more than 300 pixels
        max_width = min(int(parent_width / 4), 300)
        
        self.nav_panel.setMinimumWidth(min_width)
        self.nav_panel.setMaximumWidth(max_width)
        
    def _setup_splitter_sizes(self, parent):
        """Set splitter initial size ratio."""
        # Get parent window dimensions
        parent_width = parent.width()
        
        # Set initial sizes based on parent window width
        nav_width = max(int(parent_width / 8), 150)
        content_width = parent_width - nav_width
        
        self.splitter.setSizes([nav_width, content_width])
        
    def _create_resize_event_filter(self, parent):
        """Create window resize event filter."""
        ui_self = self
        
        class ResizeEventFilter(QtCore.QObject):
            def eventFilter(self, obj, event):
                if event.type() == QtCore.QEvent.Resize:
                    # Reset navigation panel constraints when window is resized
                    ui_self._setup_nav_panel_constraints(parent)
                    ui_self._setup_splitter_sizes(parent)
                return False
                
        return ResizeEventFilter()
        
    def _create_general_page(self):
        """Create general settings page."""
        page = QtWidgets.QWidget()
        page.setObjectName("generalPage")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Language settings
        lang_group = QtWidgets.QGroupBox()
        lang_group.setObjectName("languageGroup")
        lang_layout = QtWidgets.QVBoxLayout(lang_group)
        
        self.lang_label = QtWidgets.QLabel()
        lang_layout.addWidget(self.lang_label)
        
        self.lang_combo = QtWidgets.QComboBox()
        self.lang_combo.setObjectName("languageCombo")
        self.lang_combo.addItem(self.tr("English"), "en")
        self.lang_combo.addItem(self.tr("Simplified Chinese"), "zh_CN")
        lang_layout.addWidget(self.lang_combo)
        
        lang_layout.addStretch()
        layout.addWidget(lang_group)
        layout.addStretch()
        
        return page
        
    def _connect_signals(self):
        """Connect signals."""
        # Use exclusive button group to ensure only one button is checked
        self.button_group = QtWidgets.QButtonGroup()
        self.button_group.addButton(self.general_button)
        self.button_group.setExclusive(True)
        
        self.general_button.clicked.connect(lambda: self.content_area.setCurrentIndex(0))
        
    def retranslateUi(self):
        """Translate UI text."""
        # Navigation buttons
        self.general_button.setText(self.tr("General"))
        
        # General settings page
        self.lang_label.setText(self.tr("Language:"))
        
        # Clear and re-add translated options
        self.lang_combo.clear()
        self.lang_combo.addItem(self.tr("English"), "en")
        self.lang_combo.addItem(self.tr("Simplified Chinese"), "zh_CN")
        
        # Group box titles
        for i in range(self.content_area.count()):
            widget = self.content_area.widget(i)
            if widget.objectName() == "generalPage":
                group = widget.findChild(QtWidgets.QGroupBox, "languageGroup")
                if group:
                    group.setTitle(self.tr("Language Settings"))