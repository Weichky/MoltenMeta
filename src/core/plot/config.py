from __future__ import annotations
from dataclasses import dataclass, field
from importlib.resources import files
from typing import TYPE_CHECKING

import tomllib

from catalog import (
    DEFAULT_FONT_SIZE,
    DEFAULT_GRID,
    DEFAULT_LINE_STYLE,
    DEFAULT_LINE_WIDTH,
    DEFAULT_MARKER,
    DEFAULT_MARKER_SIZE,
    DEFAULT_PLOT_TYPE,
)

from core.plot.color import ColorPalette
from core.plot.style import PlotStyle, getDefaultPlotStyle

if TYPE_CHECKING:
    from domain.settings import Settings


@dataclass(frozen=True)
class PlotStyleConfig:
    plotType: str = DEFAULT_PLOT_TYPE
    style: PlotStyle = field(default_factory=getDefaultPlotStyle)
    x: str = ""
    xLabel: str = ""
    y: list[str] = field(default_factory=list)
    yLabels: list[str] = field(default_factory=list)
    title: str = ""


def _getDefaultSettings() -> dict:
    try:
        default_path = files("resources.default").joinpath("default_settings.toml")
        with open(str(default_path), "rb") as f:
            return tomllib.load(f)
    except Exception:
        return {}


class PlotStyleService:
    def __init__(self) -> None:
        pass

    def buildStyle(self, module_config: dict, settings: "Settings | None") -> PlotStyle:
        db_colorscheme = settings.get("plot", "colorscheme") if settings else None
        db_style = self._getStyleFromDb(settings)

        system_style = getDefaultPlotStyle()
        user_style = self._buildUserStyle(db_colorscheme, db_style)

        module_palette = module_config.get("colorscheme", {}).get("colors")
        module_lineStyle = module_config.get("lineStyle")
        module_marker = module_config.get("marker")
        module_lineWidth = module_config.get("lineWidth")
        module_markerSize = module_config.get("markerSize")
        module_grid = module_config.get("grid")
        module_fontSize = module_config.get("fontSize")

        final_colors = (
            module_palette
            or (ColorPalette.getColors(db_colorscheme) if db_colorscheme else None)
            or user_style.colors
            or system_style.colors
        )
        final_lineStyle = (
            module_lineStyle or user_style.lineStyle or system_style.lineStyle
        )
        final_marker = module_marker or user_style.marker or system_style.marker
        final_lineWidth = (
            float(module_lineWidth)
            if module_lineWidth is not None
            else user_style.lineWidth or system_style.lineWidth
        )
        final_markerSize = (
            float(module_markerSize)
            if module_markerSize is not None
            else user_style.markerSize or system_style.markerSize
        )
        final_grid = (
            module_grid
            if module_grid is not None
            else user_style.grid
            if user_style.grid is not None
            else system_style.grid
        )
        final_fontSize = (
            int(module_fontSize)
            if module_fontSize is not None
            else user_style.fontSize or system_style.fontSize
        )

        return PlotStyle(
            colors=final_colors,
            lineStyle=final_lineStyle,
            marker=final_marker,
            lineWidth=final_lineWidth,
            markerSize=final_markerSize,
            grid=final_grid,
            fontSize=final_fontSize,
        )

    def buildConfig(
        self, module_config: dict, method_config: dict, settings: "Settings | None"
    ) -> PlotStyleConfig:
        plot_config = method_config.get("plot", {})
        style = self.buildStyle(plot_config, settings)

        return PlotStyleConfig(
            plotType=plot_config.get("plotType", DEFAULT_PLOT_TYPE),
            style=style,
            x=plot_config.get("x", ""),
            xLabel=plot_config.get("xLabel", ""),
            y=plot_config.get("y", []),
            yLabels=plot_config.get("yLabels", []),
            title=plot_config.get("title", ""),
        )

    def _getStyleFromDb(self, settings: "Settings | None") -> PlotStyle | None:
        if settings is None:
            return None
        colors = []
        for i in range(8):
            c = settings.get("plot", f"color_{i}")
            if c:
                colors.append(c)
        lineStyle = settings.get("plot", "lineStyle")
        marker = settings.get("plot", "marker")
        lineWidth = settings.get("plot", "lineWidth")
        markerSize = settings.get("plot", "markerSize")
        grid = settings.get("plot", "grid")
        fontSize = settings.get("plot", "fontSize")

        if not any([colors, lineStyle, marker, lineWidth, markerSize, grid, fontSize]):
            return None

        return PlotStyle(
            colors=colors,
            lineStyle=lineStyle or DEFAULT_LINE_STYLE,
            marker=marker or DEFAULT_MARKER,
            lineWidth=float(lineWidth) if lineWidth else DEFAULT_LINE_WIDTH,
            markerSize=float(markerSize) if markerSize else DEFAULT_MARKER_SIZE,
            grid=grid == "true" if grid else DEFAULT_GRID,
            fontSize=int(fontSize) if fontSize else DEFAULT_FONT_SIZE,
        )

    def _buildUserStyle(
        self, colorscheme: str | None, db_style: PlotStyle | None
    ) -> PlotStyle:
        if db_style and db_style.colors:
            return db_style
        if colorscheme:
            return PlotStyle(colors=ColorPalette.getColors(colorscheme))
        return getDefaultPlotStyle()
