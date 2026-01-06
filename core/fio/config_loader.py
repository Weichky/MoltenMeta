from pathlib import Path
import tomllib
from typing import Dict, Any
from core.log import getLogger

logger = getLogger("config loader")

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DEFAULT_CONFIG = BASE_DIR / "assets" / "config.toml"
USER_CONFIG = BASE_DIR / "config.toml"

def mergeConfig(base: dict, override: dict) -> dict:
    result = base.copy()
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = mergeConfig(result[k], v)
        else:
            result[k] = v

    return result

def loadConfig() -> Dict[str, Any]:
    with DEFAULT_CONFIG.open("rb") as f:
        base = tomllib.load(f)

    if not USER_CONFIG.exists():
        logger.warning("No user config found, using default config")

    else:
        with USER_CONFIG.open("rb") as f:
            override = tomllib.load(f)
        base = mergeConfig(base, override)

    return base