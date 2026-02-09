import tomllib
from importlib.resources import files
from typing import Any

from domain.snapshot import SettingsSnapshot
from domain.settings import serializeSettingValue

DEFAULT_SETTINGS_PATH = files("resources.default") / "default_settings.toml"

def loadDefaultSettings() -> list[SettingsSnapshot]:
    with open(DEFAULT_SETTINGS_PATH, "rb") as f:
        settings = tomllib.load(f)

    snapshots : list[SettingsSnapshot] = []

    for section, kv_pairs in settings.items():
        for key, value in kv_pairs.items():
            snapshots.append(
                SettingsSnapshot(
                    section=section,
                    key=key,
                    value=serializeSettingValue(value))
            )

    return snapshots