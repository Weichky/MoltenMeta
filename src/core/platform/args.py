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


def getRuntimePath() -> Path:
    """
    Retrieves the base execution directory. 
    Priority: 
    1. Command line argument --runtime-path
    2. Executable directory (if compiled via Nuitka/PyInstaller)
    3. Current working directory (if running as source)
    """
    # Attempt to get path from custom arguments (assumes getArgs() is defined)
    try:
        runtime_path = getArgs().runtime_path
    except (NameError, AttributeError):
        runtime_path = None

    if not runtime_path:
        # Check if the script is compiled (Nuitka adds __compiled__ to globals)
        if "__compiled__" in globals() or getattr(sys, 'frozen', False):
            # sys.executable points to the actual .exe file
            runtime_path = Path(sys.executable).parent
        else:
            # Fallback for source development (.py)
            # You can also use Path(__file__).resolve().parent.parent if preferred
            runtime_path = Path.cwd()

    return Path(runtime_path).resolve()