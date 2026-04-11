from dataclasses import dataclass

from catalog import (
    DEFAULT_THEME_PRESET,
    DEFAULT_FONT_SIZE,
    DEFAULT_GRID,
    DEFAULT_LINE_STYLE,
    DEFAULT_LINE_WIDTH,
    DEFAULT_MARKER,
    DEFAULT_MARKER_SIZE,
    ColorAlgorithm,
)

from core.plot.color import ColorPalette, ThemeColors


@dataclass(frozen=True)
class PlotStyle:
    algorithm: ColorAlgorithm = ColorAlgorithm.LINEAR
    themeColors: ThemeColors | None = None
    lineStyle: str = DEFAULT_LINE_STYLE
    marker: str = DEFAULT_MARKER
    lineWidth: float = DEFAULT_LINE_WIDTH
    markerSize: float = DEFAULT_MARKER_SIZE
    grid: bool = DEFAULT_GRID
    fontSize: int = DEFAULT_FONT_SIZE


def getDefaultPlotStyle() -> PlotStyle:
    return PlotStyle(
        algorithm=ColorAlgorithm.LINEAR,
        themeColors=ColorPalette.getThemeColors(DEFAULT_THEME_PRESET),
        lineStyle=DEFAULT_LINE_STYLE,
        marker=DEFAULT_MARKER,
        lineWidth=DEFAULT_LINE_WIDTH,
        markerSize=DEFAULT_MARKER_SIZE,
        grid=DEFAULT_GRID,
        fontSize=DEFAULT_FONT_SIZE,
    )
