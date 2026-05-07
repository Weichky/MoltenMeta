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
    DEFAULT_TRIANGULAR_COORD_FACTOR,
    DEFAULT_CONTOUR_TRIANGULAR_HEIGHT_FACTOR,
    DEFAULT_TICK_LINE_WIDTH,
    DEFAULT_COLORBAR_TICK_COUNT,
    DEFAULT_CONTOUR_TRIANGULAR_TICK_LENGTH,
    DEFAULT_SINGLE_TICK_LABEL_OFFSET,
    DEFAULT_ELEMENT_LABEL_OFFSET,
    DEFAULT_APEX_LABEL_OFFSET,
    DEFAULT_LABEL_DISTANCE,
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

    def exportImage(self, file_path: str, format: str, dpi: int = 300) -> None:
        self._figure.savefig(
            file_path,
            format=format,
            dpi=dpi,
            facecolor=self._current_bg or "white",
            edgecolor="none",
            bbox_inches="tight",
        )

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

    def surface_3d(
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

        if generator:
            n_cmap = DEFAULT_COLORMAP_RESOLUTION
            cmap_colors = [
                generator.getColorAt(i / (n_cmap - 1)) for i in range(n_cmap)
            ]
            cmap = mpl.colors.ListedColormap(cmap_colors)
        else:
            cmap = style.colormap if hasattr(style, "colormap") else "viridis"

        self._ax.plot_trisurf(
            x_data,
            y_data,
            z_data,
            cmap=cmap,
            alpha=DEFAULT_SCATTER_3D_ALPHA,
            linewidth=style.grid_line_width
            if hasattr(style, "grid_line_width")
            else 0.5,
            antialiased=True,
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

    def _drawTriangularFrame3D(
        self,
        elem_labels: list[str],
        plane: str,
        h: float,
        style,
    ) -> None:
        factor = DEFAULT_TRIANGULAR_COORD_FACTOR

        if plane == "x_A-x_B":
            pts_a = np.array([factor, h, 0])
            pts_b = np.array([0, 0, 0])
            pts_c = np.array([1, 0, 0])
        elif plane == "x_A-x_C":
            pts_a = np.array([factor, h, 0])
            pts_b = np.array([1, 0, 0])
            pts_c = np.array([0, 0, 0])
        elif plane == "x_B-x_C":
            pts_a = np.array([0, 0, 0])
            pts_b = np.array([1, 0, 0])
            pts_c = np.array([factor, h, 0])
        else:
            pts_a = np.array([factor, h, 0])
            pts_b = np.array([0, 0, 0])
            pts_c = np.array([1, 0, 0])

        self._ax.plot(
            [pts_b[0], pts_c[0]],
            [pts_b[1], pts_c[1]],
            [0, 0],
            "k-",
            linewidth=style.grid_line_width
            if hasattr(style, "grid_line_width")
            else 1.0,
        )
        self._ax.plot(
            [pts_a[0], pts_c[0]],
            [pts_a[1], pts_c[1]],
            [0, 0],
            "k-",
            linewidth=style.grid_line_width
            if hasattr(style, "grid_line_width")
            else 1.0,
        )
        self._ax.plot(
            [pts_a[0], pts_b[0]],
            [pts_a[1], pts_b[1]],
            [0, 0],
            "k-",
            linewidth=style.grid_line_width
            if hasattr(style, "grid_line_width")
            else 1.0,
        )

        self._ax.plot(
            [pts_a[0], pts_a[0]],
            [pts_a[1], pts_a[1]],
            [0, 1],
            "k-",
            linewidth=style.grid_line_width
            if hasattr(style, "grid_line_width")
            else 1.0,
        )
        self._ax.plot(
            [pts_b[0], pts_b[0]],
            [pts_b[1], pts_b[1]],
            [0, 1],
            "k-",
            linewidth=style.grid_line_width
            if hasattr(style, "grid_line_width")
            else 1.0,
        )
        self._ax.plot(
            [pts_c[0], pts_c[0]],
            [pts_c[1], pts_c[1]],
            [0, 1],
            "k-",
            linewidth=style.grid_line_width
            if hasattr(style, "grid_line_width")
            else 1.0,
        )

    def surface_3d_triangular(
        self,
        config: "PlotStyleConfig",
        values: list[dict],
        conditions: dict | None = None,
        title: str | None = None,
        z_label: str | None = None,
        plane: str = "x_A-x_B",
    ) -> None:
        self._figure.clear()
        self._ax = self._figure.add_subplot(DEFAULT_SUBPLOT_INDEX, projection="3d")
        self.setColors(config.bg, config.fg)

        style = config.style
        h = (
            config.triangular_height_factor
            if hasattr(config, "triangular_height_factor")
            else DEFAULT_CONTOUR_TRIANGULAR_HEIGHT_FACTOR
        )

        if conditions:
            elem_labels = [
                conditions.get("elem_A", "A"),
                conditions.get("elem_B", "B"),
                conditions.get("elem_C", "C"),
            ]
            plane = conditions.get("plane", plane)
        else:
            elem_labels = (
                config.triangular_elem_labels
                if hasattr(config, "triangular_elem_labels")
                else ["A", "B", "C"]
            )

        x_A_arr = np.array([v.get("x_A", 0) for v in values])
        x_B_arr = np.array([v.get("x_B", 0) for v in values])
        x_C_arr = np.array([v.get("x_C", 0) for v in values])
        z_key = next((k for k in values[0] if k not in ("x_A", "x_B", "x_C")), "Z_ABC")
        z_arr = np.array([v.get(z_key, 0) for v in values])

        valid_mask = (
            ~np.isnan(z_arr)
            & (x_A_arr >= 0)
            & (x_A_arr <= 1)
            & (x_B_arr >= 0)
            & (x_B_arr <= 1)
            & (x_C_arr >= 0)
            & (x_C_arr <= 1)
        )

        x_A_valid = x_A_arr[valid_mask]
        x_B_valid = x_B_arr[valid_mask]
        x_C_valid = x_C_arr[valid_mask]
        z_valid = z_arr[valid_mask]

        if plane == "x_A-x_B":
            x_cart = x_C_valid + DEFAULT_TRIANGULAR_COORD_FACTOR * x_A_valid
            y_cart = h * x_A_valid
        elif plane == "x_A-x_C":
            x_cart = x_B_valid + DEFAULT_TRIANGULAR_COORD_FACTOR * x_A_valid
            y_cart = h * x_A_valid
        elif plane == "x_B-x_C":
            x_cart = x_A_valid + DEFAULT_TRIANGULAR_COORD_FACTOR * x_B_valid
            y_cart = h * x_B_valid
        else:
            x_cart = x_C_valid + DEFAULT_TRIANGULAR_COORD_FACTOR * x_A_valid
            y_cart = h * x_A_valid

        generator = config.colorGenerator
        if generator:
            n_cmap = DEFAULT_COLORMAP_RESOLUTION
            cmap_colors = [
                generator.getColorAt(i / (n_cmap - 1)) for i in range(n_cmap)
            ]
            cmap = mpl.colors.ListedColormap(cmap_colors)
        else:
            cmap = style.colormap if hasattr(style, "colormap") else "viridis"

        z_min = np.min(z_valid)
        z_max = np.max(z_valid)
        if z_max > z_min:
            z_display = (z_valid - z_min) / (z_max - z_min)
        else:
            z_display = np.zeros_like(z_valid)

        self._ax.plot_trisurf(
            x_cart,
            y_cart,
            z_display,
            cmap=cmap,
            alpha=DEFAULT_SCATTER_3D_ALPHA,
            linewidth=0.5,
            antialiased=True,
        )

        h = (
            config.triangular_height_factor
            if hasattr(config, "triangular_height_factor")
            else DEFAULT_CONTOUR_TRIANGULAR_HEIGHT_FACTOR
        )

        self._drawTriangularFrame3D(elem_labels, plane, h, style)

        final_z_label = (
            z_label
            if z_label
            else (
                config.triangular_colorbar_label
                if hasattr(config, "triangular_colorbar_label")
                else z_key
            )
        )

        self._ax.set_xlabel(wrap_latex(""), fontsize=style.labelFontSize)
        self._ax.set_ylabel(wrap_latex(""), fontsize=style.labelFontSize)
        self._ax.set_zlabel(wrap_latex(""), fontsize=style.labelFontSize)

        if title:
            self._ax.set_title(wrap_latex(title), fontsize=style.titleFontSize)

        self._ax.set_box_aspect((1, 1, 1))
        self._ax.set_xlim(-0.1, 1.1)
        self._ax.set_ylim(-0.15, 1.0)
        self._ax.axis("off")

        self._drawTriangularBase3D(
            z_min, z_max, elem_labels, plane, h, style, final_z_label, config
        )

        self._canvas.draw()

    def _drawTriangularBase3D(
        self,
        z_min: float,
        z_max: float,
        elem_labels: list[str],
        plane: str,
        h: float,
        style,
        z_label: str,
        config,
    ) -> None:
        factor = DEFAULT_TRIANGULAR_COORD_FACTOR
        tick_length = (
            config.triangular_tick_length
            if hasattr(config, "triangular_tick_length")
            else DEFAULT_CONTOUR_TRIANGULAR_TICK_LENGTH
        )
        grid_line_width = (
            style.grid_line_width if hasattr(style, "grid_line_width") else 1.0
        )

        if plane == "x_A-x_B":
            label_a = elem_labels[0] if len(elem_labels) > 0 else "A"
            label_b = elem_labels[1] if len(elem_labels) > 1 else "B"
            label_c = elem_labels[2] if len(elem_labels) > 2 else "C"
            pts_a = np.array([factor, h, 0])
            pts_b = np.array([0, 0, 0])
            pts_c = np.array([1, 0, 0])
        elif plane == "x_A-x_C":
            label_a = elem_labels[0] if len(elem_labels) > 0 else "A"
            label_b = elem_labels[2] if len(elem_labels) > 2 else "C"
            label_c = elem_labels[1] if len(elem_labels) > 1 else "B"
            pts_a = np.array([factor, h, 0])
            pts_b = np.array([1, 0, 0])
            pts_c = np.array([0, 0, 0])
        elif plane == "x_B-x_C":
            label_a = elem_labels[1] if len(elem_labels) > 1 else "B"
            label_b = elem_labels[2] if len(elem_labels) > 2 else "C"
            label_c = elem_labels[0] if len(elem_labels) > 0 else "A"
            pts_a = np.array([0, 0, 0])
            pts_b = np.array([1, 0, 0])
            pts_c = np.array([factor, h, 0])
        else:
            label_a = elem_labels[0] if len(elem_labels) > 0 else "A"
            label_b = elem_labels[1] if len(elem_labels) > 1 else "B"
            label_c = elem_labels[2] if len(elem_labels) > 2 else "C"
            pts_a = np.array([factor, h, 0])
            pts_b = np.array([0, 0, 0])
            pts_c = np.array([1, 0, 0])

        if style.gridMode == "auto":
            n_ticks = DEFAULT_COLORBAR_TICK_COUNT
        elif style.gridMode == "absolute":
            n_ticks = max(1, round(style.gridDensity))
        else:
            n_ticks = max(1, round(style.gridDensity * 10))

        tick_interval = 1.0 / n_ticks
        label_every = max(1, round(style.gridLabelDensity))
        display_ticks = []
        for i in range(1, n_ticks):
            display_ticks.append(
                (round(i * tick_interval, 2), (i - 1) % label_every == 0)
            )

        self._ax.plot(
            [pts_b[0], pts_c[0]],
            [pts_b[1], pts_c[1]],
            [0, 0],
            color=self._current_fg,
            linewidth=grid_line_width,
        )
        self._ax.plot(
            [pts_a[0], pts_c[0]],
            [pts_a[1], pts_c[1]],
            [0, 0],
            color=self._current_fg,
            linewidth=grid_line_width,
        )
        self._ax.plot(
            [pts_a[0], pts_b[0]],
            [pts_a[1], pts_b[1]],
            [0, 0],
            color=self._current_fg,
            linewidth=grid_line_width,
        )

        for t, show_label in display_ticks:
            pt_on_bc = pts_b + t * (pts_c - pts_b)
            tick_start = pt_on_bc - np.array([0, tick_length * 0.5, 0])
            tick_end = pt_on_bc + np.array([0, tick_length * 0.5, 0])
            self._ax.plot(
                [tick_start[0], tick_end[0]],
                [tick_start[1], tick_end[1]],
                [0, 0],
                color=self._current_fg,
                linewidth=DEFAULT_TICK_LINE_WIDTH,
            )
            if show_label:
                self._ax.text(
                    pt_on_bc[0],
                    pt_on_bc[1] - 0.02,
                    0,
                    f"{t:.2f}",
                    color=self._current_fg,
                    fontsize=style.tickFontSize,
                    ha="center",
                    va="top",
                )

        ab_dir = pts_a - pts_b
        left_nx = ab_dir[1]
        left_ny = -ab_dir[0]
        left_nlen = np.sqrt(left_nx * left_nx + left_ny * left_ny)
        left_nx, left_ny = left_nx / left_nlen, left_ny / left_nlen
        for t, show_label in display_ticks:
            pt_on_ab = pts_b + t * ab_dir
            tick_start = pt_on_ab - np.array([left_nx, left_ny, 0]) * tick_length * 0.5
            tick_end = pt_on_ab + np.array([left_nx, left_ny, 0]) * tick_length * 0.5
            self._ax.plot(
                [tick_start[0], tick_end[0]],
                [tick_start[1], tick_end[1]],
                [0, 0],
                color=self._current_fg,
                linewidth=DEFAULT_TICK_LINE_WIDTH,
            )
            if show_label:
                label_x = pt_on_ab[0] + left_nx * DEFAULT_LABEL_DISTANCE
                label_y = pt_on_ab[1] + left_ny * DEFAULT_LABEL_DISTANCE
                self._ax.text(
                    label_x,
                    label_y,
                    0,
                    f"{1 - t:.2f}",
                    color=self._current_fg,
                    fontsize=style.tickFontSize,
                    ha="right",
                    va="center",
                )

        ac_dir = pts_c - pts_a
        right_nx = -ac_dir[1]
        right_ny = ac_dir[0]
        right_nlen = np.sqrt(right_nx * right_nx + right_ny * right_ny)
        right_nx, right_ny = right_nx / right_nlen, right_ny / right_nlen
        for t, show_label in display_ticks:
            pt_on_ac = pts_a + t * ac_dir
            tick_start = (
                pt_on_ac - np.array([right_nx, right_ny, 0]) * tick_length * 0.5
            )
            tick_end = pt_on_ac + np.array([right_nx, right_ny, 0]) * tick_length * 0.5
            self._ax.plot(
                [tick_start[0], tick_end[0]],
                [tick_start[1], tick_end[1]],
                [0, 0],
                color=self._current_fg,
                linewidth=DEFAULT_TICK_LINE_WIDTH,
            )
            if show_label:
                label_x = pt_on_ac[0] + right_nx * DEFAULT_LABEL_DISTANCE
                label_y = pt_on_ac[1] + right_ny * DEFAULT_LABEL_DISTANCE
                self._ax.text(
                    label_x,
                    label_y,
                    0,
                    f"{t:.2f}",
                    color=self._current_fg,
                    fontsize=style.tickFontSize,
                    ha="left",
                    va="center",
                )

        self._ax.plot(
            [pts_a[0], pts_a[0]],
            [pts_a[1], pts_a[1]],
            [0, 1],
            color=self._current_fg,
            linewidth=grid_line_width,
        )

        for i in range(1, n_ticks):
            t = i * tick_interval
            z_pos = t
            self._ax.plot(
                [pts_a[0] - 0.015, pts_a[0] + 0.015],
                [pts_a[1], pts_a[1]],
                [z_pos, z_pos],
                color=self._current_fg,
                linewidth=DEFAULT_TICK_LINE_WIDTH,
            )
            if (i - 1) % label_every == 0:
                z_val = z_min + t * (z_max - z_min)
                self._ax.text(
                    pts_a[0] - 0.03,
                    pts_a[1],
                    z_pos,
                    f"{z_val:.4g}",
                    color=self._current_fg,
                    fontsize=style.tickFontSize,
                    ha="right",
                    va="center",
                )

        self._ax.text(
            pts_a[0] - 0.03,
            pts_a[1],
            1.05,
            wrap_latex(z_label),
            color=self._current_fg,
            fontsize=style.labelFontSize,
            ha="right",
            va="bottom",
        )

        self._ax.text(
            pts_a[0],
            pts_a[1] + DEFAULT_APEX_LABEL_OFFSET,
            0,
            wrap_latex(label_a),
            color=self._current_fg,
            fontsize=style.labelFontSize,
            ha="center",
            va="bottom",
        )
        self._ax.text(
            pts_b[0] + DEFAULT_SINGLE_TICK_LABEL_OFFSET,
            pts_b[1] + DEFAULT_ELEMENT_LABEL_OFFSET,
            0,
            wrap_latex(label_b),
            color=self._current_fg,
            fontsize=style.labelFontSize,
            ha="right",
            va="top",
        )
        self._ax.text(
            pts_c[0] - DEFAULT_SINGLE_TICK_LABEL_OFFSET,
            pts_c[1] + DEFAULT_ELEMENT_LABEL_OFFSET,
            0,
            wrap_latex(label_c),
            color=self._current_fg,
            fontsize=style.labelFontSize,
            ha="left",
            va="top",
        )

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
