"""
--------------------------------------------------------------------------
PSMonitor - System and network monitoring utility

File: config.py
Author: Chris Rowles <christopher.rowles@outlook.com>
Copyright: © 2025 Chris Rowles. All rights reserved.
Version: 1.5.0.2413
License: MIT
--------------------------------------------------------------------------
"""

# Standard library imports
import json
import os
from typing import TYPE_CHECKING, Optional

# Typing (type hints only, no runtime dependency)
if TYPE_CHECKING:
    from core.logging_manager import PSMonitorLogger


# Default server address and port
DEFAULT_ADDRESS = "localhost"
DEFAULT_PORT = 4500

# Default max allowed websocket connections
DEFAULT_MAX_WS_CONNECTIONS = 20

# Default reconnection settings
DEFAULT_MAX_RECONNECT_ATTEMPTS = 3
DEFAULT_RECONNECT_BASE_DELAY = 0.5

# Default GUI widget update interval
DEFAULT_GUI_REFRESH_INTERVAL = 1000

# Default logging level and enabled state
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_ENABLED = True

# Settings path and full filepath (including filename).
SETTINGS_DIR = os.path.join(os.path.expanduser('~'), '.psmonitor')
SETTINGS_FILE = os.path.join(SETTINGS_DIR, "settings.json")


default_settings = {
    "logging_enabled": DEFAULT_LOG_ENABLED,
    "log_level": DEFAULT_LOG_LEVEL,
    "address": DEFAULT_ADDRESS,
    "port_number": DEFAULT_PORT,
    "max_ws_connections": DEFAULT_MAX_WS_CONNECTIONS,
    "max_reconnect_attempts": DEFAULT_MAX_RECONNECT_ATTEMPTS,
    "reconnect_base_delay": DEFAULT_RECONNECT_BASE_DELAY,
    "gui_refresh_interval": DEFAULT_GUI_REFRESH_INTERVAL
}


def read_settings_file(logger: 'PSMonitorLogger' = None) -> dict:
    """
    Read settings from file.
    """

    try:
        if not os.path.exists(SETTINGS_FILE):
            os.makedirs(SETTINGS_DIR, exist_ok=True)
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(default_settings, f, indent=4)
            if logger:
                logger.info("Created settings file at %s", SETTINGS_FILE)
            return default_settings

        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except (PermissionError, IsADirectoryError, json.JSONDecodeError) as e:
        if logger:
            logger.error("Failed to load or create settings file: %s", e)
        return default_settings


def get_setting(key: str, settings: Optional[dict] = None, default: Optional[str] = None):
    """
    Get a particular setting.
    """

    if settings is None:
        settings = read_settings_file()

    if isinstance(settings, dict):
        return settings.get(key, default)

    return default
