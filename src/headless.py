"""
PSMonitor - A simple system monitoring utility
Author: Chris Rowles
Copyright: © 2025 Chris Rowles. All rights reserved.
License: MIT
"""

# Standard library imports
import uuid
import os
import signal

# Third-party imports
from tornado.httpserver import HTTPServer
from tornado.options import define, options, parse_command_line
from tornado.ioloop import IOLoop

# Local application imports
from core import create_app, signal_handler


# Constants
BASE_DIR = os.path.dirname(__file__)
TEMPLATE_PATH = os.path.join(BASE_DIR, 'gui', 'web')
STATIC_PATH = os.path.join(BASE_DIR, 'gui', 'web')
COOKIE_SECRET = uuid.uuid1().hex


# Define command-line options
define('address', default='localhost', help='Listen address for the application')
define('port', default=4500, help='Listen port for the application', type=int)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    parse_command_line()

    http = HTTPServer(create_app({
        'template_path': TEMPLATE_PATH,
        'static_path': STATIC_PATH,
        'cookie_secret': COOKIE_SECRET,
        'xsrf_cookies': False,
        'debug': True
    }))
    http.listen(port=options.port, address=options.address)

    print(f"Listening on http://{options.address}:{options.port}")
    IOLoop.current().start()
