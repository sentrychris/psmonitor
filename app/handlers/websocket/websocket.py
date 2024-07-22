import weakref

from tornado.ioloop import IOLoop
from tornado.iostream import StreamClosedError
from tornado.httputil import HTTPServerRequest
from tornado.web import Application
from tornado.websocket import WebSocketHandler, WebSocketClosedError

from ..base import workers
from .system import get_system_data
from .network import get_network_data


active_connections = set()
max_connections = 20


class WebsocketHandler(WebSocketHandler):
    """
    WebSocketHandler that handles WebSocket connections and communicates with
    system and network data sources.

    Attributes:
        loop (IOLoop): The current IOLoop instance.
        worker_ref (weakref.ref): A weak reference to the worker associated
            with this WebSocket connection.
    
    Methods:
        data_received(chunk: bytes): Receives data chunks (no operation in this handler).
        check_origin(origin: str): Checks the origin of the request (always allows connections).
        open(): Handles the opening of a WebSocket connection.
        monitor_system(): Coroutine that continuously sends system data to the client.
        monitor_network(): Coroutine that continuously sends network data to the client.
        on_message(message: str): Handles incoming messages from the WebSocket client.
        on_close(): Cleans up and closes the associated worker when the connection closes.
    """


    def __init__(self, application: Application, request: HTTPServerRequest, **kwargs):
        """
        Initializes the WebSocketHandler.

        Args:
            application (Application): The Tornado Application instance.
            request (HTTPServerRequest): The HTTPServerRequest object for this WebSocket connection.
            **kwargs: Additional keyword arguments to pass to the base class initializer.
        """

        self.loop = IOLoop.current()
        self.worker_ref = None
        super().__init__(application, request, **kwargs)


    def check_origin(self, origin: str):
        """
        Checks whether the WebSocket connection origin is allowed.

        Args:
            origin (str): The origin of the WebSocket request.

        Returns:
            bool: Always returns True, allowing connections from any origin.
        """

        return True


    def open(self):
        """
        Handles the opening of a WebSocket connection. Retrieves the worker based on the 'id'
        argument, sets the worker for this handler, and starts the monitoring coroutine.
        """

        if len(active_connections) >= max_connections:
            self.write_message('Server is at full capacity. Please try again later.')
            self.close()
            return
        
        active_connections.add(self)

        worker = workers.pop(self.get_argument('id'), None)

        if not worker:
            self.close(reason='Invalid worker id')
            return

        self.set_nodelay(True)

        worker.set_handler(self)
        self.worker_ref = weakref.ref(worker)

        self.write_message('connected to monitor, transmitting data...')
        self.loop.add_callback(self.monitor_system)
        # self.loop.add_callback(self.monitor_network)


    async def monitor_system(self):
        """
        Coroutine that continuously retrieves system data using a thread pool executor
        and sends it to the WebSocket client. Closes the connection if an error occurs
        or when the WebSocket is closed.
        """

        try:
            while True:
                data = await get_system_data()
                if data:
                    await self.write_message(data)
        except (StreamClosedError, WebSocketClosedError):
            pass
        finally:
            self.close()


    async def monitor_network(self):
        """
        Coroutine that continuously retrieves network data using asynchronous methods
        and sends it to the WebSocket client. Closes the connection if an error occurs
        or when the WebSocket is closed.
        """

        try:
            while True:
                data = await get_network_data()
                if data:
                    await self.write_message(data)
        except (StreamClosedError, WebSocketClosedError):
            pass
        finally:
            self.close()


    def on_message(self, message: str):
        """
        Handles incoming messages from the WebSocket client.

        Args:
            message (str): The message received from the client.

        Sends a confirmation message back to the client.
        """

        self.write_message('message received %s' % message)


    def on_close(self):
        """
        Handles the closing of the WebSocket connection. Cleans up and closes
        the associated worker if it exists.
        """

        active_connections.discard(self)

        worker = self.worker_ref() if self.worker_ref else None

        if worker:
            worker.close()
