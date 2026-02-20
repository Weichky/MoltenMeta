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
    def theme(self) -> str:
        return self.get("appearance", "theme")

    @property
    def scheme(self) -> str:
        return self.get("appearance", "scheme")

    @property
    def enable_auto_dark_mode(self) -> bool:
        return self.get("appearance", "enable_auto_dark_mode") == "true"
    
    # Combined Methods
    @property
    def theme_XML(self) -> str:
        return self.get("appearance", "scheme") + "_" + self.get("appearance", "theme") + ".xml"
