"""
PSMonitor - A simple system monitoring utility
Author: Chris Rowles
Copyright: © 2025 Chris Rowles. All rights reserved.
License: MIT
"""

# Standard library imports
import sys
from typing import Union

# Third-party imports
from tornado.ioloop import IOLoop
from tornado.web import Application

# Local application imports
from core.handler.http.http_handler import HttpHandler, HttpSystemHandler, HttpNetworkHandler
from core.handler.websocket.websocket_handler import WebsocketHandler
from core.thread_pool import executor


def signal_handler(_sig, _frame):
    """
    Signal handler for graceful shutdown of the application.

    Args:
        sig (int): The signal number that triggered this handler.
        frame (FrameType): The current stack frame (not used in this handler).
    """

    print('Shutting down gracefully...')
    IOLoop.current().stop()
    executor.shutdown(wait=True)
    sys.exit(0)


def create_app(settings: dict) -> Union[Application, bool]:
    """
    Creates and returns an application instance with specified settings.

    Args:
        settings (dict): Configuration settings for the application. 

    Returns:
        tornado.web.Application or bool: 
            - Returns an instance configured with HTTP and websocket handlers.

    Raises:
        TypeError: If `settings` is not a dictionary or `None`.

    Example:
        settings = {
            'debug': True,
            'static_path': '/path/to/static',
            'template_path': '/path/to/templates'
        }
        app = create_app(settings)
    """

    handlers = [
        (r'/', HttpHandler),
        (r'/system', HttpSystemHandler),
        (r'/network', HttpNetworkHandler),
        (r'/connect', WebsocketHandler),
    ]

    return Application(handlers, **settings)
