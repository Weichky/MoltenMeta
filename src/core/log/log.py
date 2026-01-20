import logging

from catalog import LogLevel

def getLogLevelMap() -> dict[str, int]:
    return {
        lvl.value: getattr(logging, lvl.name)
        for lvl in LogLevel
    }