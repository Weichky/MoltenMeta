from pathlib import Path
import tomllib
from typing import Dict, Any
from core.log import getLogger

from importlib.resources import files

from core.platform import getRuntimePath

logger = getLogger("config loader")

# Traversable objects act the same as Path objects here.
DEFAULT_CONFIG = files("resources") / "default.toml"

# Donot use a user config file anymore,
# using sqlite database instead.
# USER_CONFIG = Path(__file__).resolve().parent.parent.parent/ "runtime" / "config.toml"
USER_CONFIG = getRuntimePath() / "config.toml"

def _mergeConfig(base: dict, override: dict) -> dict:
    result = base.copy()
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = _mergeConfig(result[k], v)
        else:
            result[k] = v

    return result

def loadConfig() -> Dict[str, Any]:
    logger.info("User config files are no longer used")

    with DEFAULT_CONFIG.open("rb") as f:
        base = tomllib.load(f)

    if not USER_CONFIG.exists():
        logger.warning("No user config found, using default config")
        logger.info("SQLite database will save user configs alternatively in the future")

    else:
        with USER_CONFIG.open("rb") as f:
            override = tomllib.load(f)
        base = _mergeConfig(base, override)

    return base