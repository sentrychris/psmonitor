from tornado.ioloop import IOLoop

from ...worker import Worker
from ..base import BaseHandler, workers, recycle
from .system import get_system_data
from .network import get_network_data


class HttpHandler(BaseHandler):
    """
    HTTPHandler class for managing connections and serving requests for data. This handler processes
    connection requests via HTTP POST and serves the connection index page and data via HTTP GET. 
    """


    def connect(self):
        """
        Create a connection and obtain a worker
        """

        worker = Worker()
        IOLoop.current().call_later(3, recycle, worker)
        return worker


    def get(self):
        """
        Get the index page
        """

        self.render('index.html')


    def post(self):
        """
        Handles POST requests. Attempts to establish a connection and returns the
        worker ID and status.

        Returns:
            dict: A dictionary containing `id` (worker ID) and `status` (status message).
        """

        id = None
        status = None

        try:
            worker = self.connect()
        except Exception as e:
            status = str(e)
        else:
            id = worker.id
            workers[id] = worker

        self.write(dict(id=id, status=status))


class HttpSystemHandler(BaseHandler):
    """
    HttpSystemHandler class for handling http requests for data. This handler processes requests
    via HTTP GET and serves system data. 
    """

    def get(self):
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
