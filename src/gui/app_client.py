"""
--------------------------------------------------------------------------
PSMonitor - System and network monitoring utility

File: app_client.py
Author: Chris Rowles <christopher.rowles@outlook.com>
Copyright: © 2025 Chris Rowles. All rights reserved.
Version: 1.6.0.1001
License: MIT
--------------------------------------------------------------------------
"""

# Standard library imports
import json
import socket
import sys
import time
import threading
from typing import TYPE_CHECKING

# Third-party imports
import requests
import websocket

# Local application imports
from core.auth import get_credentials

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

        self._auth_token = None

        self._worker_id = None


    def safe_connect(self, max_attempts: int = None, base_delay: float = None) -> None:
        """
        Initialize the connection if the server is reachable.
        """

        if max_attempts is None:
            max_attempts = self._manager.settings_handler.max_reconnect_attempts.get()
        if base_delay is None:
            base_delay = self._manager.settings_handler.reconnect_base_delay.get()

        attempt = 0
        while attempt < max_attempts:
            if self.check_server_reachable():

                try:
                    self._authenticate()
                except Exception:
                    self._manager.logger.error("Failed to authenticate, shutting down")
                    self._manager.shutdown()
                    sys.exit(1)

                self._setup_connection()
                return

            delay = base_delay * (2 ** attempt)
            self._manager.logger.warning(
                f"Server unreachable. Retrying in {delay:.1f} seconds... (attempt {attempt + 1})"
            )
            time.sleep(delay)
            attempt += 1

        self._manager.logger.error(
            f"Failed to connect after {max_attempts} attempts. Shutting down."
        )
        self._manager.shutdown()
        sys.exit(1)


    def set_address_and_port(self, address: str, port: str) -> None:
        """
        Configure connection address and port.
        """

        self.address = address
        self.port = port

        self.http_url = f"http://{self.address}:{self.port}"
        self.ws_url = f"ws://{self.address}:{self.port}/connect?id="


    def _authenticate(self) -> None:
        """
        Authenticate against the embedded server.
        """

        username, password = get_credentials()

        response = requests.post(
            f'{self.http_url}/authenticate',
            json={"username": username, "password": password},
            timeout=5
        )

        data = response.json()
        self._auth_token = data.get("token")
        self._manager.logger.info("User has successfully authenticated")


    def _setup_connection(self) -> None:
        """
        Initialize the connection.
        """

        try:
            response = requests.get(
                url=f'{self.http_url}/system',
                headers={'Authorization': f'Bearer {self._auth_token}'},
                timeout=5
            )
            self._manager.data.update(response.json())
            self._manager.update_gui_sections()
            self._start_websocket_connection()
        except requests.RequestException as e:
            self._manager.logger.error(f"Error connecting to server: {e}")


    def _start_websocket_connection(self) -> None:
        """
        Starts the websocket connection for live data updates.
        """

        try:
            response = requests.post(
                url=f"{self.http_url}/worker",
                headers={'Authorization': f'Bearer {self._auth_token}'},
                timeout=5
            )
            worker = response.json()
            self._worker_id = worker['id']
            self._manager.logger.debug(f"Worker obtained: {self._worker_id}")
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


    def close_websocket_connection(self):
        """
        Close the websocket connection.
        """

        if self._ws:
            self._ws.close() # signal the websocket to close

        if self._ws_client_thread:
            self._ws_client_thread.join(timeout=5)
            if self._ws_client_thread.is_alive():
                self._manager.logger.error("Websocket client thread did not terminate gracefully")
            else:
                self._manager.logger.debug("Websocket server thread terminated gracefully")


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
