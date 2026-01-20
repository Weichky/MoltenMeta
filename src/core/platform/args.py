import argparse
from typing import Optional
from pathlib import Path

from core.log import LogLevel

_args: Optional[argparse.Namespace] = None

def _initArgs(argv=None) -> argparse.Namespace:
    global _args
    if _args is None:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug"
            )
        
        parser.add_argument(
            "--runtime-path",
            help="Set a path to the runtime directory"
        )

        parser.add_argument(
            "--log-level",
            choices=[level.value for level in LogLevel],
            help="Set the log level"
        )
        _args = parser.parse_args(argv)
    return _args

def getArgs() -> argparse.Namespace:
    if _args is None:
        _initArgs()
    return _args

def getRuntimePath() -> Path:
    return Path(getArgs().runtime_path).resolve() if getArgs().runtime_path else None