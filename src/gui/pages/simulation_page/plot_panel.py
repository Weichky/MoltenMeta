from PySide6 import QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib as mpl


class PlotPanel(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        mpl.rcParams["text.usetex"] = False
        self._canvas = FigureCanvasQTAgg(Figure(figsize=(8, 6)))
        self._ax = self._canvas.figure.add_subplot(111)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._canvas)
        self._ax.set_xlabel("")
        self._ax.set_ylabel("")
        self._ax.grid(True, alpha=0.3)

    def _wrapLatex(self, text: str) -> str:
        if text.startswith("$") and text.endswith("$"):
            return text
        return f"${text}$"

    def plot(
        self,
        x_data: list[float],
        y_data: list[float],
        x_label: str = "",
        y_label: str = "",
        title: str = "",
        marker: str = "o",
        color: str = "tab:blue",
    ) -> None:
        self._ax.clear()
        self._ax.plot(x_data, y_data, marker=marker, color=color, linewidth=2)
        self._ax.set_xlabel(self._wrapLatex(x_label), fontsize=12)
        self._ax.set_ylabel(self._wrapLatex(y_label), fontsize=12)
        if title:
            self._ax.set_title(self._wrapLatex(title), fontsize=14)
        self._ax.grid(True, alpha=0.3)
        self._canvas.draw()

    def plotSinglePoint(
        self,
        x: float,
        y: float,
        x_label: str = "",
        y_label: str = "",
        title: str = "",
        color: str = "tab:red",
    ) -> None:
        self._ax.clear()
        self._ax.scatter([x], [y], color=color, s=100, zorder=5, marker="o")
        self._ax.set_xlabel(self._wrapLatex(x_label), fontsize=12)
        self._ax.set_ylabel(self._wrapLatex(y_label), fontsize=12)
        if title:
            self._ax.set_title(self._wrapLatex(title), fontsize=14)
        self._ax.grid(True, alpha=0.3)
        self._canvas.draw()

    def clear(self) -> None:
        self._ax.clear()
        self._ax.set_xlabel("")
        self._ax.set_ylabel("")
        self._canvas.draw()
