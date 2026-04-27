import numpy as np

from catalog.plot_style import (
    DEFAULT_GRID_ALPHA,
    DEFAULT_MINOR_GRID_ALPHA,
    DEFAULT_GRID_RELATIVE_DIVISOR,
)


def _calcInterval(axis_min: float, axis_max: float, gridMode: str, gridDensity: float) -> float:
    range_val = axis_max - axis_min
    if gridMode == "absolute":
        return gridDensity
    return range_val / (DEFAULT_GRID_RELATIVE_DIVISOR * gridDensity)


def applyGridToAxis(
    ax,
    enabled: bool,
    gridMode: str,
    gridDensity: float,
    gridLabelDensity: float = 1.0,
) -> None:
    if not enabled:
        ax.grid(False)
        return

    if gridMode == "auto":
        ax.grid(True, alpha=DEFAULT_GRID_ALPHA)
        return

    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    x_interval = _calcInterval(xlim[0], xlim[1], gridMode, gridDensity)
    y_interval = _calcInterval(ylim[0], ylim[1], gridMode, gridDensity)

    x_ticks = np.arange(xlim[0], xlim[1] + x_interval, x_interval)
    y_ticks = np.arange(ylim[0], ylim[1] + y_interval, y_interval)

    ax.set_xticks(x_ticks)
    ax.set_yticks(y_ticks)
    ax.set_xticks(x_ticks, minor=True)
    ax.set_yticks(y_ticks, minor=True)
    ax.tick_params(which="major", label1On=True)
    ax.tick_params(which="minor", label1On=False)

    ax.grid(True, which="major", alpha=DEFAULT_GRID_ALPHA)
    ax.grid(True, which="minor", alpha=DEFAULT_MINOR_GRID_ALPHA)

    label_every = max(1, int(gridLabelDensity))
    for i, tick in enumerate(ax.xaxis.get_major_ticks()):
        tick.label1.set_visible(i % label_every == 0)
    for i, tick in enumerate(ax.yaxis.get_major_ticks()):
        tick.label1.set_visible(i % label_every == 0)


def applyGridToSingleAxis(
    axis,
    lim: tuple[float, float],
    gridDensity: float,
    gridMode: str,
    labelDensity: float,
) -> None:
    if gridMode == "auto":
        axis.grid(True, alpha=DEFAULT_GRID_ALPHA)
        return

    interval = _calcInterval(lim[0], lim[1], gridMode, gridDensity)
    ticks = np.arange(lim[0], lim[1] + interval, interval)
    axis.set_ticks(ticks)
    axis.grid(True, alpha=DEFAULT_GRID_ALPHA)

    label_every = max(1, int(labelDensity))
    for i, tick in enumerate(axis.get_major_ticks()):
        tick.label1.set_visible(i % label_every == 0)


def applyGrid3D(
    ax,
    enabled: bool,
    gridMode: str,
    gridDensity: float,
    gridLabelDensity: float = 1.0,
) -> None:
    if not enabled:
        ax.grid(False, which="major")
        return
    applyGridToSingleAxis(
        ax.zaxis, ax.get_zlim(), gridDensity, gridMode, gridLabelDensity
    )
