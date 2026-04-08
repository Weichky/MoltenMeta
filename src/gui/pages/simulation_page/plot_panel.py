from typing import TYPE_CHECKING

from PySide6 import QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib as mpl

if TYPE_CHECKING:
    from core.plot.config import PlotStyleConfig


_DARK_BG = "#232323"
_LIGHT_BG = "#fafafa"
_DARK_FG = "#ffffff"
_LIGHT_FG = "#323232"


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

    def setScheme(self, scheme: str) -> None:
        self._setTheme(scheme)

    def _applyAxisColors(self) -> None:
        self._setTheme(self._current_scheme)

    def _wrapLatex(self, text: str) -> str:
        if not text:
            return text
        if text.startswith("$") and text.endswith("$"):
            return text
        if any(c in text for c in ("\\", "^", "_", "{")):
            return f"${text}$"
        return text

    def plot(
        self,
        config: "PlotStyleConfig",
        x_data: list[float],
        y_data: list[float],
    ) -> None:
        style = config.style
        self._ax.clear()
        self._applyAxisColors()
        self._ax.plot(
            x_data,
            y_data,
            marker=style.marker,
            color=style.colors[0] if style.colors else "tab:blue",
            linewidth=style.lineWidth,
            linestyle=style.lineStyle,
            markersize=style.markerSize,
        )
        self._ax.set_xlabel(
            self._wrapLatex(config.xLabel or config.x), fontsize=style.fontSize
        )
        self._ax.set_ylabel(
            self._wrapLatex(config.yLabels[0])
            if config.yLabels
            else (self._wrapLatex(config.y[0]) if config.y else ""),
            fontsize=style.fontSize,
        )
        if config.title:
            self._ax.set_title(
                self._wrapLatex(config.title), fontsize=style.fontSize + 2
            )
        self._ax.grid(style.grid, alpha=0.3)
        self._canvas.draw()

    def plotSinglePoint(
        self,
        config: "PlotStyleConfig",
        x: float,
        y: float,
    ) -> None:
        style = config.style
        self._ax.clear()
        self._applyAxisColors()
        self._ax.scatter(
            [x],
            [y],
            color=style.colors[0] if style.colors else "tab:red",
            s=100,
            zorder=5,
            marker=style.marker,
        )
        self._ax.set_xlabel(
            self._wrapLatex(config.xLabel or config.x), fontsize=style.fontSize
        )
        self._ax.set_ylabel(
            self._wrapLatex(config.yLabels[0])
            if config.yLabels
            else (self._wrapLatex(config.y[0]) if config.y else ""),
            fontsize=style.fontSize,
        )
        if config.title:
            self._ax.set_title(
                self._wrapLatex(config.title), fontsize=style.fontSize + 2
            )
        self._ax.grid(style.grid, alpha=0.3)
        self._canvas.draw()

    def clear(self) -> None:
        self._ax.clear()
        self._canvas.draw()
