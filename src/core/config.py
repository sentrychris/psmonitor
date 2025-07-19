"""
--------------------------------------------------------------------------
PSMonitor - A simple system monitoring utility
Author: Chris Rowles
Copyright: © 2025 Chris Rowles. All rights reserved.
License: MIT
--------------------------------------------------------------------------
"""

# Standard library imports
import json
import os
from typing import TYPE_CHECKING, Optional, Union

# Typing (type hints only, no runtime dependency)
if TYPE_CHECKING:
    from core.logging_manager import PSMonitorLogger


# Default settings path and full filepath (including filename).
DEFAULT_SETTINGS_FILEPATH = os.path.join(os.path.expanduser('~'), '.psmonitor')
DEFAULT_SETTINGS_FILE = os.path.join(DEFAULT_SETTINGS_FILEPATH, "settings.json")

# Default server address and port
DEFAULT_ADDRESS = "localhost"
DEFAULT_PORT = 4500

# Default max allowed websocket connections
DEFAULT_MAX_WS_CONNECTIONS = 20

# Default GUI widget update interval
DEFAULT_REFRESH_INTERVAL = 1000

# Default logging level and enabled state
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_ENABLED = True


def read_settings_file(logger: 'PSMonitorLogger' = None) -> Union[dict, bool]:
    """
    Read settings from file.
    """

    try:
        settings_file = os.path.join(
            os.path.join(os.path.expanduser('~'), '.psmonitor'),
            "settings.json"
        )

        with open(settings_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data
    except (FileNotFoundError, PermissionError, IsADirectoryError) as e:
        if logger:
            logger.error("Failed to load settings from file: %s", e)
        return False


def get_setting(key: str, settings: Optional[dict] = None, default: Optional[str] = None):
    """
    Get a particular setting.
    """

    if settings is None:
        settings = read_settings_file()

    if isinstance(settings, dict):
        return settings.get(key, default)

    return default
