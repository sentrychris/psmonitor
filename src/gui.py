"""
--------------------------------------------------------------------------
PSMonitor - System and network monitoring utility

File: gui.py
Author: Chris Rowles
Copyright: © 2025 Chris Rowles. All rights reserved.
Version: 1.5.0.2413
License: MIT
--------------------------------------------------------------------------
"""

# Standard library imports
import signal
import sys

# Local application imports
from core import signal_handler
from core.logging_manager import PSMonitorLogger
from core.server_manager import PSMonitorServerManager
from gui.app_manager import PSMonitorApp


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create logger and clear log for new session
    logger = PSMonitorLogger("app.log")
    logger.clear_log()

    # Create server manager to handle threaded server
    server_manager = PSMonitorServerManager(logger)

    try:
        server_manager.start()
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

    # Create placeholder data to intialise GUI widgets
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
