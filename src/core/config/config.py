from typing import Dict, Any

from core.fio import _loadConfig
from core.log import getLogger

logger = getLogger(__name__)

_config: Dict[str, Any] | None = None

def loadConfig() -> None:
    global _config

    _config = _loadConfig()

def getConfigs() -> Dict[str, Any]:
    global _config

    if _config is None:
        loadConfig()

    return _config

def getConfig(key: str) -> Any:
    global _config

    if _config is None:
        raise RuntimeError("Config system not initialized")
    
    try:
        return _config[key]
    except KeyError:
        raise RuntimeError(f"Config key {key} not found")
    
def setConfig(key: str, value: Any):
    global _config

    if _config is None:
        raise RuntimeError("Config system not initialized")
    
    _config[key] = value

def getLanguage() -> str:
    return getConfig("locale")["language"]

def setLanguage(language: str):
    setConfig("locale", {"language": language})

def getLogLevel() -> str:
    return getConfig("logging")["level"]

def getThemeName() -> str:
    return getConfig("locale")["scheme"] + "_" + getConfig("locale")["theme"]

def getThemeXML() -> str:
    return getThemeName() + ".xml"

def getScheme() -> str:
    return getConfig("locale")["scheme"]