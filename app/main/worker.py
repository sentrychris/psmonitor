from tornado.ioloop import IOLoop


class Worker(object):
    """
    Workers for the worker pool...
    """

    def __init__(self):
        self.loop = IOLoop.current()
        self.id = str(id(self))
        self.handler = None
        self.mode = IOLoop.READ


    def set_handler(self, handler):
        if not self.handler:
            self.handler = handler


    def close(self):
        if self.handler:
            self.handler.close()
