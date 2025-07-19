"""
--------------------------------------------------------------------------
PSMonitor - A simple system monitoring utility
Author: Chris Rowles
Copyright: © 2025 Chris Rowles. All rights reserved.
License: MIT
--------------------------------------------------------------------------
"""

# Standard library imports
import signal
import sys

# Local application imports
from core import signal_handler
from core.app_logger import PSMonitorLogger
from core.server_manager import PSMonitorServerManager
from gui.app_manager import PSMonitorApp


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Logger
    logger = PSMonitorLogger("app.log")

    # Server manager instance
    server_manager = PSMonitorServerManager(logger)

    try:
        server_manager.start(port=4500, max_connections=100)  # example max_connections
    except Exception as e: # pylint: disable=broad-except
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

    init_data = {
        "cpu": {"usage": 0.0, "temp": 0, "freq": 0},
        "mem": {"total": 0, "used": 0, "free": 0, "percent": 0},
        "disk": {"total": 0, "used": 0, "free": 0, "percent": 0},
        "user": "",
        "platform": {"distro": "", "kernel": "", "uptime": ""},
        "uptime": "",
        "processes": []
    }

    app = PSMonitorApp(init_data, server_manager, logger)
    app.mainloop()
