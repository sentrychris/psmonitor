"""
--------------------------------------------------------------------------
PSMonitor - System and network monitoring utility

File: http_handler.py
Author: Chris Rowles <christopher.rowles@outlook.com>
Copyright: © 2025 Chris Rowles. All rights reserved.
Version: 1.6.0.1001
License: MIT
--------------------------------------------------------------------------
"""

# Standard library imports
from typing import TYPE_CHECKING

# Third-party imports
import tornado

# Local application imports
from core.config import get_launch_mode
from core.worker import Worker
from core.server.base_handler import BaseHandler, workers, recycle
from core.server.http.get_system_data import get_system_data
from core.server.http.get_network_data import get_network_data
from core.auth import verify_password, generate_token, delete_credentials_file
from core.decorators import jwt_required

# Type checking
if TYPE_CHECKING:
    from core.database_manager import PSMonitorDatabaseManager


class HttpWebUIHandler(BaseHandler):
    """
    HttpWebUIHandler class for displaying the web UI.
    """

    async def get(self):
        """
        Get the simple web UI.
        """

        self.render("web.html")


class HttpWorkerHandler(BaseHandler):
    """
    HTTPWorkerHandler class for managing connections and serving requests for data. This
    handler processes connection requests via HTTP POST.
    """

    def create_worker(self) -> Worker:
        """
        Creates a worker to pair a HTTP connection to a Websocket session.

        Returns:
            Worker: A worker instance for managing the paired connection.
        """

        subscriber = self.current_user.get("sub")
        if not subscriber:
            raise RuntimeError("Invalid subscriber for this worker instance.")

        worker = Worker(subscriber=self.current_user.get("sub"))
        # Schedule BaseHandler recycle to run after 5 seconds, if worker's
        # handler is not set then it is unclaimed and it will be removed.
        tornado.ioloop.IOLoop.current().call_later(5, recycle, worker)

        return worker


    @jwt_required
    async def post(self):
        """
        Handles POST requests. Attempts to establish a connection and returns the
        worker ID for pairing the websocket connection, websocket connect URL,
        and message.
        """

        worker_id = None
        connect_url = None
        message = None

        try:
            # Create a new worker to pair HTTP connection with websocket session
            worker = self.create_worker()
        except Exception:
            message = "There was an error creating the websocket worker."
        else:
            # Add the worker to the worker registry
            worker_id = worker.id
            subscriber = worker.subscriber
            workers[worker_id] = worker
            # Construct URL for the paired websocket connection
            connect_url = f"ws://{self.request.host}/connect?id={worker_id}&subscriber={subscriber}"
            message = "Websocket connection ready (Worker expires in 5 seconds if unclaimed)."

        self.write({
            "id": worker_id,
            "url": connect_url,
            "message": message
        })


class HttpSystemHandler(BaseHandler):
    """
    HttpSystemHandler class for handling http requests for data. This handler processes 
    requests via HTTP GET and serves system data. 
    """

    @jwt_required
    async def get(self):
        """
        Get system data.
        """

        self.set_header("Content-Type", "application/json")
        self.write(get_system_data())


class HttpNetworkHandler(BaseHandler):
    """
    HttpNetworkHandler class for handling http requests for data. This handler processes
    requests via HTTP GET and serves network data. 
    """

    @jwt_required
    async def get(self):
        """
        Get network data.
        """

        self.set_header("Content-Type", "application/json")
        self.write(await get_network_data())


class HttpAuthHandler(BaseHandler):
    """
    HttpAuthHandler class for handling http requests for authentication. This handler
    processes requests via HTTP POST and issues access tokens.
    """

    async def post(self):
        """
        Login.
        """

        try:
            db: "PSMonitorDatabaseManager" = self.application.settings.get("db")
            data = tornado.escape.json_decode(self.request.body)
            username = data.get("username")
            password = data.get("password")

            user = db.get_user(username)
            is_authenticated = verify_password(password=password, hashed=user["password"])

            if not user or not is_authenticated:
                raise tornado.web.HTTPError(401, "Invalid credentials")
            auth_token = generate_token(user["id"])

            if get_launch_mode() == "headless":
                delete_credentials_file()

            self.write(auth_token)
        except Exception as e:
            raise tornado.web.HTTPError(400, f"Bad request, {e}") from e
