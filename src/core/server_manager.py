"""
--------------------------------------------------------------------------
PSMonitor - System and network monitoring utility

File: server_manager.py
Author: Chris Rowles <christopher.rowles@outlook.com>
Copyright: © 2025 Chris Rowles. All rights reserved.
Version: 1.6.0.1001
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
import core.config as cfg
from core import create_server

# Typing (type hints only, no runtime dependency)
if TYPE_CHECKING:
    from core.logging_manager import PSMonitorLogger


class PSMonitorServerManager:
    """
    Manages a Tornado HTTP server running in a background thread.
    """

    def __init__(self, logger: 'PSMonitorLogger' = None):
        """
        Initializes the server manager with default state.
        """

        self._logger = logger

        self.port = cfg.DEFAULT_PORT
        self.address = cfg.DEFAULT_ADDRESS

        self.load_settings()

        self._thread = None
        self._ioloop = None
        self._server = None
        self._server_queue = queue.Queue()
        self._started_event = threading.Event()

        self._lock = threading.Lock()


    def _server_thread(self, port, queue_, started_event):
        """
        The target function for the server thread.

        Args:
            port (int): Port to listen on.
            queue_ (queue.Queue): Queue to send the HTTP server instance back to main thread.
            started_event (threading.Event): Event to signal when server is ready.
        """

        self._ioloop = IOLoop()

        base_dir = os.path.dirname(os.path.dirname(__file__))
        self._server = create_server(os.path.join(base_dir, 'gui', 'web'))
        self._server.listen(port, address=self.address)

        queue_.put(self._server)

        def on_start():
            self._logger.debug(
                f"Tornado server thread started: {threading.current_thread().name} "
                f"(ID: {threading.get_ident()})"
            )
            self._logger.info(f"Tornado server listening on http://{self.address}:{port}")
            started_event.set()

        self._ioloop.add_callback(on_start)
        self._ioloop.start()


    def start(self, port = None):
        """
        Starts the Tornado server in a new thread.

        Waits until the server signals it is ready.

        Args:
            port (int|None): Port to listen on.

        Raises:
            RuntimeError: If server is already running.
        """

        # If port is not overridden then use the server manager's port
        # which is assigned from load_settings() or DEFAULT_PORT
        if port is None:
            port = self.port

        with self._lock:
            if self._thread and self._thread.is_alive():
                raise RuntimeError("Server already running")
            self._server_queue = queue.Queue()
            self._started_event = threading.Event()

            self._thread = threading.Thread(
                target=self._server_thread,
                args=(port, self._server_queue, self._started_event),
                daemon=True,
                name="TornadoServerThread",
            )
            self._thread.start()

            # Wait for server to signal it is ready
            started = self._started_event.wait(timeout=5)
            if not started:
                raise TimeoutError("Server failed to start within timeout")

            self._server = self._server_queue.get()


    def stop(self):
        """
        Stops the Tornado server and waits for thread to finish.

        Does nothing if the server is not running.
        """

        with self._lock:
            if self._thread and self._thread.is_alive() and self._ioloop:
                if self._server:
                    self._server.stop()
                    self._logger.info("Tornado server is shut down")

                self._ioloop.add_callback(self._ioloop.stop)
                self._thread.join(timeout=5)
                if self._thread.is_alive():
                    self._logger.error("Tornado server thread did not terminate gracefully")
                else:
                    self._logger.debug("Tornado server thread terminated gracefully")

                self._thread = None
                self._ioloop = None
                self._server = None


    def restart(self, port):
        """
        Restarts the server with new parameters.

        Args:
            port (int): Port to listen on.
        """

        self.stop()
        self.start(port)


    def load_settings(self):
        """
        Read settings to apply outside of the GUI context
        """

        stored_settings = cfg.read_settings_file(self._logger)
        self.port = stored_settings.get("port_number", cfg.DEFAULT_PORT)
        self.address = stored_settings.get("port_address", cfg.DEFAULT_ADDRESS)
