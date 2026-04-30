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
from logging import getLogger

logger = getLogger(__name__)
logger.warning("=== Runtime Environment Debug ===")

# 1. Execution identity
logger.warning(f"sys.executable: {sys.executable}")
logger.warning(f"sys.argv: {sys.argv}")
logger.warning(f"cwd: {Path.cwd()}")

# 2. Compilation detection flags
logger.warning(f"__nuitka__ in sys.modules: {'__nuitka__' in sys.modules}")
logger.warning(f"sys.frozen: {getattr(sys, 'frozen', None)}")
logger.warning(f"hasattr(sys, '__compiled__'): {hasattr(sys, '__compiled__')}")

# 3. File context (VERY IMPORTANT)
logger.warning(f"__file__: {__file__}")
logger.warning(f"resolved __file__: {Path(__file__).resolve()}")

# 4. Inspect module location (to detect if running from build dir)
try:
    import core.platform.args as this_module
    logger.warning(f"module __file__: {this_module.__file__}")
except Exception as e:
    logger.warning(f"module inspection failed: {e}")

# 5. sys.path snapshot (only first few to avoid spam)
for i, p in enumerate(sys.path[:5]):
    logger.warning(f"sys.path[{i}]: {p}")

# 6. Environment hints
logger.warning(f"PATH (truncated): {os.environ.get('PATH', '')[:200]}")

# 7. Dist structure probe
exe_dir = Path(sys.executable).resolve().parent
logger.warning(f"exe_dir exists: {exe_dir.exists()}")
logger.warning(f"exe_dir: {exe_dir}")

for name in ["modules", "resources", "core"]:
    p = exe_dir / name
    logger.warning(f"{name} exists at exe_dir: {p.exists()} -> {p}")

logger.warning("=== End Runtime Debug ===")

def getRuntimePath() -> Path:
    """
    Resolve the runtime root directory in a robust and consistent way.

    Priority:
    1. Explicit CLI argument (--runtime-path)
    2. Packaged environment (Nuitka / PyInstaller) → directory of executable
    3. Development fallback → project root inferred from this file

    The returned path is always expected to contain runtime resources such as:
    - modules/
    - resources/
    """

    # 1. Explicit override from CLI arguments
    try:
        arg_path = getArgs().runtime_path
        if arg_path:
            path = Path(arg_path).resolve()
            if path.exists():
                return path
            else:
                logger.warning(f"[RuntimePath] Provided runtime_path does not exist: {path}")
    except Exception as e:
        logger.warning(f"[RuntimePath] Failed to read CLI runtime_path: {e}")

    # 2. Detect packaged environment (Nuitka / PyInstaller)
    try:
        is_compiled = "__nuitka__" in sys.modules or getattr(sys, "frozen", False)

        if is_compiled:
            exe_path = Path(sys.executable).resolve()
            runtime_path = exe_path.parent

            if runtime_path.exists():
                return runtime_path
            else:
                logger.warning(f"[RuntimePath] Executable parent does not exist: {runtime_path}")

    except Exception as e:
        logger.warning(f"[RuntimePath] Failed to resolve packaged runtime path: {e}")

    # 3. Development fallback
    try:
        # Assume this file is located at: src/core/platform/args.py
        # Project root = go up 3 levels → src/ → project root
        dev_path = Path(__file__).resolve().parents[3]

        if dev_path.exists():
            logger.warning(f"[RuntimePath] Falling back to development path: {dev_path}")
            return dev_path
        else:
            logger.warning(f"[RuntimePath] Development path does not exist: {dev_path}")

    except Exception as e:
        logger.warning(f"[RuntimePath] Failed to resolve development path: {e}")

    # 4. Final fallback (last resort)
    cwd = Path.cwd().resolve()
    logger.warning(f"[RuntimePath] Falling back to current working directory: {cwd}")
    return cwd