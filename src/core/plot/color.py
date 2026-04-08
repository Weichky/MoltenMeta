from catalog import (
    COLOR_PALETTE_COLORBLIND_SAFE,
    COLOR_PALETTE_DEFAULT,
    COLOR_PALETTE_PASTEL,
    COLOR_PALETTE_VIBRANT,
    COLOR_PALETTES,
)


class ColorPalette:
    VIBRANT = COLOR_PALETTE_VIBRANT
    PASTEL = COLOR_PALETTE_PASTEL
    DEFAULT = COLOR_PALETTE_DEFAULT
    COLORBLIND_SAFE = COLOR_PALETTE_COLORBLIND_SAFE

    _PRESETS = COLOR_PALETTES

    @classmethod
    def getColors(cls, scheme: str) -> list[str]:
        for name, colors in cls._PRESETS:
            if name == scheme:
                return list(colors)
        return list(cls.DEFAULT)

    @classmethod
    def presetNames(cls) -> list[str]:
        return [name for name, _ in cls._PRESETS]
