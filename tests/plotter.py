"""
Standardized Butler Test Plotter
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass


@dataclass
class PlotConfig:
    xLabel: str
    yLabel: str
    title: str
    xLims: tuple[float, float]
    yLims: tuple[float, float] | None = None
    equalAspect: bool = True


@dataclass
class SystemConfig:
    elemA: int
    elemB: int
    temperature: float
    xBulkLabel: str
    sigmaILabel: dict[int, float]


def plotSigma(
    butler,
    system: SystemConfig,
    plotCfg: PlotConfig,
    xRange: np.ndarray,
    T: float,
) -> tuple[np.ndarray, np.ndarray]:
    sigmaValues = []
    xAValues = []

    for x in xRange:
        result = butler.solve(T, float(x))
        sigmaValues.append(result["sigma"])
        xAValues.append(result["x_A_surface"])

    sigmaValues = np.array(sigmaValues)
    xAValues = np.array(xAValues)

    yMin = np.nanmin(sigmaValues)
    yMax = np.nanmax(sigmaValues)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.plot(xRange, sigmaValues, "b-", linewidth=2)
    ax.set_xlabel(plotCfg.xLabel, fontsize=12)
    ax.set_ylabel(plotCfg.yLabel, fontsize=12)
    ax.set_title(plotCfg.title, fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(plotCfg.xLims)
    ax.set_ylim(yMin, yMax)
    ax.set_aspect(
        (plotCfg.xLims[1] - plotCfg.xLims[0]) / (yMax - yMin), adjustable="box"
    )
    plt.savefig(
        f"temp/{system.elemA}_{system.elemB}_sigma_{int(T)}.png",
        dpi=150,
        bbox_inches=None,
    )
    plt.close()
    print(f"Saved: temp/{system.elemA}_{system.elemB}_sigma_{int(T)}.png")

    return sigmaValues, xAValues


def plotSurfaceComposition(
    system: SystemConfig,
    plotCfg: PlotConfig,
    xRange: np.ndarray,
    xAValues: np.ndarray,
) -> None:
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.plot(xRange, xAValues, "b-", linewidth=2, label="x^S")
    ax.plot([0, 1], [0, 1], "k--", linewidth=1, label="x^S = x^B")
    ax.set_xlabel(plotCfg.xLabel, fontsize=12)
    ax.set_ylabel(plotCfg.yLabel, fontsize=12)
    ax.set_title(plotCfg.title, fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(plotCfg.xLims)
    ax.set_ylim(plotCfg.yLims if plotCfg.yLims else (0, 1))
    if plotCfg.equalAspect:
        ax.set_aspect("equal", adjustable="datalim")
    plt.tight_layout()
    plt.savefig(
        f"temp/{system.elemA}_{system.elemB}_xs_{int(system.temperature)}.png",
        dpi=150,
        bbox_inches=None,
    )
    plt.close()
    print(f"Saved: temp/{system.elemA}_{system.elemB}_xs_{int(system.temperature)}.png")
