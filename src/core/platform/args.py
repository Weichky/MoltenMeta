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

from logging import getLogger

logger = getLogger(__name__)

runtimepath_cache = None

def getRuntimePath() -> Path:
    """
    Resolve runtime root directory in a robust and portable way.

    Priority:
    1. Cache
    2. CLI override (--runtime-path)
    3. Executable location (most reliable across Nuitka / onefile / standalone)
    4. Runtime Error if all else fails
    """

    global runtimepath_cache

    if runtimepath_cache is not None:
        if runtimepath_cache.exists():
            return runtimepath_cache
        else:
            logger.warning(f"[RuntimePath] Cache path does not exist: {runtimepath_cache}")
            runtimepath_cache = None
        
    # 2. CLI override
    try:
        arg_path = getArgs().runtime_path
        if arg_path:
            p = Path(arg_path).resolve()
            runtimepath_cache = p
            if p.exists():
                logger.info(f"[RuntimePath] Using CLI override: {p}")
                return p
            logger.warning(f"[RuntimePath] CLI path does not exist: {p}")
    except Exception as e:
        logger.warning(f"[RuntimePath] CLI parse failed: {e}")

    # 3. Runtime anchor: argv[0] (MOST IMPORTANT)
    try:
        exe_path = Path(sys.argv[0]).resolve()
        runtime_path = exe_path.parent

        logger.info(f"[RuntimePath] argv[0]: {exe_path}")
        logger.info(f"[RuntimePath] resolved runtime root: {runtime_path}")
    
        runtimepath_cache = runtime_path

        return runtime_path

    except Exception as e:
        logger.warning(f"[RuntimePath] argv[0] resolution failed: {e}")
        
    raise RuntimeError("Failed to resolve runtime path. Please specify with --runtime-path or ensure executable is properly located.")