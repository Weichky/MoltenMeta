import io
import os
import sys
import json
from typing import Tuple, Dict, Any, Optional


def detect_environment() -> str:
    """
    Detect the current runtime environment.
    
    Returns:
        str: 'dev' for development environment, 'release' for production environment.
             Defaults to 'dev' if not specified.
    """
    return getattr(sys, 'moltenmeta_env', 'dev')


def get_config_path() -> str:
    """
    Get the configuration file path based on the environment.
    
    Returns:
        str: Path to the configuration file.
    """
    env = detect_environment()
    if env == 'dev':
        # In development environment, config file is in project root directory
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.json'))
    else:
        # In release environment, config file is in the same directory as executable
        if getattr(sys, 'frozen', False):
            # Packaged environment
            app_dir = os.path.dirname(sys.executable)
        else:
            # Regular release environment
            app_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(app_dir, 'config.json')


def load_config() -> Tuple[bool, Optional[Dict[Any, Any]]]:
    """
    Load configuration file.
    
    Returns:
        Tuple[bool, Optional[Dict[Any, Any]]]: First element indicates whether 
        the config file exists, second element is the config content (None if 
        file doesn't exist or failed to parse).
    """
    config_path = get_config_path()
    
    if not os.path.exists(config_path):
        return False, None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return True, config
    except (IOError, json.JSONDecodeError):
        # File read failure or JSON parsing error
        return True, None


# Backward compatibility alias
ConfigLoader = load_config