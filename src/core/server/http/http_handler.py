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

# Third-party imports
import jwt
import tornado

# Local application imports
from core.worker import Worker
from core.server.base_handler import BaseHandler, workers, recycle
from core.server.http.get_system_data import get_system_data
from core.server.http.get_network_data import get_network_data
from core.auth import query_user, verify_password, generate_tokens, refresh_access_token
from core.decorators import jwt_required


class HttpHandler(BaseHandler):
    """
    HTTPHandler class for managing connections and serving requests for data. This handler processes
    connection requests via HTTP POST and serves the connection index page and data via HTTP GET. 
    """


    def create_worker(self):
        """
        Creates a worker to pair a HTTP connection to a Websocket session.
        """

        worker = Worker()
        # If no websocket claims the worker within 5 seconds, then remove it
        tornado.ioloop.IOLoop.current().call_later(5, recycle, worker)

        return worker


    async def get(self):
        """
        Get the simple web UI.
        """

        self.render("web.html")


    @jwt_required
    async def post(self):
        """
        Handles POST requests. Attempts to establish a connection and returns the
        worker ID for pairing the websocket connection, websocket connect URL,
        and message.

        Returns:
            dict: A dictionary containing id, url and message.
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
            workers[worker_id] = worker
            # Construct URL for the paired websocket connection
            connect_url = f"ws://{self.request.host}/connect?id={worker_id}"
            message = "Websocket connection ready (Worker expires in 5 seconds if unclaimed)."

        self.write({
            "id": worker_id,
            "url": connect_url,
            "message": message
        })


class HttpSystemHandler(BaseHandler):
    """
    HttpSystemHandler class for handling http requests for data. This handler processes requests
    via HTTP GET and serves system data. 
    """

    @jwt_required
    async def get(self):
        """
        Default GET handler
        """

        self.set_header("Content-Type", "application/json")
        self.write(get_system_data())


class HttpNetworkHandler(BaseHandler):
    """
    HttpNetworkHandler class for handling http requests for data. This handler processes requests
    via HTTP GET and serves system data. 
    """

    @jwt_required
    async def get(self):
        """
        Default GET handler
        """

        self.set_header("Content-Type", "application/json")
        self.write(await get_network_data())


class HttpAuthLoginHandler(BaseHandler):
    """
    Handles login.
    """

    async def post(self):
        """
        Dfault POST handler
        """

        try:
            data = tornado.escape.json_decode(self.request.body)
            username = data.get("username")
            password = data.get("password")

            user = query_user(username)
            authenticated = verify_password(password=password, hashed=user["password"])

            if not user or not authenticated:
                raise tornado.web.HTTPError(401, "Invalid credentials")

            tokens = generate_tokens(user["id"])
            self.write(tokens)
        except Exception as e:
            raise tornado.web.HTTPError(400, f"Bad request, {e}") from e


class HttpAuthRefreshHandler(BaseHandler):
    """
    sadsad
    """

    async def post(self):
        """
        Post
        """
        auth_header = self.request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise tornado.web.HTTPError(400, "Missing or invalid Authorization header")

        refresh_token = auth_header.removeprefix("Bearer ").strip()

        try:
            tokens = refresh_access_token(refresh_token)
            self.write(tokens)
        except jwt.ExpiredSignatureError as e:
            raise tornado.web.HTTPError(401, f"Refresh token expired, {e}") from e
        except jwt.InvalidTokenError as e:
            raise tornado.web.HTTPError(401, f"Invalid refresh token, {e}") from e
        except Exception as e:
            raise tornado.web.HTTPError(400, f"Bad request, {e}") from e
