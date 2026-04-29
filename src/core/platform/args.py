import argparse
import sys
from pathlib import Path

from core.log import LogLevel

_args: argparse.Namespace | None = None


def _initArgs(argv=None) -> argparse.Namespace:
    global _args
    if _args is None:
        parser = argparse.ArgumentParser()
        parser.add_argument("--debug", action="store_true", help="Enable debug")

        parser.add_argument(
            "--runtime-path", help="Set a path to the runtime directory"
        )

        parser.add_argument(
            "--log-level",
            choices=[level.value for level in LogLevel],
            help="Set the log level",
        )
        _args = parser.parse_args(argv)
    return _args


def getArgs() -> argparse.Namespace:
    if _args is None:
        _initArgs()
    return _args


import sys
import os
from pathlib import Path

def getRuntimePath() -> Path:
    """
    Retrieves the base execution directory (the 'runtime' folder).
    """
    # 1. Prioritize command-line arguments (Explicit is better than implicit)
    try:
        arg_path = getArgs().runtime_path
        if arg_path:
            return Path(arg_path).resolve()
    except Exception:
        pass

    # 2. Check if running in a packaged environment (Nuitka / PyInstaller)
    # Checking for specific flags in sys.modules is more robust than checking globals()
    is_compiled = "__nuitka__" in sys.modules or getattr(sys, 'frozen', False)

    if is_compiled:
        # In "Onefile" mode, sys.executable always points to the physical location of the .exe file.
        # Regardless of which cache folder the code was unpacked into, this will always return the /runtime/ directory.
        return Path(sys.executable).parent.resolve()

        # 3. Fallback logic for source code development environments
        # It is recommended *not* to use Path.cwd(), as running commands from different directories would lead to inconsistent results.
        # It is recommended to use the location of main.py as the baseline (assuming main.py resides in the src/ directory).
    return Path(__file__).resolve().parent.parent # Points to the project root directory