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
import queue
import threading
from typing import TYPE_CHECKING

# Third-party imports
from tornado.ioloop import IOLoop

# Local application imports
from core import create_server

if TYPE_CHECKING:
    from logger import ThreadSafeLogger


class TornadoServerManager:
    """
    Manages a Tornado HTTP server running in a background thread.

    Provides start, stop, and restart functionality with thread-safe control
    over the Tornado IOLoop and server lifecycle.
    """

    def __init__(self, logger: 'ThreadSafeLogger' = None):
        """
        Initializes the TornadoServerManager with default state.
        """
        self.logger = logger

        self.thread = None
        self.ioloop = None
        self.http_server = None
        self.server_queue = queue.Queue()
        self.started_event = threading.Event()
        self.port = None
        self.max_connections = None
        self.lock = threading.Lock()


    def _server_thread(self, port, max_connections, queue_, started_event):
        """
        The target function for the server thread.

        Args:
            port (int): Port to listen on.
            max_connections (int | None): Maximum number of connections if supported.
            queue_ (queue.Queue): Queue to send the HTTP server instance back to main thread.
            started_event (threading.Event): Event to signal when server is ready.
        """
        self.ioloop = IOLoop()

        # Pass max_connections to create_server if supported by your implementation
        self.http_server = create_server(os.path.join(os.path.dirname(__file__), 'gui', 'web'))
        self.http_server.listen(port, address="localhost")

        queue_.put(self.http_server)

        def on_start():
            self.logger.debug(
                f"Tornado server thread started: {threading.current_thread().name} "
                f"(ID: {threading.get_ident()})"
            )
            started_event.set()

        self.ioloop.add_callback(on_start)
        self.ioloop.start()


    def start(self, port, max_connections=5):
        """
        Starts the Tornado server in a new thread.

        Blocks until the server signals it is ready.

        Args:
            port (int): Port to listen on.
            max_connections (int): Optional maximum number of connections.

        Raises:
            RuntimeError: If server is already running.
        """
        with self.lock:
            if self.thread and self.thread.is_alive():
                raise RuntimeError("Server already running")
            self.port = port
            self.max_connections = max_connections
            self.server_queue = queue.Queue()
            self.started_event = threading.Event()

            self.thread = threading.Thread(
                target=self._server_thread,
                args=(port, max_connections, self.server_queue, self.started_event),
                daemon=True,
                name="TornadoServerThread",
            )
            self.thread.start()

            # Wait for server to signal it is ready
            started = self.started_event.wait(timeout=5)
            if not started:
                raise TimeoutError("Server failed to start within timeout")
            self.http_server = self.server_queue.get()


    def stop(self):
        """
        Stops the Tornado server and waits for thread to finish.

        Does nothing if the server is not running.
        """

        with self.lock:
            if self.thread and self.thread.is_alive() and self.ioloop:
                if self.http_server:
                    self.logger.info("Tornado server is shutting down...")
                    self.http_server.stop()
                self.ioloop.add_callback(self.ioloop.stop)
                self.thread.join(timeout=5)
                self.thread = None
                self.ioloop = None
                self.http_server = None
                self.logger.info("Tornado server thread terminated...")


    def restart(self, port, max_connections=5):
        """
        Restarts the server with new parameters.

        Args:
            port (int): Port to listen on.
            max_connections (int): Optional maximum number of connections.
        """

        self.stop()
        self.start(port, max_connections)
