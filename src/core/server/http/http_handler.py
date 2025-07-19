"""
--------------------------------------------------------------------------
PSMonitor - A simple system monitoring utility
Author: Chris Rowles
Copyright: © 2025 Chris Rowles. All rights reserved.
License: MIT
--------------------------------------------------------------------------
"""

# Third-party imports
from tornado.ioloop import IOLoop

# Local application imports
from core.worker import Worker
from core.server.base_handler import BaseHandler, workers, recycle
from core.server.http.get_system_data import get_system_data
from core.server.http.get_network_data import get_network_data


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
        # If no websocket claims the worker within 3 seconds, then remove it
        IOLoop.current().call_later(3, recycle, worker)

        return worker


    async def get(self):
        """
        Get the simple web UI.
        """

        self.render('web.html')


    async def post(self):
        """
        Handles POST requests. Attempts to establish a connection and returns the
        worker ID and status.

        Returns:
            dict: A dictionary containing `id` (worker ID) and `status` (status message).
        """

        worker_id = None
        status = None

        try:
            # Create a new worker to pair HTTP connection with websocket session
            worker = self.create_worker()
        except Exception as e:
            status = str(e)
        else:
            # Add the worker to the worker registry
            worker_id = worker.id
            workers[worker_id] = worker

        self.write({"id": worker_id, "status": status})


class HttpSystemHandler(BaseHandler):
    """
    HttpSystemHandler class for handling http requests for data. This handler processes requests
    via HTTP GET and serves system data. 
    """

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

    async def get(self):
        """
        Default GET handler
        """

        self.set_header("Content-Type", "application/json")
        self.write(await get_network_data())
