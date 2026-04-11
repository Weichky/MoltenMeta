from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QObject

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from core.log import getLogLevelMap
from catalog import getSupportedLanguagesNameMap

from domain.settings import Settings


class UiSettingsPage(QObject):
    def __init__(self, settings: Settings):
        super().__init__()
        self._settings = settings

    def setupUi(self, settingsPage: QtWidgets.QWidget):
        # Prepare translations for combo box items
        self.display_mode_translations = {
            "light": self.tr("Light"),
            "dark": self.tr("Dark"),
            "system": self.tr("System"),
        }

        self.color_translations = {
            "blue": self.tr("Blue"),
            "teal": self.tr("Teal"),
            "amber": self.tr("Amber"),
            "cyan": self.tr("Cyan"),
            "red": self.tr("Red"),
        }

        if not settingsPage.objectName():
            settingsPage.setObjectName("settingsPage")

        self.root_layout = QtWidgets.QHBoxLayout(settingsPage)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        # Create resizable splitter
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("settingsSplitter")
        self.splitter.setChildrenCollapsible(
            False
        )  # Prevent child widgets from being completely collapsed

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
        self.plot_button = QtWidgets.QPushButton()

        self.general_button.setCheckable(True)
        self.log_button.setCheckable(True)
        self.plot_button.setCheckable(True)
        self.general_button.setChecked(True)
        self.log_button.setChecked(False)
        self.plot_button.setChecked(False)

        self.nav_buttons_layout.addWidget(self.general_button)
        self.nav_buttons_layout.addWidget(self.log_button)
        self.nav_buttons_layout.addWidget(self.plot_button)

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

        # Create plot settings page
        self.plot_page = self._createPlotPage()
        self.content_area.addWidget(self.plot_page)

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

        # Appearance settings
        appearance_group = QtWidgets.QGroupBox()
        appearance_group.setObjectName("appearanceGroup")
        appearance_layout = QtWidgets.QVBoxLayout(appearance_group)

        self.theme_color_label = QtWidgets.QLabel()
        appearance_layout.addWidget(self.theme_color_label)

        self.theme_color_combo = QtWidgets.QComboBox()
        self.theme_color_combo.setObjectName("themeColorCombo")
        appearance_layout.addWidget(self.theme_color_combo)

        for value, translated_text in self.color_translations.items():
            self.theme_color_combo.addItem(translated_text, value)

        theme_color = self._settings.theme
        self.theme_color_combo.setCurrentIndex(
            self.theme_color_combo.findData(theme_color)
        )

        self.theme_mode_label = QtWidgets.QLabel()
        appearance_layout.addWidget(self.theme_mode_label)

        self.theme_mode_combo = QtWidgets.QComboBox()
        self.theme_mode_combo.setObjectName("themeModeCombo")
        appearance_layout.addWidget(self.theme_mode_combo)

        for key, translated_text in self.display_mode_translations.items():
            self.theme_mode_combo.addItem(translated_text, key)

        theme_mode = self._settings.theme_mode
        self.theme_mode_combo.setCurrentIndex(
            self.theme_mode_combo.findData(theme_mode)
        )

        self.density_scale_label = QtWidgets.QLabel()
        appearance_layout.addWidget(self.density_scale_label)

        self.density_scale_spin = QtWidgets.QSpinBox()
        self.density_scale_spin.setObjectName("densityScaleSpin")
        self.density_scale_spin.setRange(-4, 4)
        self.density_scale_spin.setValue(self._settings.density_scale)
        appearance_layout.addWidget(self.density_scale_spin)

        appearance_layout.addStretch()
        page_layout.addWidget(appearance_group)

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

        log_display_group = QtWidgets.QGroupBox()
        log_display_group.setObjectName("logDisplayGroup")
        log_display_layout = QtWidgets.QVBoxLayout(log_display_group)

        self.log_display = QtWidgets.QTextEdit()
        self.log_display.setObjectName("logDisplay")
        self.log_display.setReadOnly(True)
        log_display_layout.addWidget(self.log_display)

        page_layout.addWidget(log_display_group)

        return page

    def _createPlotPage(self) -> QtWidgets.QWidget:
        page = QtWidgets.QWidget()
        page.setObjectName("plotPage")
        page_layout = QtWidgets.QVBoxLayout(page)
        page_layout.setSpacing(10)
        page_layout.setContentsMargins(10, 10, 10, 10)

        plot_style_group = QtWidgets.QGroupBox()
        plot_style_group.setObjectName("plotStyleGroup")
        plot_style_layout = QtWidgets.QFormLayout(plot_style_group)

        self.palette_label = QtWidgets.QLabel()
        self.palette_combo = QtWidgets.QComboBox()
        self.palette_combo.setObjectName("paletteCombo")
        for name in ["default", "custom"]:
            self.palette_combo.addItem(name, name)
        palette = self._settings.plot_colorscheme or "default"
        self.palette_combo.setCurrentIndex(self.palette_combo.findData(palette))
        plot_style_layout.addRow(self.palette_label, self.palette_combo)

        self.algorithm_label = QtWidgets.QLabel()
        self.algorithm_combo = QtWidgets.QComboBox()
        self.algorithm_combo.setObjectName("algorithmCombo")
        for algo in ["linear", "harmonic", "colorwheel"]:
            self.algorithm_combo.addItem(algo, algo)
        algorithm = self._settings.plot_color_algorithm or "linear"
        self.algorithm_combo.setCurrentIndex(self.algorithm_combo.findData(algorithm))
        plot_style_layout.addRow(self.algorithm_label, self.algorithm_combo)

        self.color_scheme_label = QtWidgets.QLabel()
        self.color_scheme_combo = QtWidgets.QComboBox()
        self.color_scheme_combo.setObjectName("colorSchemeCombo")
        for scheme in ["follow", "light", "dark"]:
            self.color_scheme_combo.addItem(scheme, scheme)
        color_scheme = self._settings.plot_color_scheme
        self.color_scheme_combo.setCurrentIndex(
            self.color_scheme_combo.findData(color_scheme)
        )
        plot_style_layout.addRow(self.color_scheme_label, self.color_scheme_combo)

        self.line_style_label = QtWidgets.QLabel()
        self.line_style_combo = QtWidgets.QComboBox()
        self.line_style_combo.setObjectName("lineStyleCombo")
        for style in ["-", "--", ":", "-."]:
            self.line_style_combo.addItem(style, style)
        line_style = self._settings.plot_line_style or "-"
        self.line_style_combo.setCurrentIndex(
            self.line_style_combo.findData(line_style)
        )
        plot_style_layout.addRow(self.line_style_label, self.line_style_combo)

        self.marker_label = QtWidgets.QLabel()
        self.marker_combo = QtWidgets.QComboBox()
        self.marker_combo.setObjectName("markerCombo")
        for marker in ["o", "s", "^", "D", "v", "<", ">"]:
            self.marker_combo.addItem(marker, marker)
        marker = self._settings.plot_marker or "o"
        self.marker_combo.setCurrentIndex(self.marker_combo.findData(marker))
        plot_style_layout.addRow(self.marker_label, self.marker_combo)

        self.line_width_label = QtWidgets.QLabel()
        self.line_width_spin = QtWidgets.QDoubleSpinBox()
        self.line_width_spin.setObjectName("lineWidthSpin")
        self.line_width_spin.setRange(0.5, 10.0)
        self.line_width_spin.setSingleStep(0.5)
        self.line_width_spin.setValue(self._settings.plot_line_width or 2.0)
        plot_style_layout.addRow(self.line_width_label, self.line_width_spin)

        self.marker_size_label = QtWidgets.QLabel()
        self.marker_size_spin = QtWidgets.QDoubleSpinBox()
        self.marker_size_spin.setObjectName("markerSizeSpin")
        self.marker_size_spin.setRange(1.0, 20.0)
        self.marker_size_spin.setSingleStep(0.5)
        self.marker_size_spin.setValue(self._settings.plot_marker_size or 6.0)
        plot_style_layout.addRow(self.marker_size_label, self.marker_size_spin)

        self.grid_check = QtWidgets.QCheckBox()
        self.grid_check.setObjectName("gridCheck")
        self.grid_check.setChecked(
            self._settings.plot_grid if self._settings.plot_grid is not None else True
        )
        plot_style_layout.addRow(self.grid_check)

        self.font_size_label = QtWidgets.QLabel()
        self.font_size_spin = QtWidgets.QSpinBox()
        self.font_size_spin.setObjectName("fontSizeSpin")
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(self._settings.plot_font_size or 12)
        plot_style_layout.addRow(self.font_size_label, self.font_size_spin)

        page_layout.addWidget(plot_style_group)

        preview_group = QtWidgets.QGroupBox()
        preview_group.setObjectName("plotPreviewGroup")
        preview_layout = QtWidgets.QVBoxLayout(preview_group)

        self.preview_figure = Figure(figsize=(6, 3))
        self.preview_canvas = FigureCanvasQTAgg(self.preview_figure)
        self.preview_ax = self.preview_figure.add_subplot(111)
        preview_layout.addWidget(self.preview_canvas)

        page_layout.addWidget(preview_group)
        page_layout.addStretch()

        return page

    def retranslateUi(self):
        self.display_mode_translations = {
            "light": self.tr("Light"),
            "dark": self.tr("Dark"),
            "system": self.tr("System"),
        }

        self.color_translations = {
            "blue": self.tr("Blue"),
            "teal": self.tr("Teal"),
            "amber": self.tr("Amber"),
            "cyan": self.tr("Cyan"),
            "red": self.tr("Red"),
        }

        # Navigation buttons
        self.general_button.setText(self.tr("General"))
        self.log_button.setText(self.tr("Log"))
        self.plot_button.setText(self.tr("Plot"))

        # General settings page
        self.lang_label.setText(self.tr("Language:"))
        self.theme_mode_label.setText(self.tr("Display Mode:"))
        self.theme_color_label.setText(self.tr("Theme Color:"))
        self.density_scale_label.setText(self.tr("Density Scale:"))

        # Log settings page
        self.log_level_label.setText(self.tr("Log level:"))
        log_display_group = self.log_page.findChild(
            QtWidgets.QWidget, "logDisplayGroup"
        )
        if log_display_group:
            log_display_group.setTitle(self.tr("Log Output"))

        # Plot settings page
        self.palette_label.setText(self.tr("Palette:"))
        self.algorithm_label.setText(self.tr("Color Algorithm:"))
        self.color_scheme_label.setText(self.tr("Color Scheme:"))
        self.line_style_label.setText(self.tr("Line Style:"))
        self.marker_label.setText(self.tr("Marker:"))
        self.line_width_label.setText(self.tr("Line Width:"))
        self.marker_size_label.setText(self.tr("Marker Size:"))
        self.font_size_label.setText(self.tr("Font Size:"))
        self.grid_check.setText(self.tr("Show Grid"))
        preview_group = self.plot_page.findChild(QtWidgets.QWidget, "plotPreviewGroup")
        if preview_group:
            preview_group.setTitle(self.tr("Preview"))

        # # Group box titles
        # for i in range(self.content_area.count()):
        #     widget = self.content_area.widget(i)
        #     if widget.objectName() == "generalPage":
        #         group = widget.findChild(QtWidgets.QGroupBox, "languageGroup")
        #         if group:
        #             group.setTitle(self.tr("Language Settings"))
        #         group = widget.findChild(QtWidgets.QGroupBox, "appearanceGroup")
        #         if group:
        #             group.setTitle(self.tr("Appearance Settings"))
        #     if widget.objectName() == "loggingPage":
        #         group = widget.findChild(QtWidgets.QGroupBox, "logLevelGroup")
        #         if group:
        #             group.setTitle(self.tr("Logging Settings"))

        for i in range(self.theme_mode_combo.count()):
            data = self.theme_mode_combo.itemData(i)
            new_text = self.display_mode_translations[data]
            self.theme_mode_combo.setItemText(i, new_text)

        for i in range(self.theme_color_combo.count()):
            data = self.theme_color_combo.itemData(i)
            new_text = self.color_translations[data]
            self.theme_color_combo.setItemText(i, new_text)

    def updatePreview(
        self,
        colors: list[str],
        line_style: str = "-",
        marker: str = "o",
        line_width: float = 2.0,
        grid: bool = True,
    ) -> None:
        self.preview_ax.clear()
        x = list(range(10))
        for i, color in enumerate(colors[:5]):
            y = [v + i * 0.5 for v in x]
            self.preview_ax.plot(
                x,
                y,
                color=color,
                linestyle=line_style,
                marker=marker,
                linewidth=line_width,
                markersize=4,
            )
        self.preview_ax.grid(grid, alpha=0.3)
        self.preview_figure.tight_layout()
        self.preview_canvas.draw()
