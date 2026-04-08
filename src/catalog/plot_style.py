DEFAULT_LINE_WIDTH = 2.0
DEFAULT_MARKER_SIZE = 6.0
DEFAULT_FONT_SIZE = 12
DEFAULT_LINE_STYLE = "-"
DEFAULT_MARKER = "o"
DEFAULT_GRID = True
DEFAULT_COLOR_SCHEME = "default"
DEFAULT_PLOT_TYPE = "line_2d"

PLOT_TYPE_LINE_2D = "line_2d"
PLOT_TYPE_SCATTER_2D = "scatter_2d"
PLOT_TYPE_SCATTER_3D = "scatter_3d"
PLOT_TYPE_SURFACE_3D = "surface_3d"

COLOR_SCHEME_VIBRANT = "vibrant"
COLOR_SCHEME_PASTEL = "pastel"
COLOR_SCHEME_DEFAULT = "default"
COLOR_SCHEME_COLORBLIND = "colorblind_safe"

COLOR_PALETTE_VIBRANT = [
    "#039be5",
    "#ff6d00",
    "#43a047",
    "#8e24aa",
    "#00acc1",
    "#e53935",
    "#fdd835",
    "#6d4c41",
]

COLOR_PALETTE_PASTEL = [
    "#b3e5fc",
    "#ffe0b2",
    "#c8e6c9",
    "#e1bee7",
    "#b2ebf2",
    "#ffcdd2",
    "#fff9c4",
    "#d7ccc8",
]

COLOR_PALETTE_DEFAULT = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
]

COLOR_PALETTE_COLORBLIND_SAFE = [
    "#0072B2",
    "#E69F00",
    "#009E73",
    "#CC79A7",
    "#56B4E9",
    "#F0E442",
    "#D55E00",
    "#999999",
]

COLOR_PALETTES = (
    (COLOR_SCHEME_VIBRANT, COLOR_PALETTE_VIBRANT),
    (COLOR_SCHEME_PASTEL, COLOR_PALETTE_PASTEL),
    (COLOR_SCHEME_DEFAULT, COLOR_PALETTE_DEFAULT),
    (COLOR_SCHEME_COLORBLIND, COLOR_PALETTE_COLORBLIND_SAFE),
)
