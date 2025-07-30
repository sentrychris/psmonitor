"""
--------------------------------------------------------------------------
PSMonitor - System and network monitoring utility

File: gui.py
Author: Chris Rowles <christopher.rowles@outlook.com>
Copyright: © 2025 Chris Rowles. All rights reserved.
Version: 1.6.0.1001
License: MIT
--------------------------------------------------------------------------
"""

# Standard library imports
import signal
import sys

# Local application imports
from core import signal_handler
from core.config import init_data, set_launch_mode
from core.logging_manager import PSMonitorLogger
from core.database_manager import PSMonitorDatabaseManager
from core.server_manager import PSMonitorServerManager
from gui.app_manager import PSMonitorApp


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    set_launch_mode("gui")

    # Create logger and clear log for new session
    logger = PSMonitorLogger("app.log")
    logger.clear_log()

    # Initialize DB if it hasn't already been initialized
    db = PSMonitorDatabaseManager(logger)
    db.initialize()

    # Create server manager to handle threaded server
    server_manager = PSMonitorServerManager(logger)

    try:
        server_manager.start()
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

    app = PSMonitorApp(init_data, server_manager, logger)
    app.mainloop()
