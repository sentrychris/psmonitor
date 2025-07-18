"""
--------------------------------------------------------------------------
PSMonitor - A simple system monitoring utility
Author: Chris Rowles
Copyright: © 2025 Chris Rowles. All rights reserved.
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


# Define command-line options
define('address', default='localhost', help='Listen address for the application')
define('port', default=4500, help='Listen port for the application', type=int)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    parse_command_line()

    http = create_server(os.path.join(os.path.dirname(__file__), 'gui', 'web'))
    http.listen(port=options.port, address=options.address)

    print(f"Listening on http://{options.address}:{options.port}")
    IOLoop.current().start()
