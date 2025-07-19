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


# Constants
WS_URL = 'ws://localhost:4500/connect?id='
HTTP_URL = 'http://localhost:4500'


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

        self._ws = None
        self._ws_client_thread = None
        self._worker_id = None


    def setup_connection(self) -> None:
        """
        Initialize the connection to the local tornado server.
        """

        try:
            response = requests.get(f'{HTTP_URL}/system', timeout=5)
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
            response = requests.post(HTTP_URL, json={'connection': 'monitor'}, timeout=5)
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
            f"{WS_URL}{worker_id}",
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


    def check_server_reachable(self, host="127.0.0.1", port=4500, timeout=1):
        """
        Check the server is reachable.
        """
        try:
            with socket.create_connection((host, port), timeout=timeout):
                self._manager.logger.info("Tornado server is reachable.")
                return True
        except OSError as e:
            self._manager.logger.error(f"Server not reachable: {e}")
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
        except Exception as e: # pylint: disable=broad-except
            self._manager.logger.error(f"Error fetching websocket data: {e}")


    def on_error(self, ws: websocket.WebSocketApp, error) -> None:
        """
        Handles websocket errors.

        Args:
            ws (websocket.WebSocketApp): The websocket instance.
            error (Exception): The error encountered.
        """

        self._manager.logger.error(f"Websocket error: {error} (ws url: {ws.url})")


    def on_close(self, _ws: websocket.WebSocketApp, _status_code: int, _msg: str) -> None:
        """
        Handles websocket closure.

        Args:
            _ws (websocket.WebSocketApp): The websocket instance.
            _status_code (int): The status code for the closure.
            _msg (str): The closure message.
        """

        self._manager.logger.info("websocket connection is now closed.")


    def on_open(self, ws: websocket.WebSocketApp) -> None:
        """
        Handles websocket opening.

        Args:
            ws (websocket.WebSocketApp): The websocket instance.
        """

        self._manager.logger.info(f"websocket connection is now open (ws url: {ws.url})")


    def on_closing(self) -> None:
        """
        Handles application closing.
        """

        if self._ws:
            self._ws.close()
        if self._ws_client_thread:
            self._ws_client_thread.join()

        self._manager.server.stop()
        self._manager.logger.stop()
        IOLoop.current().add_callback(IOLoop.current().stop)

        self._manager.destroy()
