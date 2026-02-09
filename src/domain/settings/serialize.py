from typing import Any

def serializeSettingValue(val: Any) -> str:
    if isinstance(val, bool):
        return "true" if val else "false"
    return str(val)