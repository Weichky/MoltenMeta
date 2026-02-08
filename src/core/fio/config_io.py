from pathlib import Path
import tomllib
from typing import Dict, Any
from core.log import getLogService

from importlib.resources import files

from core.platform import getRuntimePath

# Traversable objects act the same as Path objects here.
DEFAULT_CONFIG = files("resources.default") / "default.toml.old"

# Donot use a user config file anymore,
# using sqlite database instead.
# USER_CONFIG = Path(__file__).resolve().parent.parent.parent/ "runtime" / "config.toml"
USER_CONFIG = getRuntimePath() / "config.toml" if getRuntimePath() else None

def _getLogger() -> 'logging'.Logger:
    return getLogService().getLogger(__name__)

def _mergeConfig(base: dict, override: dict) -> dict:
    result = base.copy()
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = _mergeConfig(result[k], v)
        else:
            result[k] = v

    return result
# Shouldnot be used at elsewhere but config.py
def _loadConfig() -> Dict[str, Any]:
    logger = _getLogger()

    logger.debug("User config files are no longer used")

    with DEFAULT_CONFIG.open("rb") as f:
        base = tomllib.load(f)

    if not USER_CONFIG:
        logger.warning("No runtime path given, using default config")
        return base

    if not USER_CONFIG.exists():
        logger.warning("No user config found, using default config")
        logger.debug("SQLite database will save user configs alternatively in the future")

    else:
        with USER_CONFIG.open("rb") as f:
            override = tomllib.load(f)
        base = _mergeConfig(base, override)

    return base