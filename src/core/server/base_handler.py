"""
--------------------------------------------------------------------------
PSMonitor - System and network monitoring utility

File: base_handler.py
Author: Chris Rowles <christopher.rowles@outlook.com>
Copyright: © 2025 Chris Rowles. All rights reserved.
Version: 1.5.0.2413
License: MIT
--------------------------------------------------------------------------
"""

# Third-party imports
from tornado.web import RequestHandler


# Dictionary to store active workers
workers = {}


def recycle(worker):
    """
    Recycles a worker by removing it from the workers dictionary if its handler is not set.

    Args:
        worker: The worker object to recycle.
    
    Returns:
        None
    """

    if worker.handler:
        return

    workers.pop(worker.id, None)
    worker.close()


class BaseHandler(RequestHandler):
    """
    BaseHandler class for handling HTTP requests. CORS headers are set by default.
    """


    def set_default_headers(self):
        """
        Sets default headers for CORS and content type.
        """

        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")


    async def get(self):
        """
        Base HTTP GET request handler.
        """

        self.write("silence is golden.")


    async def post(self):
        """
        Base HTTP POST request handler.
        """

        self.write("silence is golden.")


    def options(self):
        """
        Base HTTP OPTIONS request handler.
        """

        self.set_status(204)
        self.finish()


    def data_received(self, chunk: bytes) -> None:
        """
        For this base handler, we do not process streaming request body.
        """
