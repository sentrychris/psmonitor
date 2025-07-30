"""
--------------------------------------------------------------------------
PSMonitor - System and network monitoring utility

File: worker.py
Author: Chris Rowles <christopher.rowles@outlook.com>
Copyright: © 2025 Chris Rowles. All rights reserved.
Version: 1.6.0.1001
License: MIT
--------------------------------------------------------------------------
"""

# Standard library imports
import secrets

# Third-party imports
from tornado.ioloop import IOLoop

# Local application imports
from core.server.websocket.websocket_handler import WebsocketHandler


class Worker():
    """
    Worker class for managing worker instances within a worker pool.

    This class represents a worker that can be associated with a WebSocket handler and
    manages its I/O loop operations.

    Attributes:
        id (str): A unique identifier for the worker instance.
        subscriber (str): The UUID representing the subscriber for this worker instance.
        handler (WebSocketHandler): The WebSocket handler associated with this worker.
        loop (IOLoop): The current IOLoop instance.
        mode (int): The I/O loop mode, default is IOLoop.READ.
    """


    def __init__(self, subscriber: str):
        """
        Initializes the Worker instance.

        Sets the current IOLoop, generates a unique ID for the worker, and initializes
        the handler and mode attributes.
        """

        self.id = str(secrets.token_urlsafe(32))
        self.subscriber = subscriber
        self.handler = None
        self.loop = IOLoop.current()
        self.mode = IOLoop.READ


    def set_handler(self, handler: WebsocketHandler):
        """
        Sets the WebSocket handler for the worker.

        Associates the given handler with this worker if no handler is currently set.

        Args:
            handler (WebSocketHandler): The WebSocket handler to be associated with this worker.
        """

        if not self.handler:
            self.handler = handler


    def close(self):
        """
        Closes the associated WebSocket handler.

        If a handler is set, this method closes the handler to clean up the connection.
        """

        if self.handler:
            self.handler.close()
