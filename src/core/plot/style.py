from dataclasses import dataclass

from catalog import (
    DEFAULT_THEME_PRESET,
    DEFAULT_GRID,
    DEFAULT_GRID_MODE,
    DEFAULT_GRID_DENSITY,
    DEFAULT_GRID_LABEL_DENSITY,
    DEFAULT_LINE_STYLE,
    DEFAULT_LINE_WIDTH,
    DEFAULT_MARKER,
    DEFAULT_MARKER_SIZE,
    ColorAlgorithm,
)

from core.plot.color import ColorPalette, ThemeColors

DEFAULT_TITLE_FONT_SIZE = 14
DEFAULT_LABEL_FONT_SIZE = 12
DEFAULT_TICK_FONT_SIZE = 10
DEFAULT_LEGEND_FONT_SIZE = 10


@dataclass(frozen=True)
class PlotStyle:
    algorithm: ColorAlgorithm = ColorAlgorithm.LINEAR
    themeColors: ThemeColors | None = None
    lineStyle: str = DEFAULT_LINE_STYLE
    marker: str = DEFAULT_MARKER
    lineWidth: float = DEFAULT_LINE_WIDTH
    markerSize: float = DEFAULT_MARKER_SIZE
    grid: bool = DEFAULT_GRID
    gridMode: str = DEFAULT_GRID_MODE
    gridDensity: float = DEFAULT_GRID_DENSITY
    gridLabelDensity: float = DEFAULT_GRID_LABEL_DENSITY
    titleFontSize: int = DEFAULT_TITLE_FONT_SIZE
    labelFontSize: int = DEFAULT_LABEL_FONT_SIZE
    tickFontSize: int = DEFAULT_TICK_FONT_SIZE
    legendFontSize: int = DEFAULT_LEGEND_FONT_SIZE


def getDefaultPlotStyle() -> PlotStyle:
    return PlotStyle(
        algorithm=ColorAlgorithm.LINEAR,
        themeColors=ColorPalette.getThemeColors(DEFAULT_THEME_PRESET),
        lineStyle=DEFAULT_LINE_STYLE,
        marker=DEFAULT_MARKER,
        lineWidth=DEFAULT_LINE_WIDTH,
        markerSize=DEFAULT_MARKER_SIZE,
        grid=DEFAULT_GRID,
        gridMode=DEFAULT_GRID_MODE,
        gridDensity=DEFAULT_GRID_DENSITY,
        gridLabelDensity=DEFAULT_GRID_LABEL_DENSITY,
        titleFontSize=DEFAULT_TITLE_FONT_SIZE,
        labelFontSize=DEFAULT_LABEL_FONT_SIZE,
        tickFontSize=DEFAULT_TICK_FONT_SIZE,
        legendFontSize=DEFAULT_LEGEND_FONT_SIZE,
    )
