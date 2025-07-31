"""
--------------------------------------------------------------------------
PSMonitor - System and network monitoring utility

File: headless.py
Author: Chris Rowles <christopher.rowles@outlook.com>
Copyright: © 2025 Chris Rowles. All rights reserved.
Version: 2.0.0.1011
License: MIT
--------------------------------------------------------------------------
"""

# Standard library imports
import os
import signal

# Third-party imports
from tornado.options import define, options, parse_command_line
from tornado.ioloop import IOLoop

# Local application imports
from core import signal_handler, create_server
from core.config import DEFAULT_PORT, set_launch_mode
from core.auth import write_credentials_file
from core.logging_manager import PSMonitorLogger
from core.database_manager import PSMonitorDatabaseManager


# Define command-line options
define("address", default="localhost", help="Listen address for the application")
define("port", default=DEFAULT_PORT, help="Listen port for the application", type=int)
define("export-credentials", default=False, help="Export connection credentials to file", type=bool)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    set_launch_mode("headless")

    parse_command_line()

    # Create logger and clear log for new session
    logger = PSMonitorLogger("app.log")
    logger.clear_log()

    # Initialize DB if it hasn't already been initialized
    db = PSMonitorDatabaseManager(logger)
    db.initialize()

    # Export connection credentials for the user
    if options.export_credentials:
        credentials_file = write_credentials_file()
        if not credentials_file:
            logger.error("Failed to write credentials file")
        logger.info(f"Connection credentials have been written to {credentials_file}")
        logger.info("Note: File will be deleted automatically after first connection.")

    http = create_server(db, logger, os.path.join(os.path.dirname(__file__), 'gui', 'web'))
    http.listen(port=options.port, address=options.address)

    logger.info(f"Listening on http://{options.address}:{options.port}")
    IOLoop.current().start()
