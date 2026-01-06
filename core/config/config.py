from typing import Dict, Any

from core.fio import loadConfig
from core.log import getLogger

logger = getLogger(__name__)

_config: Dict[str, Any] | None = None

def getConfigs() -> Dict[str, Any]:
    global _config

    if _config is None:
        _config = loadConfig()

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