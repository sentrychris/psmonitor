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
    from core.app_logger import PSMonitorLogger


# pylint: disable=too-many-instance-attributes
# the number of attributes is reasonable in this case.
class PSMonitorServerManager:
    """
    Manages a Tornado HTTP server running in a background thread.
    """

    def __init__(self, logger: 'PSMonitorLogger' = None):
        """
        Initializes the server manager with default state.
        """

        self.logger = logger

        self.thread = None
        self.ioloop = None
        self.http_server = None
        self.server_queue = queue.Queue()
        self.started_event = threading.Event()
        self.port = None
        self.lock = threading.Lock()


    def _server_thread(self, port, queue_, started_event):
        """
        The target function for the server thread.

        Args:
            port (int): Port to listen on.
            queue_ (queue.Queue): Queue to send the HTTP server instance back to main thread.
            started_event (threading.Event): Event to signal when server is ready.
        """

        self.ioloop = IOLoop()

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


    def start(self, port):
        """
        Starts the Tornado server in a new thread.

        Waits until the server signals it is ready.

        Args:
            port (int): Port to listen on.

        Raises:
            RuntimeError: If server is already running.
        """

        with self.lock:
            if self.thread and self.thread.is_alive():
                raise RuntimeError("Server already running")
            self.port = port
            self.server_queue = queue.Queue()
            self.started_event = threading.Event()

            self.thread = threading.Thread(
                target=self._server_thread,
                args=(port, self.server_queue, self.started_event),
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
                    self.logger.debug("Tornado server is shutting down...")
                    self.http_server.stop()

                self.ioloop.add_callback(self.ioloop.stop)
                self.thread.join(timeout=5)
                self.thread = None
                self.ioloop = None
                self.http_server = None
                self.logger.debug("Tornado server thread terminated...")


    def restart(self, port):
        """
        Restarts the server with new parameters.

        Args:
            port (int): Port to listen on.
        """

        self.stop()
        self.start(port)
