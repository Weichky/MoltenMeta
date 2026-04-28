from domain.snapshot import SettingsSnapshot


class Settings:
    def __init__(self, records: list[SettingsSnapshot] | None = None):
        self._data: dict[tuple[str, str], str] = {}

        if records is not None:
            for r in records:
                self._data[(r.section, r.key)] = r.value

    def get(self, section: str, key: str, default=None):
        return self._data.get((section, key), default)

    def to_snapshots(self) -> list[SettingsSnapshot]:
        result = []
        for (section, key), value in self._data.items():
            snap = SettingsSnapshot(section=section, key=key, value=value)
            result.append(snap)
        return result

    # runtime
    @property
    def python_version(self) -> str:
        return self.get("runtime", "python_version")

    # database
    @property
    def database_type(self) -> str:
        return self.get("database", "db_type")

    @property
    def sqlite_db_path(self) -> str:
        return self.get("database", "sqlite_path")

    @property
    def database_file(self) -> str:
        return self.get("database", "database_file")

    # log
    @property
    def log_level(self) -> str:
        return self.get("log", "level")

    @property
    def enable_file_logging(self) -> bool:
        return self.get("log", "file_logging") == "true"

    # locale
    @property
    def language(self) -> str:
        return self.get("locale", "language")

    # appearance
    @property
    def scheme(self) -> str:
        return self.get("appearance", "scheme")

    @property
    def theme_mode(self) -> str:
        return self.get("appearance", "theme_mode")

    @property
    def density_scale(self) -> int:
        val = self.get("appearance", "density_scale", "-2")
        try:
            return int(val)
        except (ValueError, TypeError):
            return -2

    # appearance
    @property
    def primary_color(self) -> str | None:
        return self.get("appearance", "primary_color")

    @property
    def secondary_color(self) -> str | None:
        return self.get("appearance", "secondary_color")

    # plot
    @property
    def plot_colorscheme(self) -> str | None:
        return self.get("plot", "colorscheme")

    @property
    def plot_color_algorithm(self) -> str | None:
        return self.get("plot", "color_algorithm")

    @property
    def plot_color_scheme(self) -> str:
        return self.get("plot", "colorScheme") or "follow"

    @property
    def plot_bg(self) -> str | None:
        return self.get("plot", "bg")

    @property
    def plot_fg(self) -> str | None:
        return self.get("plot", "fg")

    @property
    def plot_line_style(self) -> str | None:
        return self.get("plot", "lineStyle")

    @property
    def plot_marker(self) -> str | None:
        return self.get("plot", "marker")

    @property
    def plot_line_width(self) -> float | None:
        val = self.get("plot", "lineWidth")
        try:
            return float(val) if val else None
        except (ValueError, TypeError):
            return None

    @property
    def plot_marker_size(self) -> float | None:
        val = self.get("plot", "markerSize")
        try:
            return float(val) if val else None
        except (ValueError, TypeError):
            return None

    @property
    def plot_grid(self) -> bool | None:
        val = self.get("plot", "grid")
        if val is None:
            return None
        return val == "true"

    @property
    def plot_grid_mode(self) -> str | None:
        return self.get("plot", "gridMode")

    @property
    def plot_grid_density(self) -> float | None:
        val = self.get("plot", "gridDensity")
        try:
            return float(val) if val else None
        except (ValueError, TypeError):
            return None

    @property
    def plot_grid_label_density(self) -> float | None:
        val = self.get("plot", "gridLabelDensity")
        try:
            return float(val) if val else None
        except (ValueError, TypeError):
            return None

    @property
    def plot_title_font_size(self) -> int | None:
        val = self.get("plot", "titleFontSize")
        try:
            return int(val) if val else None
        except (ValueError, TypeError):
            return None

    @property
    def plot_label_font_size(self) -> int | None:
        val = self.get("plot", "labelFontSize")
        try:
            return int(val) if val else None
        except (ValueError, TypeError):
            return None

    @property
    def plot_tick_font_size(self) -> int | None:
        val = self.get("plot", "tickFontSize")
        try:
            return int(val) if val else None
        except (ValueError, TypeError):
            return None

    @property
    def plot_legend_font_size(self) -> int | None:
        val = self.get("plot", "legendFontSize")
        try:
            return int(val) if val else None
        except (ValueError, TypeError):
            return None

    @property
    def plot_triangular_levels(self) -> int | None:
        val = self.get("plot", "triangular_levels")
        try:
            return int(val) if val else None
        except (ValueError, TypeError):
            return None

    @property
    def plot_triangular_alpha(self) -> float | None:
        val = self.get("plot", "triangular_alpha")
        try:
            return float(val) if val else None
        except (ValueError, TypeError):
            return None

    @property
    def plot_triangular_grid_alpha(self) -> float | None:
        val = self.get("plot", "triangular_grid_alpha")
        try:
            return float(val) if val else None
        except (ValueError, TypeError):
            return None

    @property
    def plot_triangular_grid_line_width(self) -> float | None:
        val = self.get("plot", "triangular_grid_line_width")
        try:
            return float(val) if val else None
        except (ValueError, TypeError):
            return None
