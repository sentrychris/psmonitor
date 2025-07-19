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
from typing import TYPE_CHECKING, Union

# Typing (type hints only, no runtime dependency)
if TYPE_CHECKING:
    from core.logging_manager import PSMonitorLogger



def read_settings_file(logger: 'PSMonitorLogger') -> Union[dict, bool]:
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
        logger.error("Failed to load settings from file: %s", e)
        return False
