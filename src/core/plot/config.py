from __future__ import annotations
from dataclasses import dataclass, field
from importlib.resources import files
from typing import TYPE_CHECKING

import tomllib

from catalog import (
    DEFAULT_PLOT_TYPE,
    DEFAULT_THEME_PRESET,
    DEFAULT_ALGORITHM,
    ColorAlgorithm,
)

from core.plot.color import ColorPalette, ColorGenerator, ThemeColors
from core.plot.style import PlotStyle, getDefaultPlotStyle

if TYPE_CHECKING:
    from domain.settings import Settings


@dataclass(frozen=True)
class PlotStyleConfig:
    plotType: str = DEFAULT_PLOT_TYPE
    style: PlotStyle = field(default_factory=getDefaultPlotStyle)
    colorGenerator: ColorGenerator | None = None
    x: str = ""
    xLabel: str = ""
    y: list[str] = field(default_factory=list)
    yLabels: list[str] = field(default_factory=list)
    title: str = ""


def _getDefaultSettings() -> dict:
    try:
        default_path = files("resources.default").joinpath("default_settings.toml")
        with open(str(default_path), "rb") as f:
            return tomllib.load(f)
    except Exception:
        return {}


def _parseAlgorithm(algo_str: str | None) -> ColorAlgorithm:
    if not algo_str:
        return DEFAULT_ALGORITHM
    for algo in ColorAlgorithm:
        if algo.value == algo_str:
            return algo
    return DEFAULT_ALGORITHM


def _parseThemeColors(
    preset: str | None,
    primary: str | None,
    secondary: str | None,
    settings: "Settings | None" = None,
) -> ThemeColors | None:
    if preset == "custom" and settings:
        custom_primary = settings.get("plot", "custom_primary")
        custom_secondary = settings.get("plot", "custom_secondary")
        if custom_primary:
            return ThemeColors(
                primary=custom_primary,
                secondary=custom_secondary or "#000000",
            )
        return None
    if preset and preset != "custom":
        return ColorPalette.getThemeColors(preset)
    if primary:
        return ThemeColors(
            primary=primary,
            secondary=secondary or "#000000",
        )
    return None


class PlotStyleService:
    def __init__(self) -> None:
        pass

    def buildStyle(
        self, module_config: dict, method_config: dict, settings: "Settings | None"
    ) -> PlotStyle:
        system_style = getDefaultPlotStyle()

        module_colorscheme = module_config.get("colorscheme", {})
        method_colorscheme = method_config.get("colorscheme", {})

        module_algorithm = _parseAlgorithm(module_colorscheme.get("algorithm"))
        method_algorithm_str = method_colorscheme.get("algorithm")
        db_algorithm_str = settings.get("plot", "color_algorithm") if settings else None

        algorithm优先级 = (
            _parseAlgorithm(method_algorithm_str)
            or module_algorithm
            or _parseAlgorithm(db_algorithm_str)
            or system_style.algorithm
        )

        module_preset = module_colorscheme.get("preset")
        method_preset = method_colorscheme.get("preset")
        db_preset = settings.get("plot", "colorscheme") if settings else None

        module_primary = module_colorscheme.get("primary")
        method_primary = method_colorscheme.get("primary")
        module_secondary = module_colorscheme.get("secondary")
        method_secondary = method_colorscheme.get("secondary")

        final_theme = (
            _parseThemeColors(method_preset, method_primary, method_secondary, settings)
            or _parseThemeColors(
                module_preset, module_primary, module_secondary, settings
            )
            or _parseThemeColors(db_preset, None, None, settings)
            or system_style.themeColors
        )

        lineStyle = (
            method_colorscheme.get("lineStyle")
            or module_colorscheme.get("lineStyle")
            or (settings.get("plot", "lineStyle") if settings else None)
            or system_style.lineStyle
        )
        marker = (
            method_colorscheme.get("marker")
            or module_colorscheme.get("marker")
            or (settings.get("plot", "marker") if settings else None)
            or system_style.marker
        )
        lineWidth = (
            float(method_colorscheme["lineWidth"])
            if "lineWidth" in method_colorscheme
            else float(module_colorscheme["lineWidth"])
            if "lineWidth" in module_colorscheme
            else (
                float(settings.get("plot", "lineWidth"))
                if settings and settings.get("plot", "lineWidth")
                else None
            )
            or system_style.lineWidth
        )
        markerSize = (
            float(method_colorscheme["markerSize"])
            if "markerSize" in method_colorscheme
            else float(module_colorscheme["markerSize"])
            if "markerSize" in module_colorscheme
            else (
                float(settings.get("plot", "markerSize"))
                if settings and settings.get("plot", "markerSize")
                else None
            )
            or system_style.markerSize
        )
        grid = (
            method_colorscheme.get("grid", NotImplemented)
            if "grid" in method_colorscheme
            else module_colorscheme.get("grid", NotImplemented)
            if "grid" in module_colorscheme
            else (
                settings.get("plot", "grid") == "true"
                if settings and settings.get("plot", "grid")
                else NotImplemented
            )
        )
        if grid is NotImplemented:
            grid = system_style.grid

        fontSize = (
            int(method_colorscheme["fontSize"])
            if "fontSize" in method_colorscheme
            else int(module_colorscheme["fontSize"])
            if "fontSize" in module_colorscheme
            else (
                int(settings.get("plot", "fontSize"))
                if settings and settings.get("plot", "fontSize")
                else None
            )
            or system_style.fontSize
        )

        return PlotStyle(
            algorithm=algorithm优先级,
            themeColors=final_theme,
            lineStyle=lineStyle,
            marker=marker,
            lineWidth=lineWidth,
            markerSize=markerSize,
            grid=grid,
            fontSize=fontSize,
        )

    def buildConfig(
        self, module_config: dict, method_config: dict, settings: "Settings | None"
    ) -> PlotStyleConfig:
        plot_config = method_config.get("plot", {})
        style = self.buildStyle(module_config, method_config, settings)
        theme = style.themeColors or ColorPalette.getThemeColors(DEFAULT_THEME_PRESET)
        generator = ColorGenerator(theme, style.algorithm)

        return PlotStyleConfig(
            plotType=plot_config.get("plotType", DEFAULT_PLOT_TYPE),
            style=style,
            colorGenerator=generator,
            x=plot_config.get("x", ""),
            xLabel=plot_config.get("xLabel", ""),
            y=plot_config.get("y", []),
            yLabels=plot_config.get("yLabels", []),
            title=plot_config.get("title", ""),
        )
