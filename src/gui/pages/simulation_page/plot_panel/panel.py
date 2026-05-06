import logging
from typing import TYPE_CHECKING

from PySide6 import QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib as mpl
import numpy as np

from core.plot.latex_utils import wrap_latex
from catalog.plot_style import (
    DEFAULT_FIGURE_SIZE,
    DEFAULT_SUBPLOT_INDEX,
    DEFAULT_LAYOUT_MARGINS,
    DEFAULT_SINGLE_POINT_SIZE,
    DEFAULT_ZORDER,
    DEFAULT_SCATTER_3D_ALPHA,
    DEFAULT_CONTOUR_ALPHA,
    DEFAULT_CONTOUR_LINE_WIDTH,
    DEFAULT_COLORMAP_RESOLUTION,
    DEFAULT_Z_EDGE_EPSILON,
    DEFAULT_NORMALIZED_EPSILON,
)

from .grid import applyGridToAxis, applyGrid3D
from .triangular import renderTriangularContour
from .utils import resolveLabels

if TYPE_CHECKING:
    from core.plot.config import PlotStyleConfig

logging.getLogger("matplotlib").setLevel(logging.WARNING)


class PlotPanel(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        mpl.rcParams["text.usetex"] = False
        self._figure = Figure(figsize=DEFAULT_FIGURE_SIZE)
        self._canvas = FigureCanvasQTAgg(self._figure)
        self._ax = self._figure.add_subplot(DEFAULT_SUBPLOT_INDEX)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(*DEFAULT_LAYOUT_MARGINS)
        layout.addWidget(self._canvas)
        self._current_bg = None
        self._current_fg = None

    def applyPlaceholder(
        self, grid: bool, gridMode: str, gridDensity: float, gridLabelDensity: float
    ) -> None:
        applyGridToAxis(self._ax, grid, gridMode, gridDensity, gridLabelDensity)
        self._canvas.draw()

    def setColors(self, bg: str, fg: str) -> None:
        # Track current colors to avoid redundant color application.
        # Stored for potential future use (e.g., theme comparison).
        self._current_bg = bg
        self._current_fg = fg
        # Apply bg to figure background and axis face.
        self._figure.set_facecolor(bg)
        self._ax.set_facecolor(bg)
        # Apply fg to all axis text elements (labels, title, ticks, spines).
        self._ax.xaxis.label.set_color(fg)
        self._ax.yaxis.label.set_color(fg)
        self._ax.title.set_color(fg)
        self._ax.spines["bottom"].set_color(fg)
        self._ax.spines["top"].set_color(fg)
        self._ax.spines["left"].set_color(fg)
        self._ax.spines["right"].set_color(fg)
        self._ax.tick_params(axis="x", colors=fg)
        self._ax.tick_params(axis="y", colors=fg)
        # For 3D axes, also set z-axis colors and pane backgrounds.
        if hasattr(self._ax, "zaxis"):
            self._ax.zaxis.label.set_color(fg)
            self._ax.tick_params(axis="z", colors=fg)
            self._ax.xaxis.pane.fill = False
            self._ax.yaxis.pane.fill = False
            self._ax.zaxis.pane.fill = False
            self._ax.xaxis.pane.set_facecolor(bg)
            self._ax.yaxis.pane.set_facecolor(bg)
            self._ax.zaxis.pane.set_facecolor(bg)

    def plot(
        self,
        config: "PlotStyleConfig",
        x_data: list[float],
        y_data: list[float],
        x_label: str | None = None,
        y_label: str | None = None,
    ) -> None:
        # Lifecycle pattern: clear figure BEFORE adding new axis.
        # figure.clear() removes all axes from the figure.
        # add_subplot() then creates a fresh axis.
        # This avoids axes accumulation that would occur if we only called ax.clear().
        self._figure.clear()
        self._ax = self._figure.add_subplot(DEFAULT_SUBPLOT_INDEX)
        style = config.style
        generator = config.colorGenerator
        self._ax.clear()
        self.setColors(config.bg, config.fg)
        color = generator.getColor(0, 1) if generator else style.themeColors.primary
        self._ax.plot(
            x_data,
            y_data,
            marker=style.marker,
            color=color,
            linewidth=style.lineWidth,
            linestyle=style.lineStyle,
            markersize=style.markerSize,
        )
        final_x_label, final_y_label = resolveLabels(x_label, y_label, config)
        self._ax.set_xlabel(wrap_latex(final_x_label), fontsize=style.labelFontSize)
        self._ax.set_ylabel(
            wrap_latex(final_y_label),
            fontsize=style.labelFontSize,
        )
        if config.title:
            self._ax.set_title(wrap_latex(config.title), fontsize=style.titleFontSize)
        self._ax.tick_params(axis="both", labelsize=style.tickFontSize)
        applyGridToAxis(
            self._ax,
            style.grid,
            style.gridMode,
            style.gridDensity,
            style.gridLabelDensity,
        )
        self._canvas.draw()

    def plotSinglePoint(
        self,
        config: "PlotStyleConfig",
        x: float,
        y: float,
        x_label: str | None = None,
        y_label: str | None = None,
    ) -> None:
        self._figure.clear()
        self._ax = self._figure.add_subplot(DEFAULT_SUBPLOT_INDEX)
        style = config.style
        generator = config.colorGenerator
        self._ax.clear()
        self.setColors(config.bg, config.fg)
        color = generator.getColor(0, 1) if generator else style.themeColors.primary
        self._ax.scatter(
            [x],
            [y],
            color=color,
            s=DEFAULT_SINGLE_POINT_SIZE,
            zorder=DEFAULT_ZORDER,
            marker=style.marker,
        )
        final_x_label, final_y_label = resolveLabels(x_label, y_label, config)
        self._ax.set_xlabel(wrap_latex(final_x_label), fontsize=style.labelFontSize)
        self._ax.set_ylabel(
            wrap_latex(final_y_label),
            fontsize=style.labelFontSize,
        )
        if config.title:
            self._ax.set_title(wrap_latex(config.title), fontsize=style.titleFontSize)
        self._ax.tick_params(axis="both", labelsize=style.tickFontSize)
        applyGridToAxis(
            self._ax,
            style.grid,
            style.gridMode,
            style.gridDensity,
            style.gridLabelDensity,
        )
        self._canvas.draw()

    def clear(self) -> None:
        self._ax.clear()
        self._canvas.draw()

    def scatter_3d(
        self,
        config: "PlotStyleConfig",
        x_data: list[float],
        y_data: list[float],
        z_data: list[float],
        x_label: str | None = None,
        y_label: str | None = None,
        z_label: str | None = None,
        title: str | None = None,
    ) -> None:
        self._figure.clear()
        self._ax = self._figure.add_subplot(DEFAULT_SUBPLOT_INDEX, projection="3d")
        self.setColors(config.bg, config.fg)

        style = config.style
        generator = config.colorGenerator
        color = generator.getColor(0, 1) if generator else style.themeColors.primary

        self._ax.scatter(
            x_data,
            y_data,
            z_data,
            color=color,
            s=style.markerSize,
            marker=style.marker,
            alpha=DEFAULT_SCATTER_3D_ALPHA,
        )

        self._ax.set_xlabel(wrap_latex(x_label or "x"), fontsize=style.labelFontSize)
        self._ax.set_ylabel(wrap_latex(y_label or "y"), fontsize=style.labelFontSize)
        self._ax.set_zlabel(wrap_latex(z_label or "z"), fontsize=style.labelFontSize)

        if title:
            self._ax.set_title(wrap_latex(title), fontsize=style.titleFontSize)

        self._ax.tick_params(axis="both", labelsize=style.tickFontSize)
        self._ax.tick_params(axis="z", labelsize=style.tickFontSize)
        applyGridToAxis(
            self._ax,
            style.grid,
            style.gridMode,
            style.gridDensity,
            style.gridLabelDensity,
        )
        applyGrid3D(
            self._ax,
            style.grid,
            style.gridMode,
            style.gridDensity,
            style.gridLabelDensity,
        )

        self._canvas.draw()

    def contourf(
        self,
        config: "PlotStyleConfig",
        x_mesh: list[list[float]],
        y_mesh: list[list[float]],
        z_mesh: list[list[float]],
        x_label: str | None = None,
        y_label: str | None = None,
        title: str | None = None,
        levels: int = 20,
    ) -> None:
        self._figure.clear()
        self._ax = self._figure.add_subplot(DEFAULT_SUBPLOT_INDEX)
        self._ax.clear()
        self.setColors(config.bg, config.fg)

        style = config.style
        generator = config.colorGenerator

        x_arr = np.array(x_mesh)
        y_arr = np.array(y_mesh)
        z_arr = np.array(z_mesh)

        z_min = np.nanmin(z_arr)
        z_max = np.nanmax(z_arr)
        if z_min == z_max:
            z_min = z_min - DEFAULT_Z_EDGE_EPSILON
            z_max = z_max + DEFAULT_Z_EDGE_EPSILON

        # Normalize Z to [0,1] for the custom colormap.
        # When z_min == z_max, the normalized value would be 0.5 everywhere,
        # so we shift the range by epsilon to avoid a flat color.
        if generator:
            n_cmap = DEFAULT_COLORMAP_RESOLUTION
            cmap_colors = [
                generator.getColorAt(i / (n_cmap - 1)) for i in range(n_cmap)
            ]
            cmap = mpl.colors.ListedColormap(cmap_colors)
            z_norm = (z_arr - z_min) / (z_max - z_min + DEFAULT_NORMALIZED_EPSILON)
            cf = self._ax.contourf(
                x_arr,
                y_arr,
                z_norm,
                levels=np.linspace(0, 1, levels),
                cmap=cmap,
                alpha=DEFAULT_CONTOUR_ALPHA,
                extend="neither",
            )
            for i, level in enumerate(np.linspace(0, 1, levels)):
                color = generator.getColorAt(level)
                self._ax.contour(
                    x_arr,
                    y_arr,
                    z_norm,
                    levels=[level],
                    colors=[color],
                    linewidths=DEFAULT_CONTOUR_LINE_WIDTH,
                )
        else:
            contour_levels = np.linspace(z_min, z_max, levels)
            cf = self._ax.contourf(
                x_arr,
                y_arr,
                z_arr,
                levels=contour_levels,
                cmap="viridis",
                alpha=DEFAULT_CONTOUR_ALPHA,
            )

        cbar = self._figure.colorbar(cf, ax=self._ax)
        cbar.set_label(wrap_latex("Z_ABC"), fontsize=style.labelFontSize)

        self._ax.set_xlabel(wrap_latex(x_label or "x"), fontsize=style.labelFontSize)
        self._ax.set_ylabel(wrap_latex(y_label or "y"), fontsize=style.labelFontSize)

        if title:
            self._ax.set_title(wrap_latex(title), fontsize=style.titleFontSize)

        self._ax.set_xlim(0, 1)
        self._ax.set_ylim(0, 1)
        self._ax.tick_params(axis="both", labelsize=style.tickFontSize)
        applyGridToAxis(
            self._ax,
            style.grid,
            style.gridMode,
            style.gridDensity,
            style.gridLabelDensity,
        )

        self._canvas.draw()

    def contour_triangular(
        self,
        config: "PlotStyleConfig",
        values: list[dict],
        conditions: dict | None = None,
        title: str | None = None,
        z_label: str | None = None,
        levels: int | None = None,
        plane: str = "x_A-x_B",
    ) -> None:
        self._figure.clear()
        self._ax = self._figure.add_subplot(DEFAULT_SUBPLOT_INDEX)
        self.setColors(config.bg, config.fg)

        renderTriangularContour(
            self._figure,
            self._ax,
            config,
            values,
            conditions,
            title,
            z_label,
            levels,
            plane,
        )

        self._canvas.draw()
