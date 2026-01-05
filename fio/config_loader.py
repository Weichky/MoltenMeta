from pathlib import Path
import tomllib
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_CONFIG = BASE_DIR / "assets" / "config.toml"
USER_CONFIG = BASE_DIR / "config.toml"

_config: Dict[str, Any] | None = None

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

    if USER_CONFIG.exists():
        with USER_CONFIG.open("rb") as f:
            override = tomllib.load(f)
        return mergeConfig(base, override)

    return base

def getConfig() -> Dict[str, Any]:
    global _config
    if _config is None:
        _config = loadConfig()
        
    return _config