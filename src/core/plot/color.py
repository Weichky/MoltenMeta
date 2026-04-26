from dataclasses import dataclass
import colorsys

from catalog import (
    THEME_PRESETS,
    ColorAlgorithm,
)


@dataclass(frozen=True)
class ThemeColors:
    primary: str
    secondary: str

    @staticmethod
    def fromPreset(preset: str) -> "ThemeColors":
        for name, theme in THEME_PRESETS:
            if name == preset:
                return ThemeColors(
                    primary=theme["primary"],
                    secondary=theme["secondary"],
                )
        from catalog import THEME_COLORS_DEFAULT

        return ThemeColors(
            primary=THEME_COLORS_DEFAULT["primary"],
            secondary=THEME_COLORS_DEFAULT["secondary"],
        )


def _hexToRgb(hex_color: str) -> tuple[float, float, float]:
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return (r, g, b)


def _rgbToHex(rgb: tuple[float, float, float]) -> str:
    return "#{:02x}{:02x}{:02x}".format(
        int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
    )


def _lerpColor(
    color1: tuple[float, float, float], color2: tuple[float, float, float], t: float
) -> tuple[float, float, float]:
    return (
        color1[0] + (color2[0] - color1[0]) * t,
        color1[1] + (color2[1] - color1[1]) * t,
        color1[2] + (color2[2] - color1[2]) * t,
    )


class ColorGenerator:
    def __init__(
        self, theme: ThemeColors, algorithm: ColorAlgorithm = ColorAlgorithm.LINEAR
    ):
        self._theme = theme
        self._algorithm = algorithm

    def getColor(self, index: int, total: int = 1) -> str:
        if self._algorithm == ColorAlgorithm.LINEAR:
            return self._linear(index, total)
        elif self._algorithm == ColorAlgorithm.HARMONIC:
            return self._harmonic(index, total)
        elif self._algorithm == ColorAlgorithm.COLORWHEEL:
            return self._colorwheel(index, total)
        return self._linear(index, total)

    def getColorN(self, n: int) -> list[str]:
        return [self.getColor(i, n) for i in range(n)]

    def getColorAt(self, t: float) -> str:
        t = max(0.0, min(1.0, t))
        if self._algorithm == ColorAlgorithm.LINEAR:
            return self._colorAtLinear(t)
        elif self._algorithm == ColorAlgorithm.HARMONIC:
            return self._colorAtHarmonic(t)
        elif self._algorithm == ColorAlgorithm.COLORWHEEL:
            return self._colorAtColorwheel(t)
        return self._theme.primary

    def _colorAtLinear(self, t: float) -> str:
        primary_rgb = _hexToRgb(self._theme.primary)
        secondary_rgb = _hexToRgb(self._theme.secondary)
        result_rgb = _lerpColor(primary_rgb, secondary_rgb, t)
        return _rgbToHex(result_rgb)

    def _colorAtHarmonic(self, t: float) -> str:
        rgb = _hexToRgb(self._theme.primary)
        hsv = colorsys.rgb_to_hsv(*rgb)
        new_hue = (hsv[0] + t) % 1.0
        result = colorsys.hsv_to_rgb(new_hue, hsv[1], hsv[2])
        return _rgbToHex(result)

    def _colorAtColorwheel(self, t: float) -> str:
        rgb = colorsys.hsv_to_rgb(t, 0.7, 0.9)
        return _rgbToHex(rgb)

    def _linear(self, index: int, total: int) -> str:
        if total == 1:
            return self._theme.primary
        t = index / (total - 1) if total > 1 else 0
        return self._colorAtLinear(t)

    def _harmonic(self, index: int, total: int) -> str:
        t = index * (1.0 / total)
        return self._colorAtHarmonic(t)

    def _colorwheel(self, index: int, total: int) -> str:
        if total == 1:
            return self._theme.primary
        t = index * (360.0 / total) / 360.0
        return self._colorAtColorwheel(t)


class ColorPalette:
    _PRESETS = THEME_PRESETS

    @classmethod
    def getThemeColors(cls, scheme: str) -> ThemeColors:
        return ThemeColors.fromPreset(scheme)

    @classmethod
    def presetNames(cls) -> list[str]:
        return [name for name, _ in cls._PRESETS]

    @classmethod
    def getGenerator(
        cls, scheme: str, algorithm: ColorAlgorithm = ColorAlgorithm.LINEAR
    ) -> ColorGenerator:
        theme = cls.getThemeColors(scheme)
        return ColorGenerator(theme, algorithm)
