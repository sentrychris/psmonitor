"""
--------------------------------------------------------------------------
PSMonitor - A simple system monitoring utility
Author: Chris Rowles
Copyright: © 2025 Chris Rowles. All rights reserved.
License: MIT
--------------------------------------------------------------------------
"""

# Standard library imports
import json
import socket
import threading
from typing import TYPE_CHECKING

# Third-party imports
import requests
import websocket
from tornado.ioloop import IOLoop

# Typing (type hints only, no runtime dependency)
if TYPE_CHECKING:
    from gui.app_manager import PSMonitorApp


class PSMonitorAppClient():
    """
    App client for connection to the tornado server.
    """

    def __init__(self, manager: 'PSMonitorApp' = None) -> None:
        """
        Initializes the app client.
        """

        super().__init__()

        self._manager = manager

        self.port = self._manager.server.port
        self.address = self._manager.server.address

        self.http_url = f"http://{self.address}:{self.port}"
        self.ws_url = f"ws://{self.address}:{self.port}/connect?id="

        self._ws = None
        self._ws_client_thread = None

        self._worker_id = None


    def setup_connection(self) -> None:
        """
        Initialize the connection to the local tornado server.
        """

        try:
            response = requests.get(f'{self.http_url}/system', timeout=5)
            self._manager.data.update(response.json())
            self._manager.update_gui_sections()
            self._start_websocket_connection()
        except requests.RequestException as e:
            self._manager.logger.error(f"Error connecting to local server: {e}")


    def _start_websocket_connection(self) -> None:
        """
        Starts the websocket connection for live data updates.
        """

        try:
            response = requests.post(self.http_url, json={'connection': 'monitor'}, timeout=5)
            worker = response.json()
            self._worker_id = worker['id']
            self._connect_websocket(self._worker_id)
        except requests.RequestException as e:
            self._manager.logger.error(f"Error obtaining worker for websocket connection: {e}")


    def _connect_websocket(self, worker_id: str) -> None:
        """
        Starts the websocket connection with the specified worker ID.

        Args:
            worker_id (str): The worker ID for the websocket connection.
        """

        websocket.enableTrace(False)

        self._ws = websocket.WebSocketApp(
            f"{self.ws_url}{worker_id}",
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )

        # small helper to allow us to log inside the ws client thread
        def run_ws_forever():
            self._manager.logger.debug(
                f"Websocket client thread started: {threading.current_thread().name} "
                f"(ID: {threading.get_ident()})"
            )
            self._ws.run_forever()

        # Run the websocket client in the another thread so it doesn't block the GUI's mainloop().
        self._ws_client_thread = threading.Thread(
            target=run_ws_forever,
            name="PSMonitorWSClientThread",
            daemon=True
        )

        self._ws_client_thread.start()


    def get_worker(self) -> str:
        """
        Return the ID for the worker managing the session.
        """
        return self._worker_id


    def check_server_reachable(self, timeout=1):
        """
        Check the server is reachable.
        """
        try:
            with socket.create_connection((self.address, self.port), timeout=timeout):
                self._manager.logger.info("Tornado server is reachable")
                return True
        except OSError as e:
            self._manager.logger.error(f"Tornado server is not reachable: {e}")
            return False


    def on_message(self, ws: websocket.WebSocketApp, message: str) -> None:
        """
        Handles incoming websocket messages.

        Args:
            ws (websocket.WebSocketApp): The websocket instance.
            message (str): The incoming message.
        """

        try:
            if not ws or not message.startswith("{"):
                return

            self._manager.refresh_data(json.loads(message))
        except json.JSONDecodeError as e:
            self._manager.logger.error(f"Invalid JSON from websocket: {message[:100]}... ({e})")
        except Exception as e:
            self._manager.logger.error(f"Error fetching websocket data: {e}")


    def on_error(self, ws: websocket.WebSocketApp, error) -> None:
        """
        Handles websocket errors.

        Args:
            ws (websocket.WebSocketApp): The websocket instance.
            error (Exception): The error encountered.
        """

        self._manager.logger.error(f"Websocket error: {error} ({ws.url})")


    def on_close(self, _ws: websocket.WebSocketApp, _status_code: int, _msg: str) -> None:
        """
        Handles websocket closure.

        Args:
            _ws (websocket.WebSocketApp): The websocket instance.
            _status_code (int): The status code for the closure.
            _msg (str): The closure message.
        """

        self._manager.logger.info("Websocket connection is closed")


    def on_open(self, ws: websocket.WebSocketApp) -> None:
        """
        Handles websocket opening.

        Args:
            ws (websocket.WebSocketApp): The websocket instance.
        """

        self._manager.logger.info(f"Websocket connection is open ({ws.url})")


    def on_closing(self) -> None:
        """
        Handles application closing.
        """

        if self._ws:
            self._ws.close() # signal the websocket to close

        if self._ws_client_thread:
            self._ws_client_thread.join(timeout=5)
            if self._ws_client_thread.is_alive():
                self._manager.logger.error("Websocket client thread did not terminate gracefully")
            else:
                self._manager.logger.debug("Websocket server thread terminated gracefully")

        self._manager.server.stop()
        self._manager.logger.stop()
        IOLoop.current().add_callback(IOLoop.current().stop)

        self._manager.destroy()
