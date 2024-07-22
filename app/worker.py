from tornado.ioloop import IOLoop

from .handler.websocket.websocket import WebsocketHandler


class Worker(object):
    """
    Worker class for managing worker instances within a worker pool.

    This class represents a worker that can be associated with a WebSocket handler and
    manages its I/O loop operations.

    Attributes:
        loop (IOLoop): The current IOLoop instance.
        id (str): A unique identifier for the worker instance.
        handler (WebSocketHandler): The WebSocket handler associated with this worker.
        mode (int): The I/O loop mode, default is IOLoop.READ.
    """


    def __init__(self):
        """
        Initializes the Worker instance.

        Sets the current IOLoop, generates a unique ID for the worker, and initializes
        the handler and mode attributes.
        """

        self.loop = IOLoop.current()
        self.id = str(id(self))
        self.handler = None
        self.mode = IOLoop.READ


    def set_handler(self, handler: WebsocketHandler):
        """
        Sets the WebSocket handler for the worker.

        Associates the given handler with this worker if no handler is currently set.

        Args:
            handler (WebSocketHandler): The WebSocket handler to be associated with this worker.
        """

        if not self.handler:
            self.handler = handler


    def close(self):
        """
        Closes the associated WebSocket handler.

        If a handler is set, this method closes the handler to clean up the connection.
        """

        if self.handler:
            self.handler.close()
