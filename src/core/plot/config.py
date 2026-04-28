from __future__ import annotations
import logging
from dataclasses import dataclass, field
from importlib.resources import files
from typing import TYPE_CHECKING

import tomllib

from catalog import (
    DEFAULT_PLOT_TYPE,
    DEFAULT_THEME_PRESET,
    DEFAULT_PLOT_BG,
    DEFAULT_PLOT_FG,
    ColorAlgorithm,
    DEFAULT_SCATTER_3D_DEFAULT_COORD_INDEX,
    DEFAULT_CONTOUR_TRIANGULAR_HEIGHT_FACTOR,
    DEFAULT_CONTOUR_TRIANGULAR_XLIM,
    DEFAULT_CONTOUR_TRIANGULAR_YLIM,
    DEFAULT_CONTOUR_TRIANGULAR_TICK_POSITIONS,
    DEFAULT_CONTOUR_TRIANGULAR_TICK_LENGTH,
    DEFAULT_CONTOUR_TRIANGULAR_ELEM_LABELS,
    DEFAULT_CONTOUR_TRIANGULAR_COLORBAR_LABEL,
    DEFAULT_CONTOUR_TRIANGULAR_LEVELS,
    DEFAULT_CONTOUR_TRIANGULAR_ALPHA,
    DEFAULT_TRIANGULAR_GRID_ALPHA,
    DEFAULT_TRIANGULAR_GRID_LINE_WIDTH,
)

from core.plot.color import ColorPalette, ColorGenerator, ThemeColors
from core.plot.style import PlotStyle, getDefaultPlotStyle

if TYPE_CHECKING:
    from application.settings import Settings

_logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PlotStyleConfig:
    plotType: str = DEFAULT_PLOT_TYPE
    style: PlotStyle = field(default_factory=getDefaultPlotStyle)
    colorGenerator: ColorGenerator | None = None
    bg: str = DEFAULT_PLOT_BG
    fg: str = DEFAULT_PLOT_FG
    x: str = ""
    xLabel: str = ""
    y: list[str] = field(default_factory=list)
    yLabels: list[str] = field(default_factory=list)
    title: str = ""
    scatter3d_default_coord_index: int = DEFAULT_SCATTER_3D_DEFAULT_COORD_INDEX
    scatter3d_x_label: str = ""
    scatter3d_y_label: str = ""
    scatter3d_z_label: str = ""
    triangular_height_factor: float = DEFAULT_CONTOUR_TRIANGULAR_HEIGHT_FACTOR
    triangular_xlim: list[float] = field(
        default_factory=lambda: DEFAULT_CONTOUR_TRIANGULAR_XLIM.copy()
    )
    triangular_ylim: list[float] = field(
        default_factory=lambda: DEFAULT_CONTOUR_TRIANGULAR_YLIM.copy()
    )
    triangular_tick_positions: list[float] = field(
        default_factory=lambda: DEFAULT_CONTOUR_TRIANGULAR_TICK_POSITIONS.copy()
    )
    triangular_tick_length: float = DEFAULT_CONTOUR_TRIANGULAR_TICK_LENGTH
    triangular_elem_labels: list[str] = field(
        default_factory=lambda: DEFAULT_CONTOUR_TRIANGULAR_ELEM_LABELS.copy()
    )
    triangular_colorbar_label: str = DEFAULT_CONTOUR_TRIANGULAR_COLORBAR_LABEL
    triangular_levels: int = DEFAULT_CONTOUR_TRIANGULAR_LEVELS
    triangular_alpha: float = DEFAULT_CONTOUR_TRIANGULAR_ALPHA
    triangular_grid_alpha: float = DEFAULT_TRIANGULAR_GRID_ALPHA
    triangular_grid_line_width: float = DEFAULT_TRIANGULAR_GRID_LINE_WIDTH


def _getDefaultSettings() -> dict:
    try:
        default_path = files("resources.default").joinpath("default_settings.toml")
        with open(str(default_path), "rb") as f:
            return tomllib.load(f)
    except Exception as e:
        _logger.error(f"Failed to load default_settings.toml: {e}")
        raise


def _parseAlgorithm(algo_str: str | None) -> ColorAlgorithm | None:
    if not algo_str:
        return None
    for algo in ColorAlgorithm:
        if algo.value == algo_str:
            return algo
    return None


def _parseThemeColors(
    preset: str | None,
    primary: str | None,
    secondary: str | None,
    settings: "Settings | None" = None,
) -> ThemeColors | None:
    if preset == "custom" and settings:
        custom_primary = settings.get("plot", "custom_primary")
        custom_secondary = settings.get("plot", "custom_secondary")
        if custom_primary:
            return ThemeColors(
                primary=custom_primary,
                secondary=custom_secondary or "#000000",
            )
        return None
    if preset and preset != "custom":
        return ColorPalette.getThemeColors(preset)
    if primary:
        return ThemeColors(
            primary=primary,
            secondary=secondary or "#000000",
        )
    return None


class PlotStyleService:
    def __init__(self) -> None:
        pass

    def buildStyle(
        self, module_config: dict, method_config: dict, settings: "Settings | None"
    ) -> PlotStyle:
        system_style = getDefaultPlotStyle()

        module_colorscheme = module_config.get("colorscheme", {})
        method_colorscheme = method_config.get("colorscheme", {})

        module_algorithm = _parseAlgorithm(module_colorscheme.get("algorithm"))
        method_algorithm_str = method_colorscheme.get("algorithm")
        db_algorithm_str = settings.get("plot", "color_algorithm") if settings else None

        algorithmPriority = (
            _parseAlgorithm(method_algorithm_str)
            or module_algorithm
            or _parseAlgorithm(db_algorithm_str)
            or system_style.algorithm
        )

        module_preset = module_colorscheme.get("preset")
        method_preset = method_colorscheme.get("preset")
        db_preset = settings.get("plot", "colorscheme") if settings else None

        module_primary = module_colorscheme.get("primary")
        method_primary = method_colorscheme.get("primary")
        module_secondary = module_colorscheme.get("secondary")
        method_secondary = method_colorscheme.get("secondary")

        final_theme = (
            _parseThemeColors(method_preset, method_primary, method_secondary, settings)
            or _parseThemeColors(
                module_preset, module_primary, module_secondary, settings
            )
            or _parseThemeColors(db_preset, None, None, settings)
            or system_style.themeColors
        )

        lineStyle = (
            method_colorscheme.get("lineStyle")
            or module_colorscheme.get("lineStyle")
            or (settings.get("plot", "lineStyle") if settings else None)
            or system_style.lineStyle
        )
        marker = (
            method_colorscheme.get("marker")
            or module_colorscheme.get("marker")
            or (settings.get("plot", "marker") if settings else None)
            or system_style.marker
        )
        lineWidth = (
            float(method_colorscheme["lineWidth"])
            if "lineWidth" in method_colorscheme
            else float(module_colorscheme["lineWidth"])
            if "lineWidth" in module_colorscheme
            else (
                float(settings.get("plot", "lineWidth"))
                if settings and settings.get("plot", "lineWidth")
                else None
            )
            or system_style.lineWidth
        )
        markerSize = (
            float(method_colorscheme["markerSize"])
            if "markerSize" in method_colorscheme
            else float(module_colorscheme["markerSize"])
            if "markerSize" in module_colorscheme
            else (
                float(settings.get("plot", "markerSize"))
                if settings and settings.get("plot", "markerSize")
                else None
            )
            or system_style.markerSize
        )
        grid = (
            method_colorscheme.get("grid", NotImplemented)
            if "grid" in method_colorscheme
            else module_colorscheme.get("grid", NotImplemented)
            if "grid" in module_colorscheme
            else (
                settings.get("plot", "grid") == "true"
                if settings and settings.get("plot", "grid")
                else NotImplemented
            )
        )
        if grid is NotImplemented:
            grid = system_style.grid

        gridMode = (
            method_colorscheme.get("gridMode")
            or module_colorscheme.get("gridMode")
            or (settings.get("plot", "gridMode") if settings else None)
            or system_style.gridMode
        )

        gridDensity = (
            float(method_colorscheme["gridDensity"])
            if "gridDensity" in method_colorscheme
            else float(module_colorscheme["gridDensity"])
            if "gridDensity" in module_colorscheme
            else (
                float(settings.get("plot", "gridDensity"))
                if settings and settings.get("plot", "gridDensity")
                else None
            )
            or system_style.gridDensity
        )

        gridLabelDensity = (
            float(method_colorscheme["gridLabelDensity"])
            if "gridLabelDensity" in method_colorscheme
            else float(module_colorscheme["gridLabelDensity"])
            if "gridLabelDensity" in module_colorscheme
            else (
                float(settings.get("plot", "gridLabelDensity"))
                if settings and settings.get("plot", "gridLabelDensity")
                else None
            )
            or system_style.gridLabelDensity
        )

        titleFontSize = (
            int(method_colorscheme["titleFontSize"])
            if "titleFontSize" in method_colorscheme
            else int(module_colorscheme["titleFontSize"])
            if "titleFontSize" in module_colorscheme
            else (
                int(settings.get("plot", "titleFontSize"))
                if settings and settings.get("plot", "titleFontSize")
                else None
            )
            or system_style.titleFontSize
        )

        labelFontSize = (
            int(method_colorscheme["labelFontSize"])
            if "labelFontSize" in method_colorscheme
            else int(module_colorscheme["labelFontSize"])
            if "labelFontSize" in module_colorscheme
            else (
                int(settings.get("plot", "labelFontSize"))
                if settings and settings.get("plot", "labelFontSize")
                else None
            )
            or system_style.labelFontSize
        )

        tickFontSize = (
            int(method_colorscheme["tickFontSize"])
            if "tickFontSize" in method_colorscheme
            else int(module_colorscheme["tickFontSize"])
            if "tickFontSize" in module_colorscheme
            else (
                int(settings.get("plot", "tickFontSize"))
                if settings and settings.get("plot", "tickFontSize")
                else None
            )
            or system_style.tickFontSize
        )

        legendFontSize = (
            int(method_colorscheme["legendFontSize"])
            if "legendFontSize" in method_colorscheme
            else int(module_colorscheme["legendFontSize"])
            if "legendFontSize" in module_colorscheme
            else (
                int(settings.get("plot", "legendFontSize"))
                if settings and settings.get("plot", "legendFontSize")
                else None
            )
            or system_style.legendFontSize
        )

        return PlotStyle(
            algorithm=algorithmPriority,
            themeColors=final_theme,
            lineStyle=lineStyle,
            marker=marker,
            lineWidth=lineWidth,
            markerSize=markerSize,
            grid=grid,
            gridMode=gridMode,
            gridDensity=gridDensity,
            gridLabelDensity=gridLabelDensity,
            titleFontSize=titleFontSize,
            labelFontSize=labelFontSize,
            tickFontSize=tickFontSize,
            legendFontSize=legendFontSize,
        )

    def buildConfig(
        self, module_config: dict, method_config: dict, settings: "Settings | None"
    ) -> PlotStyleConfig:
        plot_config = method_config.get("plot", {})
        module_plot_config = module_config.get("plot", {})
        global_plot = _getDefaultSettings().get("plot", {})
        style = self.buildStyle(module_config, method_config, settings)
        theme = style.themeColors or ColorPalette.getThemeColors(DEFAULT_THEME_PRESET)
        generator = ColorGenerator(theme, style.algorithm)

        scatter3d_global = global_plot.get("scatter_3d", {})
        triangular_global = global_plot.get("contour_triangular", {})

        scatter3d_default_coord_index = (
            plot_config.get("default_coord_index")
            or module_plot_config.get("default_coord_index")
            or scatter3d_global.get("default_coord_index")
            or DEFAULT_SCATTER_3D_DEFAULT_COORD_INDEX
        )
        scatter3d_x_label = (
            plot_config.get("xLabel")
            or module_plot_config.get("xLabel")
            or scatter3d_global.get("xLabel")
            or ""
        )
        scatter3d_y_label = (
            plot_config.get("yLabel")
            or module_plot_config.get("yLabel")
            or scatter3d_global.get("yLabel")
            or ""
        )
        scatter3d_z_label = (
            plot_config.get("zLabel")
            or module_plot_config.get("zLabel")
            or scatter3d_global.get("zLabel")
            or ""
        )
        triangular_height_factor = (
            plot_config.get("height_factor")
            or module_plot_config.get("height_factor")
            or triangular_global.get("height_factor")
            or DEFAULT_CONTOUR_TRIANGULAR_HEIGHT_FACTOR
        )
        triangular_xlim = (
            plot_config.get("xlim")
            or module_plot_config.get("xlim")
            or triangular_global.get("xlim")
            or DEFAULT_CONTOUR_TRIANGULAR_XLIM
        )
        triangular_ylim = (
            plot_config.get("ylim")
            or module_plot_config.get("ylim")
            or triangular_global.get("ylim")
            or DEFAULT_CONTOUR_TRIANGULAR_YLIM
        )
        triangular_tick_positions = (
            plot_config.get("tick_positions")
            or module_plot_config.get("tick_positions")
            or triangular_global.get("tick_positions")
            or DEFAULT_CONTOUR_TRIANGULAR_TICK_POSITIONS
        )
        triangular_tick_length = (
            plot_config.get("tick_length")
            or module_plot_config.get("tick_length")
            or triangular_global.get("tick_length")
            or DEFAULT_CONTOUR_TRIANGULAR_TICK_LENGTH
        )
        triangular_elem_labels = (
            plot_config.get("elem_labels")
            or module_plot_config.get("elem_labels")
            or triangular_global.get("elem_labels")
            or DEFAULT_CONTOUR_TRIANGULAR_ELEM_LABELS
        )
        triangular_colorbar_label = (
            plot_config.get("colorbar_label")
            or module_plot_config.get("colorbar_label")
            or triangular_global.get("colorbar_label")
            or DEFAULT_CONTOUR_TRIANGULAR_COLORBAR_LABEL
        )
        triangular_levels = (
            plot_config.get("levels")
            or module_plot_config.get("levels")
            or (
                str(settings.plot_triangular_levels)
                if settings and settings.plot_triangular_levels is not None
                else None
            )
            or DEFAULT_CONTOUR_TRIANGULAR_LEVELS
        )

        triangular_alpha = (
            plot_config.get("alpha")
            or module_plot_config.get("alpha")
            or (
                str(settings.plot_triangular_alpha)
                if settings and settings.plot_triangular_alpha is not None
                else None
            )
            or DEFAULT_CONTOUR_TRIANGULAR_ALPHA
        )

        triangular_grid_alpha = (
            plot_config.get("grid_alpha")
            or module_plot_config.get("grid_alpha")
            or (
                str(settings.plot_triangular_grid_alpha)
                if settings and settings.plot_triangular_grid_alpha is not None
                else None
            )
            or DEFAULT_TRIANGULAR_GRID_ALPHA
        )

        triangular_grid_line_width = (
            plot_config.get("grid_line_width")
            or module_plot_config.get("grid_line_width")
            or (
                str(settings.plot_triangular_grid_line_width)
                if settings and settings.plot_triangular_grid_line_width is not None
                else None
            )
            or DEFAULT_TRIANGULAR_GRID_LINE_WIDTH
        )

        bg = (
            plot_config.get("bg")
            or module_plot_config.get("bg")
            or (settings.plot_bg if settings else None)
            or DEFAULT_PLOT_BG
        )
        fg = (
            plot_config.get("fg")
            or module_plot_config.get("fg")
            or (settings.plot_fg if settings else None)
            or DEFAULT_PLOT_FG
        )

        return PlotStyleConfig(
            plotType=plot_config.get("plotType", DEFAULT_PLOT_TYPE),
            style=style,
            colorGenerator=generator,
            bg=bg,
            fg=fg,
            x=plot_config.get("x", ""),
            xLabel=plot_config.get("xLabel", ""),
            y=plot_config.get("y", []),
            yLabels=plot_config.get("yLabels", []),
            title=plot_config.get("title", ""),
            scatter3d_default_coord_index=scatter3d_default_coord_index,
            scatter3d_x_label=scatter3d_x_label,
            scatter3d_y_label=scatter3d_y_label,
            scatter3d_z_label=scatter3d_z_label,
            triangular_height_factor=triangular_height_factor,
            triangular_xlim=triangular_xlim,
            triangular_ylim=triangular_ylim,
            triangular_tick_positions=triangular_tick_positions,
            triangular_tick_length=triangular_tick_length,
            triangular_elem_labels=triangular_elem_labels,
            triangular_colorbar_label=triangular_colorbar_label,
            triangular_levels=int(triangular_levels),
            triangular_alpha=float(triangular_alpha),
            triangular_grid_alpha=float(triangular_grid_alpha),
            triangular_grid_line_width=float(triangular_grid_line_width),
        )
