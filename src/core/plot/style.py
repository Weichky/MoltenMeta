from dataclasses import dataclass, field

from catalog import (
    DEFAULT_COLOR_SCHEME,
    DEFAULT_FONT_SIZE,
    DEFAULT_GRID,
    DEFAULT_LINE_STYLE,
    DEFAULT_LINE_WIDTH,
    DEFAULT_MARKER,
    DEFAULT_MARKER_SIZE,
)


@dataclass(frozen=True)
class PlotStyle:
    colors: list[str] = field(default_factory=list)
    lineStyle: str = DEFAULT_LINE_STYLE
    marker: str = DEFAULT_MARKER
    lineWidth: float = DEFAULT_LINE_WIDTH
    markerSize: float = DEFAULT_MARKER_SIZE
    grid: bool = DEFAULT_GRID
    fontSize: int = DEFAULT_FONT_SIZE


def getDefaultPlotStyle() -> PlotStyle:
    from core.plot.color import ColorPalette

    return PlotStyle(
        colors=ColorPalette.getColors(DEFAULT_COLOR_SCHEME),
        lineStyle=DEFAULT_LINE_STYLE,
        marker=DEFAULT_MARKER,
        lineWidth=DEFAULT_LINE_WIDTH,
        markerSize=DEFAULT_MARKER_SIZE,
        grid=DEFAULT_GRID,
        fontSize=DEFAULT_FONT_SIZE,
    )
