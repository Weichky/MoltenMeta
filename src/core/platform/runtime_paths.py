import argparse
from typing import Optional

_args: Optional[argparse.Namespace] = None

def init_args(argv=None) -> argparse.Namespace:
    global _args
    if _args is None:
        parser = argparse.ArgumentParser()
        parser.add_argument("--debug", action="store_true")
        parser.add_argument("--runtime-path")
        _args = parser.parse_args(argv)
    return _args

def getArgs() -> argparse.Namespace:
    if _args is None:
        raise RuntimeError("Arguments not initialized. Call init_args() first.")
    return _args
