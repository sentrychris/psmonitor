"""
--------------------------------------------------------------------------
PSMonitor - System and network monitoring utility

File: headless.py
Author: Chris Rowles <christopher.rowles@outlook.com>
Copyright: © 2025 Chris Rowles. All rights reserved.
Version: 1.6.0.1001
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
from core import create_server, signal_handler
from core.config import DEFAULT_PORT
from core.database_manager import init_db
from core.logging_manager import PSMonitorLogger


# Define command-line options
define('address', default='localhost', help='Listen address for the application')
define('port', default=DEFAULT_PORT, help='Listen port for the application', type=int)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    parse_command_line()

    # Create logger and clear log for new session
    logger = PSMonitorLogger("app.log")
    logger.clear_log()

    init_db(logger)

    http = create_server()
    http.listen(port=options.port, address=options.address)

    print(f"Listening on http://{options.address}:{options.port}")
    IOLoop.current().start()
