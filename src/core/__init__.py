"""
--------------------------------------------------------------------------
PSMonitor - System and network monitoring utility

File: __init__.py
Author: Chris Rowles <christopher.rowles@outlook.com>
Copyright: © 2025 Chris Rowles. All rights reserved.
Version: 1.6.0.1001
License: MIT
--------------------------------------------------------------------------
"""

# Standard library imports
import uuid
import sys
from typing import TYPE_CHECKING

# Third-party imports
from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.httpserver import HTTPServer

# Local application imports
from core.server.http.http_handler import HttpAuthHandler, HttpWorkerHandler, \
    HttpSystemHandler, HttpNetworkHandler
from core.server.websocket.websocket_handler import WebsocketHandler
from core.thread_pool import executor

# Type checking
if TYPE_CHECKING:
    from core.database_manager import PSMonitorDatabaseManager
    from core.logging_manager import PSMonitorLogger


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


def create_server(db: 'PSMonitorDatabaseManager', logger: 'PSMonitorLogger') -> HTTPServer:
    """
    Create a server
    """

    return HTTPServer(create_app({
        'cookie_secret': uuid.uuid1().hex,
        'xsrf_cookies': False,
        'debug': False,
        'db': db,
        'logger': logger
    }))


def create_app(settings: dict) -> Application | bool:
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
        (r'/authenticate', HttpAuthHandler),
        (r'/worker', HttpWorkerHandler),
        (r'/system', HttpSystemHandler),
        (r'/network', HttpNetworkHandler),
        (r'/connect', WebsocketHandler),
    ]

    return Application(handlers, **settings)
