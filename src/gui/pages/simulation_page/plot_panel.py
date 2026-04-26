import logging
from typing import TYPE_CHECKING

from PySide6 import QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.tri import Triangulation
import matplotlib as mpl
import numpy as np

if TYPE_CHECKING:
    from core.plot.config import PlotStyleConfig


_DARK_BG = "#232323"
_LIGHT_BG = "#fafafa"
_DARK_FG = "#ffffff"
_LIGHT_FG = "#323232"

logging.getLogger("matplotlib").setLevel(logging.WARNING)


class PlotPanel(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        mpl.rcParams["text.usetex"] = False
        self._figure = Figure(figsize=(8, 6))
        self._canvas = FigureCanvasQTAgg(self._figure)
        self._ax = self._figure.add_subplot(111)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._canvas)
        self._current_scheme = "light"
        self._setTheme("light")

    def applyPlaceholder(self, grid: bool, gridMode: str, gridDensity: float, gridLabelDensity: float) -> None:
        self._applyGrid(grid, gridMode, gridDensity, gridLabelDensity)
        self._canvas.draw()

    def _applyGrid(
        self,
        enabled: bool,
        gridMode: str,
        gridDensity: float,
        gridLabelDensity: float = 1.0,
    ) -> None:
        if not enabled:
            self._ax.grid(False)
            return

        if gridMode == "auto":
            self._ax.grid(True, alpha=0.3)
            return

        xlim = self._ax.get_xlim()
        ylim = self._ax.get_ylim()

        def calcInterval(axis_min: float, axis_max: float) -> float:
            range_val = axis_max - axis_min
            if gridMode == "absolute":
                return gridDensity
            return range_val / (10.0 * gridDensity)

        x_interval = calcInterval(xlim[0], xlim[1])
        y_interval = calcInterval(ylim[0], ylim[1])

        x_ticks = np.arange(xlim[0], xlim[1] + x_interval, x_interval)
        y_ticks = np.arange(ylim[0], ylim[1] + y_interval, y_interval)

        self._ax.set_xticks(x_ticks)
        self._ax.set_yticks(y_ticks)
        self._ax.set_xticks(x_ticks, minor=True)
        self._ax.set_yticks(y_ticks, minor=True)
        self._ax.tick_params(which="major", label1On=True)
        self._ax.tick_params(which="minor", label1On=False)

        self._ax.grid(True, which="major", alpha=0.3)
        self._ax.grid(True, which="minor", alpha=0.15)

        label_every = max(1, int(gridLabelDensity))
        for i, tick in enumerate(self._ax.xaxis.get_major_ticks()):
            tick.label1.set_visible(i % label_every == 0)
        for i, tick in enumerate(self._ax.yaxis.get_major_ticks()):
            tick.label1.set_visible(i % label_every == 0)

    def _applyGridToAxis(
        self,
        axis,
        lim: tuple[float, float],
        gridDensity: float,
        gridMode: str,
        labelDensity: float,
    ) -> None:
        if gridMode == "auto":
            axis.grid(True, alpha=0.3)
            return

        def calcInterval(axis_min: float, axis_max: float) -> float:
            range_val = axis_max - axis_min
            if gridMode == "absolute":
                return gridDensity
            return range_val / (10.0 * gridDensity)

        interval = calcInterval(lim[0], lim[1])
        ticks = np.arange(lim[0], lim[1] + interval, interval)
        axis.set_ticks(ticks)
        axis.grid(True, alpha=0.3)

        label_every = max(1, int(labelDensity))
        for i, tick in enumerate(axis.get_major_ticks()):
            tick.label1.set_visible(i % label_every == 0)

    def _applyGrid3D(
        self,
        enabled: bool,
        gridMode: str,
        gridDensity: float,
        gridLabelDensity: float = 1.0,
    ) -> None:
        if not enabled:
            self._ax.grid(False, which="major")
            return
        self._applyGridToAxis(
            self._ax.zaxis, self._ax.get_zlim(), gridDensity, gridMode, gridLabelDensity
        )

    def _setTheme(self, scheme: str) -> None:
        self._current_scheme = scheme
        if scheme == "dark":
            self._figure.set_facecolor(_DARK_BG)
            self._ax.set_facecolor(_DARK_BG)
            self._ax.xaxis.label.set_color(_DARK_FG)
            self._ax.yaxis.label.set_color(_DARK_FG)
            self._ax.title.set_color(_DARK_FG)
            self._ax.spines["bottom"].set_color(_DARK_FG)
            self._ax.spines["top"].set_color(_DARK_FG)
            self._ax.spines["left"].set_color(_DARK_FG)
            self._ax.spines["right"].set_color(_DARK_FG)
            self._ax.tick_params(axis="x", colors=_DARK_FG)
            self._ax.tick_params(axis="y", colors=_DARK_FG)
            if hasattr(self._ax, "zaxis"):
                self._ax.zaxis.label.set_color(_DARK_FG)
                self._ax.tick_params(axis="z", colors=_DARK_FG)
                self._ax.xaxis.pane.fill = False
                self._ax.yaxis.pane.fill = False
                self._ax.zaxis.pane.fill = False
                self._ax.xaxis.pane.set_facecolor(_DARK_BG)
                self._ax.yaxis.pane.set_facecolor(_DARK_BG)
                self._ax.zaxis.pane.set_facecolor(_DARK_BG)
        else:
            self._figure.set_facecolor(_LIGHT_BG)
            self._ax.set_facecolor(_LIGHT_BG)
            self._ax.xaxis.label.set_color(_LIGHT_FG)
            self._ax.yaxis.label.set_color(_LIGHT_FG)
            self._ax.title.set_color(_LIGHT_FG)
            self._ax.spines["bottom"].set_color(_LIGHT_FG)
            self._ax.spines["top"].set_color(_LIGHT_FG)
            self._ax.spines["left"].set_color(_LIGHT_FG)
            self._ax.spines["right"].set_color(_LIGHT_FG)
            self._ax.tick_params(axis="x", colors=_LIGHT_FG)
            self._ax.tick_params(axis="y", colors=_LIGHT_FG)
            if hasattr(self._ax, "zaxis"):
                self._ax.zaxis.label.set_color(_LIGHT_FG)
                self._ax.tick_params(axis="z", colors=_LIGHT_FG)

    def setScheme(self, scheme: str) -> None:
        self._setTheme(scheme)

    def _applyAxisColors(self) -> None:
        self._setTheme(self._current_scheme)

    def _wrapLatex(self, text: str) -> str:
        """Validate latex syntax by test-rendering, return original if invalid."""
        if not text:
            return text
        if not any(c in text for c in ("\\", "^", "_", "{")):
            return text
        from matplotlib.figure import Figure

        fig = Figure()
        ax = fig.add_subplot(111)
        try:
            ax.set_xlabel(f"${text}$")
            ax.set_ylabel(f"${text}$")
        except Exception:
            return text
        return f"${text}$"

    def plot(
        self,
        config: "PlotStyleConfig",
        x_data: list[float],
        y_data: list[float],
        x_label: str | None = None,
        y_label: str | None = None,
    ) -> None:
        self._figure.clear()
        self._ax = self._figure.add_subplot(111)
        style = config.style
        generator = config.colorGenerator
        self._ax.clear()
        self._applyAxisColors()
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
        final_x_label = x_label if x_label is not None else (config.xLabel or config.x)
        final_y_label = (
            y_label
            if y_label is not None
            else (
                config.yLabels[0]
                if config.yLabels
                else (config.y[0] if config.y else "")
            )
        )
        self._ax.set_xlabel(
            self._wrapLatex(final_x_label), fontsize=style.labelFontSize
        )
        self._ax.set_ylabel(
            self._wrapLatex(final_y_label),
            fontsize=style.labelFontSize,
        )
        if config.title:
            self._ax.set_title(
                self._wrapLatex(config.title), fontsize=style.titleFontSize
            )
        self._ax.tick_params(axis="both", labelsize=style.tickFontSize)
        self._applyGrid(
            style.grid, style.gridMode, style.gridDensity, style.gridLabelDensity
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
        self._ax = self._figure.add_subplot(111)
        style = config.style
        generator = config.colorGenerator
        self._ax.clear()
        self._applyAxisColors()
        color = generator.getColor(0, 1) if generator else style.themeColors.primary
        self._ax.scatter(
            [x],
            [y],
            color=color,
            s=100,
            zorder=5,
            marker=style.marker,
        )
        final_x_label = x_label if x_label is not None else (config.xLabel or config.x)
        final_y_label = (
            y_label
            if y_label is not None
            else (
                config.yLabels[0]
                if config.yLabels
                else (config.y[0] if config.y else "")
            )
        )
        self._ax.set_xlabel(
            self._wrapLatex(final_x_label), fontsize=style.labelFontSize
        )
        self._ax.set_ylabel(
            self._wrapLatex(final_y_label),
            fontsize=style.labelFontSize,
        )
        if config.title:
            self._ax.set_title(
                self._wrapLatex(config.title), fontsize=style.titleFontSize
            )
        self._ax.tick_params(axis="both", labelsize=style.tickFontSize)
        self._applyGrid(
            style.grid, style.gridMode, style.gridDensity, style.gridLabelDensity
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
        """Render 3D scatter plot with ternary composition coordinates."""
        self._figure.clear()
        self._ax = self._figure.add_subplot(111, projection="3d")
        self._setTheme(self._current_scheme)

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
            alpha=0.7,
        )

        self._ax.set_xlabel(
            self._wrapLatex(x_label or "x"), fontsize=style.labelFontSize
        )
        self._ax.set_ylabel(
            self._wrapLatex(y_label or "y"), fontsize=style.labelFontSize
        )
        self._ax.set_zlabel(
            self._wrapLatex(z_label or "z"), fontsize=style.labelFontSize
        )

        if title:
            self._ax.set_title(self._wrapLatex(title), fontsize=style.titleFontSize)

        self._ax.tick_params(axis="both", labelsize=style.tickFontSize)
        self._ax.tick_params(axis="z", labelsize=style.tickFontSize)
        self._applyGrid(style.grid, style.gridMode, style.gridDensity, style.gridLabelDensity)
        self._applyGrid3D(style.grid, style.gridMode, style.gridDensity, style.gridLabelDensity)

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
        """Render filled contour plot with color bar and optional custom generator."""
        self._figure.clear()
        self._ax = self._figure.add_subplot(111)
        self._ax.clear()
        self._applyAxisColors()

        style = config.style
        generator = config.colorGenerator

        import numpy as np

        x_arr = np.array(x_mesh)
        y_arr = np.array(y_mesh)
        z_arr = np.array(z_mesh)

        z_min = np.nanmin(z_arr)
        z_max = np.nanmax(z_arr)
        if z_min == z_max:
            z_min = z_min - 1e-10
            z_max = z_max + 1e-10

        if generator:
            n_cmap = 256
            cmap_colors = [generator.getColorAt(i / (n_cmap - 1)) for i in range(n_cmap)]
            cmap = mpl.colors.ListedColormap(cmap_colors)
            z_norm = (z_arr - z_min) / (z_max - z_min + 1e-12)
            cf = self._ax.contourf(
                x_arr,
                y_arr,
                z_norm,
                levels=np.linspace(0, 1, levels),
                cmap=cmap,
                alpha=0.8,
                extend="neither",
            )
            for i, level in enumerate(np.linspace(0, 1, levels)):
                color = generator.getColorAt(level)
                self._ax.contour(
                    x_arr, y_arr, z_norm, levels=[level], colors=[color], linewidths=0.5
                )
        else:
            contour_levels = np.linspace(z_min, z_max, levels)
            cf = self._ax.contourf(
                x_arr,
                y_arr,
                z_arr,
                levels=contour_levels,
                cmap="viridis",
                alpha=0.8,
            )

        cbar = self._figure.colorbar(cf, ax=self._ax)
        cbar.set_label(self._wrapLatex("Z_ABC"), fontsize=style.labelFontSize)

        self._ax.set_xlabel(
            self._wrapLatex(x_label or "x"), fontsize=style.labelFontSize
        )
        self._ax.set_ylabel(
            self._wrapLatex(y_label or "y"), fontsize=style.labelFontSize
        )

        if title:
            self._ax.set_title(self._wrapLatex(title), fontsize=style.titleFontSize)

        self._ax.set_xlim(0, 1)
        self._ax.set_ylim(0, 1)
        self._ax.tick_params(axis="both", labelsize=style.tickFontSize)
        self._applyGrid(style.grid, style.gridMode, style.gridDensity, style.gridLabelDensity)

        self._canvas.draw()

    def contour_triangular(
        self,
        config: "PlotStyleConfig",
        values: list[dict],
        conditions: dict | None = None,
        title: str | None = None,
        z_label: str | None = None,
        levels: int | None = None,
    ) -> None:
        """
        Draw contour plot in triangular coordinate system.

        Args:
            config: Plot style configuration
            values: List of dicts with x_A, x_B, x_C and Z_ABC
            conditions: Dict with elem_A, elem_B, elem_C symbols
            title: Plot title (overrides config.title if provided)
            z_label: Z-axis label (overrides config if provided)
            levels: Number of contour levels (overrides config if provided)
        """
        import numpy as np

        self._figure.clear()
        self._ax = self._figure.add_subplot(111)
        self._setTheme(self._current_scheme)

        style = config.style
        generator = config.colorGenerator
        h = config.triangular_height_factor
        xlim = config.triangular_xlim
        ylim = config.triangular_ylim
        tick_positions = config.triangular_tick_positions
        tick_length = config.triangular_tick_length
        plot_levels = levels if levels is not None else config.triangular_levels

        if conditions:
            elem_labels = [
                conditions.get("elem_A", "A"),
                conditions.get("elem_B", "B"),
                conditions.get("elem_C", "C"),
            ]
        else:
            elem_labels = config.triangular_elem_labels

        final_colorbar_label = z_label if z_label else config.triangular_colorbar_label

        x_A_arr = np.array([v.get("x_A", 0) for v in values])
        x_B_arr = np.array([v.get("x_B", 0) for v in values])
        x_C_arr = np.array([v.get("x_C", 0) for v in values])
        z_key = next((k for k in values[0] if k not in ("x_A", "x_B", "x_C")), "Z_ABC")
        z_arr = np.array([v.get(z_key, 0) for v in values])

        if len(x_A_arr) == 0 or len(x_B_arr) == 0 or len(x_C_arr) == 0:
            return

        valid_mask = (
            ~np.isnan(z_arr)
            & (x_A_arr >= 0)
            & (x_A_arr <= 1)
            & (x_B_arr >= 0)
            & (x_B_arr <= 1)
            & (x_C_arr >= 0)
            & (x_C_arr <= 1)
            & (x_A_arr + x_B_arr + x_C_arr > 0.99)
            & (x_A_arr + x_B_arr + x_C_arr < 1.01)
        )

        if not np.any(valid_mask):
            return

        x_A_valid = x_A_arr[valid_mask]
        x_C_valid = x_C_arr[valid_mask]
        z_valid = z_arr[valid_mask]

        x_cart = x_C_valid + 0.5 * x_A_valid
        y_cart = h * x_A_valid

        triang = Triangulation(x_cart, y_cart)

        z_min = np.min(z_valid)
        z_max = np.max(z_valid)
        if z_min == z_max:
            z_min = z_min - 1e-10
            z_max = z_max + 1e-10
        contour_levels = np.linspace(z_min, z_max, plot_levels)

        if generator:
            n_cmap = 256
            cmap_colors = [generator.getColorAt(i / (n_cmap - 1)) for i in range(n_cmap)]
            cmap = mpl.colors.ListedColormap(cmap_colors)
            cmap.set_under("white")
            cmap.set_over("white")
            z_normalized = (z_valid - z_min) / (z_max - z_min + 1e-12)
            cf = self._ax.tricontourf(
                triang,
                z_normalized,
                levels=np.linspace(0, 1, plot_levels),
                cmap=cmap,
                alpha=0.8,
                extend="neither",
            )
            self._ax.tricontour(
                triang, z_valid, levels=contour_levels, colors="white", linewidths=0.3
            )
        else:
            cf = self._ax.tricontourf(
                triang,
                z_valid,
                levels=contour_levels,
                cmap="viridis",
                alpha=0.8,
            )

        cbar = self._figure.colorbar(cf, ax=self._ax)
        cbar.set_label(
            self._wrapLatex(final_colorbar_label), fontsize=style.labelFontSize
        )
        cbar.ax.tick_params(labelsize=style.tickFontSize)

        self._draw_triangular_axes(
            style,
            h,
            xlim,
            ylim,
            tick_positions,
            tick_length,
            elem_labels,
        )

        final_title = title if title else config.title
        if final_title:
            self._ax.set_title(
                self._wrapLatex(final_title), fontsize=style.titleFontSize
            )

        self._canvas.draw()

    def _draw_triangular_axes(
        self,
        style,
        h: float,
        xlim: list[float],
        ylim: list[float],
        tick_positions: list[float],
        tick_length: float,
        elem_labels: list[str],
    ) -> None:
        """Draw triangular coordinate axes with ticks and labels on all three sides."""
        self._ax.set_xlim(xlim[0], xlim[1])
        self._ax.set_ylim(ylim[0], ylim[1])
        self._ax.set_aspect("equal")
        self._ax.axis("off")

        triangle_x = [0, 1, 0.5, 0]
        triangle_y = [0, 0, h, 0]
        self._ax.plot(triangle_x, triangle_y, "k-", linewidth=1.0)

        for t in tick_positions:
            if t <= 1.0:
                self._ax.plot([t, t], [-tick_length, tick_length], "k-", linewidth=0.8)
                self._ax.text(
                    t,
                    -0.05,
                    f"{t:.1f}",
                    ha="center",
                    va="top",
                    fontsize=style.tickFontSize,
                )

        for i, t in enumerate(tick_positions):
            if t <= 0.5:
                x_on_left = t * 0.5
                y_on_left = t * h
                dx = -0.02
                dy = 0
                self._ax.plot(
                    [x_on_left - dx, x_on_left + dx],
                    [y_on_left - dy, y_on_left + dy],
                    "k-",
                    linewidth=0.8,
                )
                label_x = x_on_left - 0.06
                label_y = y_on_left
                self._ax.text(
                    label_x,
                    label_y,
                    f"{1 - t:.1f}",
                    ha="right",
                    va="center",
                    fontsize=style.tickFontSize,
                )

        for i, t in enumerate(tick_positions):
            if t <= 0.5:
                x_on_right = 1 - t * 0.5
                y_on_right = t * h
                dx = 0.02
                dy = 0
                self._ax.plot(
                    [x_on_right - dx, x_on_right + dx],
                    [y_on_right - dy, y_on_right + dy],
                    "k-",
                    linewidth=0.8,
                )
                label_x = x_on_right + 0.06
                label_y = y_on_right
                self._ax.text(
                    label_x,
                    label_y,
                    f"{1 - t:.1f}",
                    ha="left",
                    va="center",
                    fontsize=style.tickFontSize,
                )

        label_a = elem_labels[0] if len(elem_labels) > 0 else "A"
        label_b = elem_labels[1] if len(elem_labels) > 1 else "B"
        label_c = elem_labels[2] if len(elem_labels) > 2 else "C"

        self._ax.text(
            0.5,
            h + 0.1,
            label_a,
            ha="center",
            va="bottom",
            fontsize=style.labelFontSize,
        )
        self._ax.text(
            xlim[0] - 0.05,
            -0.05,
            label_b,
            ha="right",
            va="top",
            fontsize=style.labelFontSize,
        )
        self._ax.text(
            xlim[1] + 0.05,
            -0.05,
            label_c,
            ha="left",
            va="top",
            fontsize=style.labelFontSize,
        )
