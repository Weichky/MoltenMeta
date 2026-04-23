from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QObject

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np

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

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("settingsSplitter")
        self.splitter.setChildrenCollapsible(False)

        self.nav_panel = QtWidgets.QWidget()
        self.nav_panel.setObjectName("settingsNavPanel")
        self.nav_panel.setMinimumWidth(200)
        self.nav_panel.setMaximumWidth(200)

        self.nav_layout = QtWidgets.QVBoxLayout(self.nav_panel)
        self.nav_layout.setContentsMargins(16, 24, 16, 24)
        self.nav_layout.setSpacing(8)

        self.general_button = QtWidgets.QPushButton()
        self.log_button = QtWidgets.QPushButton()
        self.plot_button = QtWidgets.QPushButton()

        self.general_button.setObjectName("sidebarButton")
        self.log_button.setObjectName("sidebarButton")
        self.plot_button.setObjectName("sidebarButton")

        self.general_button.setCheckable(True)
        self.log_button.setCheckable(True)
        self.plot_button.setCheckable(True)
        self.general_button.setChecked(True)

        self.nav_layout.addWidget(self.general_button)
        self.nav_layout.addWidget(self.log_button)
        self.nav_layout.addWidget(self.plot_button)
        self.nav_layout.addStretch()

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
        self.splitter.setSizes([200, 600])

        self.root_layout.addWidget(self.splitter)

    def _createGeneralPage(self) -> QtWidgets.QWidget:
        page = QtWidgets.QWidget()
        page.setObjectName("generalPage")
        page_layout = QtWidgets.QVBoxLayout(page)
        page_layout.setSpacing(20)
        page_layout.setContentsMargins(32, 32, 32, 32)

        section_label = QtWidgets.QLabel()
        section_label.setObjectName("sectionLabel")
        section_label.setText(self.tr("Language"))
        page_layout.addWidget(section_label)

        lang_layout = QtWidgets.QHBoxLayout()
        lang_layout.setSpacing(12)

        self.lang_combo = QtWidgets.QComboBox()
        self.lang_combo.setObjectName("languageCombo")

        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()

        for code, name in getSupportedLanguagesNameMap().items():
            self.lang_combo.addItem(name, code)

        language = self._settings.language
        self.lang_combo.setCurrentIndex(self.lang_combo.findData(language))

        page_layout.addLayout(lang_layout)

        self.section_line1 = QtWidgets.QFrame()
        self.section_line1.setObjectName("dividerLine")
        self.section_line1.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.section_line1.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.section_line1.setFixedHeight(1)
        page_layout.addWidget(self.section_line1)

        appearance_label = QtWidgets.QLabel()
        appearance_label.setObjectName("sectionLabel")
        appearance_label.setText(self.tr("Appearance"))
        page_layout.addWidget(appearance_label)

        grid_layout = QtWidgets.QGridLayout()
        grid_layout.setSpacing(12)
        grid_layout.setColumnMinimumWidth(0, 100)

        self.primary_color_input = QtWidgets.QLineEdit()
        self.primary_color_input.setObjectName("primaryColorInput")
        self.primary_color_input.setPlaceholderText("#C62828")
        primary_color = self._settings.primary_color or "#C62828"
        self.primary_color_input.setText(primary_color)
        grid_layout.addWidget(QtWidgets.QLabel(self.tr("Primary Color")), 0, 0)
        grid_layout.addWidget(self.primary_color_input, 0, 1)

        self.secondary_color_input = QtWidgets.QLineEdit()
        self.secondary_color_input.setObjectName("secondaryColorInput")
        self.secondary_color_input.setPlaceholderText("#1A1A1A")
        secondary_color = self._settings.secondary_color or "#1A1A1A"
        self.secondary_color_input.setText(secondary_color)
        grid_layout.addWidget(QtWidgets.QLabel(self.tr("Secondary Color")), 1, 0)
        grid_layout.addWidget(self.secondary_color_input, 1, 1)

        self.density_scale_combo = QtWidgets.QComboBox()
        self.density_scale_combo.setObjectName("densityScaleCombo")
        density_options = [
            (self.tr("50%"), -4),
            (self.tr("75%"), -3),
            (self.tr("100%"), -2),
            (self.tr("125%"), -1),
            (self.tr("150%"), 0),
        ]
        for display, value in density_options:
            self.density_scale_combo.addItem(display, value)
        current_density = self._settings.density_scale
        self.density_scale_combo.setCurrentIndex(
            self.density_scale_combo.findData(current_density)
        )
        grid_layout.addWidget(QtWidgets.QLabel(self.tr("Density")), 2, 0)
        grid_layout.addWidget(self.density_scale_combo, 2, 1)

        page_layout.addLayout(grid_layout)
        page_layout.addStretch()

        return page

    def _createLogPage(self) -> QtWidgets.QWidget:
        page = QtWidgets.QWidget()
        page.setObjectName("loggingPage")
        page_layout = QtWidgets.QVBoxLayout(page)
        page_layout.setSpacing(20)
        page_layout.setContentsMargins(32, 32, 32, 32)

        section_label = QtWidgets.QLabel()
        section_label.setObjectName("sectionLabel")
        section_label.setText(self.tr("Log Level"))
        page_layout.addWidget(section_label)

        row_layout = QtWidgets.QHBoxLayout()
        row_layout.setSpacing(12)

        self.log_level_combo = QtWidgets.QComboBox()
        self.log_level_combo.setObjectName("logLevelCombo")

        row_layout.addWidget(self.log_level_combo)
        row_layout.addStretch()

        for level in getLogLevelMap().keys():
            self.log_level_combo.addItem(self.tr(level), level)

        log_level = self._settings.log_level
        self.log_level_combo.setCurrentIndex(self.log_level_combo.findData(log_level))

        page_layout.addLayout(row_layout)

        self.section_line1 = QtWidgets.QFrame()
        self.section_line1.setObjectName("dividerLine")
        self.section_line1.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.section_line1.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.section_line1.setFixedHeight(1)
        page_layout.addWidget(self.section_line1)

        output_label = QtWidgets.QLabel()
        output_label.setObjectName("sectionLabel")
        output_label.setText(self.tr("Log Output"))
        page_layout.addWidget(output_label)

        self.log_display = QtWidgets.QTextEdit()
        self.log_display.setObjectName("logDisplay")
        self.log_display.setReadOnly(True)
        page_layout.addWidget(self.log_display)

        return page

    def _createPlotPage(self) -> QtWidgets.QWidget:
        page = QtWidgets.QWidget()
        page.setObjectName("plotPage")
        page_layout = QtWidgets.QVBoxLayout(page)
        page_layout.setSpacing(20)
        page_layout.setContentsMargins(32, 32, 32, 32)

        basic_label = QtWidgets.QLabel()
        basic_label.setObjectName("sectionLabel")
        basic_label.setText(self.tr("Basic"))
        page_layout.addWidget(basic_label)

        basic_grid = QtWidgets.QGridLayout()
        basic_grid.setSpacing(12)
        basic_grid.setColumnMinimumWidth(0, 80)

        self.palette_combo = QtWidgets.QComboBox()
        self.palette_combo.setObjectName("paletteCombo")
        self.palette_items = [
            (self.tr("Default"), "default"),
            (self.tr("Custom"), "custom"),
        ]
        for display, value in self.palette_items:
            self.palette_combo.addItem(display, value)
        palette = self._settings.plot_colorscheme or "default"
        self.palette_combo.setCurrentIndex(self.palette_combo.findData(palette))
        basic_grid.addWidget(QtWidgets.QLabel(self.tr("Palette")), 0, 0)
        basic_grid.addWidget(self.palette_combo, 0, 1)

        self.algorithm_combo = QtWidgets.QComboBox()
        self.algorithm_combo.setObjectName("algorithmCombo")
        self.algorithm_items = [
            (self.tr("Linear"), "linear"),
            (self.tr("Harmonic"), "harmonic"),
            (self.tr("Colorwheel"), "colorwheel"),
        ]
        for display, value in self.algorithm_items:
            self.algorithm_combo.addItem(display, value)
        algorithm = self._settings.plot_color_algorithm or "linear"
        self.algorithm_combo.setCurrentIndex(self.algorithm_combo.findData(algorithm))
        basic_grid.addWidget(QtWidgets.QLabel(self.tr("Algorithm")), 1, 0)
        basic_grid.addWidget(self.algorithm_combo, 1, 1)

        self.line_style_combo = QtWidgets.QComboBox()
        self.line_style_combo.setObjectName("lineStyleCombo")
        self.line_style_items = [
            (self.tr("Solid"), "-"),
            (self.tr("Dashed"), "--"),
            (self.tr("Dotted"), ":"),
            (self.tr("Dash-Dot"), "-."),
        ]
        for display, value in self.line_style_items:
            self.line_style_combo.addItem(display, value)
        line_style = self._settings.plot_line_style or "-"
        self.line_style_combo.setCurrentIndex(
            self.line_style_combo.findData(line_style)
        )
        basic_grid.addWidget(QtWidgets.QLabel(self.tr("Line Style")), 5, 0)
        basic_grid.addWidget(self.line_style_combo, 5, 1)

        self.marker_combo = QtWidgets.QComboBox()
        self.marker_combo.setObjectName("markerCombo")
        self.marker_items = [
            (self.tr("Circle"), "o"),
            (self.tr("Square"), "s"),
            (self.tr("Triangle"), "^"),
            (self.tr("Diamond"), "D"),
        ]
        for display, value in self.marker_items:
            self.marker_combo.addItem(display, value)
        marker = self._settings.plot_marker or "o"
        self.marker_combo.setCurrentIndex(self.marker_combo.findData(marker))
        basic_grid.addWidget(QtWidgets.QLabel(self.tr("Marker")), 4, 0)
        basic_grid.addWidget(self.marker_combo, 4, 1)

        page_layout.addLayout(basic_grid)

        self.section_line1 = QtWidgets.QFrame()
        self.section_line1.setObjectName("dividerLine")
        self.section_line1.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.section_line1.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.section_line1.setFixedHeight(1)
        page_layout.addWidget(self.section_line1)

        line_label = QtWidgets.QLabel()
        line_label.setObjectName("sectionLabel")
        line_label.setText(self.tr("Line & Grid"))
        page_layout.addWidget(line_label)

        line_grid = QtWidgets.QGridLayout()
        line_grid.setSpacing(12)
        line_grid.setColumnMinimumWidth(0, 80)

        self.line_width_spin = QtWidgets.QDoubleSpinBox()
        self.line_width_spin.setObjectName("lineWidthSpin")
        self.line_width_spin.setRange(0.5, 10.0)
        self.line_width_spin.setSingleStep(0.5)
        self.line_width_spin.setValue(self._settings.plot_line_width or 2.0)
        line_grid.addWidget(QtWidgets.QLabel(self.tr("Width")), 0, 0)
        line_grid.addWidget(self.line_width_spin, 0, 1)

        self.marker_size_spin = QtWidgets.QDoubleSpinBox()
        self.marker_size_spin.setObjectName("markerSizeSpin")
        self.marker_size_spin.setRange(1.0, 20.0)
        self.marker_size_spin.setSingleStep(0.5)
        self.marker_size_spin.setValue(self._settings.plot_marker_size or 6.0)
        line_grid.addWidget(QtWidgets.QLabel(self.tr("Marker Size")), 1, 0)
        line_grid.addWidget(self.marker_size_spin, 1, 1)

        self.grid_check = QtWidgets.QCheckBox()
        self.grid_check.setObjectName("gridCheck")
        self.grid_check.setChecked(
            self._settings.plot_grid if self._settings.plot_grid is not None else True
        )
        line_grid.addWidget(self.grid_check, 2, 0, 1, 2)

        self.grid_mode_combo = QtWidgets.QComboBox()
        self.grid_mode_combo.setObjectName("gridModeCombo")
        self.grid_mode_items = [
            (self.tr("Auto"), "auto"),
            (self.tr("Relative"), "relative"),
            (self.tr("Absolute"), "absolute"),
        ]
        for display, value in self.grid_mode_items:
            self.grid_mode_combo.addItem(display, value)
        grid_mode = self._settings.plot_grid_mode or "auto"
        self.grid_mode_combo.setCurrentIndex(self.grid_mode_combo.findData(grid_mode))
        line_grid.addWidget(QtWidgets.QLabel(self.tr("Grid Mode")), 3, 0)
        line_grid.addWidget(self.grid_mode_combo, 3, 1)

        self.grid_density_spin = QtWidgets.QDoubleSpinBox()
        self.grid_density_spin.setObjectName("gridDensitySpin")
        self.grid_density_spin.setDecimals(2)
        self.grid_density_spin.setRange(0.01, 999999)
        self.grid_density_spin.setValue(self._settings.plot_grid_density or 1.0)
        line_grid.addWidget(QtWidgets.QLabel(self.tr("Grid Density")), 4, 0)
        line_grid.addWidget(self.grid_density_spin, 4, 1)

        self.grid_label_density_spin = QtWidgets.QDoubleSpinBox()
        self.grid_label_density_spin.setObjectName("gridLabelDensitySpin")
        self.grid_label_density_spin.setDecimals(2)
        self.grid_label_density_spin.setRange(0.01, 999999)
        self.grid_label_density_spin.setValue(
            self._settings.plot_grid_label_density or 1.0
        )
        line_grid.addWidget(QtWidgets.QLabel(self.tr("Label Density")), 5, 0)
        line_grid.addWidget(self.grid_label_density_spin, 5, 1)

        page_layout.addLayout(line_grid)

        self.section_line2 = QtWidgets.QFrame()
        self.section_line2.setObjectName("dividerLine")
        self.section_line2.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.section_line2.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.section_line2.setFixedHeight(1)
        page_layout.addWidget(self.section_line2)

        typography_label = QtWidgets.QLabel()
        typography_label.setObjectName("sectionLabel")
        typography_label.setText(self.tr("Typography"))
        page_layout.addWidget(typography_label)

        typography_grid = QtWidgets.QGridLayout()
        typography_grid.setSpacing(12)
        typography_grid.setColumnMinimumWidth(0, 80)

        self.title_font_size_spin = QtWidgets.QSpinBox()
        self.title_font_size_spin.setObjectName("titleFontSizeSpin")
        self.title_font_size_spin.setRange(6, 32)
        self.title_font_size_spin.setValue(self._settings.plot_title_font_size or 14)
        typography_grid.addWidget(QtWidgets.QLabel(self.tr("Title")), 0, 0)
        typography_grid.addWidget(self.title_font_size_spin, 0, 1)

        self.label_font_size_spin = QtWidgets.QSpinBox()
        self.label_font_size_spin.setObjectName("labelFontSizeSpin")
        self.label_font_size_spin.setRange(6, 32)
        self.label_font_size_spin.setValue(self._settings.plot_label_font_size or 12)
        typography_grid.addWidget(QtWidgets.QLabel(self.tr("Label")), 1, 0)
        typography_grid.addWidget(self.label_font_size_spin, 1, 1)

        self.tick_font_size_spin = QtWidgets.QSpinBox()
        self.tick_font_size_spin.setObjectName("tickFontSizeSpin")
        self.tick_font_size_spin.setRange(6, 32)
        self.tick_font_size_spin.setValue(self._settings.plot_tick_font_size or 10)
        typography_grid.addWidget(QtWidgets.QLabel(self.tr("Tick")), 2, 0)
        typography_grid.addWidget(self.tick_font_size_spin, 2, 1)

        self.legend_font_size_spin = QtWidgets.QSpinBox()
        self.legend_font_size_spin.setObjectName("legendFontSizeSpin")
        self.legend_font_size_spin.setRange(6, 32)
        self.legend_font_size_spin.setValue(self._settings.plot_legend_font_size or 10)
        typography_grid.addWidget(QtWidgets.QLabel(self.tr("Legend")), 3, 0)
        typography_grid.addWidget(self.legend_font_size_spin, 3, 1)

        page_layout.addLayout(typography_grid)

        self.section_line3 = QtWidgets.QFrame()
        self.section_line3.setObjectName("dividerLine")
        self.section_line3.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.section_line3.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.section_line3.setFixedHeight(1)
        page_layout.addWidget(self.section_line3)

        preview_label = QtWidgets.QLabel()
        preview_label.setObjectName("sectionLabel")
        preview_label.setText(self.tr("Preview"))
        page_layout.addWidget(preview_label)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setObjectName("previewScrollArea")
        scroll_area.setWidgetResizable(False)
        scroll_area.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        preview_widget = QtWidgets.QWidget()
        preview_inner_layout = QtWidgets.QVBoxLayout(preview_widget)
        preview_inner_layout.setContentsMargins(0, 0, 0, 0)

        self.preview_figure = Figure(figsize=(8, 6), constrained_layout=True)
        self.preview_canvas = FigureCanvasQTAgg(self.preview_figure)
        self.preview_canvas.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
        self.preview_ax1 = self.preview_figure.add_subplot(2, 2, 1)
        self.preview_ax2 = self.preview_figure.add_subplot(2, 2, 2)
        self.preview_ax3 = self.preview_figure.add_subplot(2, 2, 3, projection="3d")
        self.preview_ax4 = self.preview_figure.add_subplot(2, 2, 4)
        preview_inner_layout.addWidget(self.preview_canvas)

        scroll_area.setWidget(preview_widget)
        page_layout.addWidget(scroll_area)

        return page

    def retranslateUi(self):
        self.general_button.setText(self.tr("General"))
        self.log_button.setText(self.tr("Log"))
        self.plot_button.setText(self.tr("Plot"))

        for i, (display, value) in enumerate(self.palette_items):
            self.palette_combo.setItemText(i, self.tr(display))

        for i, (display, value) in enumerate(self.algorithm_items):
            self.algorithm_combo.setItemText(i, self.tr(display))

        for i, (display, value) in enumerate(self.line_style_items):
            self.line_style_combo.setItemText(i, self.tr(display))

        for i, (display, value) in enumerate(self.marker_items):
            self.marker_combo.setItemText(i, self.tr(display))

        for i, (display, value) in enumerate(self.grid_mode_items):
            self.grid_mode_combo.setItemText(i, self.tr(display))

    def _calcGridTicks(
        self, axis_min: float, axis_max: float, grid_mode: str, grid_density: float
    ) -> np.ndarray:
        range_val = axis_max - axis_min
        if grid_mode == "absolute":
            interval = grid_density
        else:
            interval = range_val / (10.0 * grid_density)
        return np.arange(axis_min, axis_max + interval, interval)

    def _applyGridToAxis(
        self,
        ax,
        enabled: bool,
        grid_mode: str,
        grid_density: float,
        grid_label_density: float = 1.0,
    ) -> None:
        if not enabled:
            ax.grid(False)
            return

        if grid_mode == "auto":
            ax.grid(True, alpha=0.3)
            return

        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        x_grid_ticks = self._calcGridTicks(xlim[0], xlim[1], grid_mode, grid_density)
        y_grid_ticks = self._calcGridTicks(ylim[0], ylim[1], grid_mode, grid_density)

        ax.set_xticks(x_grid_ticks)
        ax.set_yticks(y_grid_ticks)
        ax.set_xticks(x_grid_ticks, minor=True)
        ax.set_yticks(y_grid_ticks, minor=True)
        ax.tick_params(which="major", label1On=True)
        ax.tick_params(which="minor", label1On=False)

        ax.grid(True, which="major", alpha=0.3)
        ax.grid(True, which="minor", alpha=0.15)

        label_every = max(1, int(grid_label_density))
        for i, tick in enumerate(ax.xaxis.get_major_ticks()):
            tick.label1.set_visible(i % label_every == 0)
        for i, tick in enumerate(ax.yaxis.get_major_ticks()):
            tick.label1.set_visible(i % label_every == 0)

    def updatePreview(
        self,
        colors: list[str],
        line_style: str = "-",
        marker: str = "o",
        line_width: float = 2.0,
        grid: bool = True,
        grid_mode: str = "relative",
        grid_density: float = 1.0,
        grid_label_density: float = 1.0,
        title_font_size: int = 14,
        label_font_size: int = 12,
        tick_font_size: int = 10,
        legend_font_size: int = 10,
    ) -> None:
        self.preview_ax1.clear()
        self.preview_ax2.clear()
        self.preview_ax3.clear()
        self.preview_ax4.clear()

        x = list(range(10))

        self.preview_ax1.set_title("Line 2D", fontsize=title_font_size)
        for i, color in enumerate(colors[:5]):
            y = [v + i * 0.5 for v in x]
            self.preview_ax1.plot(
                x,
                y,
                color=color,
                linestyle=line_style,
                marker=marker,
                linewidth=line_width,
                markersize=4,
            )
        self.preview_ax1.set_xlabel("X", fontsize=label_font_size)
        self.preview_ax1.set_ylabel("Y", fontsize=label_font_size)
        self.preview_ax1.tick_params(axis="both", labelsize=tick_font_size)
        self._applyGridToAxis(
            self.preview_ax1, grid, grid_mode, grid_density, grid_label_density
        )

        self.preview_ax2.set_title("Scatter 2D", fontsize=title_font_size)
        for i, color in enumerate(colors[:5]):
            xs = np.random.rand(10) * 10
            ys = np.random.rand(10) + i
            self.preview_ax2.scatter(xs, ys, c=color, s=30, marker=marker)
        self.preview_ax2.set_xlabel("X", fontsize=label_font_size)
        self.preview_ax2.set_ylabel("Y", fontsize=label_font_size)
        self.preview_ax2.tick_params(axis="both", labelsize=tick_font_size)
        self._applyGridToAxis(
            self.preview_ax2, grid, grid_mode, grid_density, grid_label_density
        )

        self.preview_ax3.set_title("Surface 3D", fontsize=title_font_size)
        X = np.linspace(-5, 5, 30)
        Y = np.linspace(-5, 5, 30)
        X, Y = np.meshgrid(X, Y)
        Z = np.sin(np.sqrt(X**2 + Y**2))
        self.preview_ax3.plot_surface(
            X, Y, Z, color=colors[0], alpha=0.7, rstride=1, cstride=1
        )
        self.preview_ax3.view_init(elev=25, azim=45)
        self.preview_ax3.set_box_aspect([1.2, 1.2, 0.8])
        self.preview_ax3.tick_params(axis="both", labelsize=tick_font_size)

        self.preview_ax4.set_title("Contour", fontsize=title_font_size)
        X = np.arange(-5, 5, 0.5)
        Y = np.arange(-5, 5, 0.5)
        X, Y = np.meshgrid(X, Y)
        Z = np.sin(np.sqrt(X**2 + Y**2))
        self.preview_ax4.contourf(X, Y, Z, levels=10, colors=colors[:10])
        self.preview_ax4.set_xlim(-5, 5)
        self.preview_ax4.set_ylim(-5, 5)
        self.preview_ax4.set_xlabel("X", fontsize=label_font_size)
        self.preview_ax4.set_ylabel("Y", fontsize=label_font_size)
        self.preview_ax4.tick_params(axis="both", labelsize=tick_font_size)
        self._applyGridToAxis(
            self.preview_ax4, grid, grid_mode, grid_density, grid_label_density
        )

        self.preview_canvas.draw()
