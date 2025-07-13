import sys
from tornado.ioloop import IOLoop
from tornado.web import Application
from typing import Union
from .handler.http.http import HttpHandler, HttpSystemHandler, HttpNetworkHandler
from .handler.websocket.websocket import WebsocketHandler
from .thread_pool import executor


def signal_handler(sig, frame):
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
