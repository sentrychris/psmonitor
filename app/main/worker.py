import tornado.websocket

from tornado.ioloop import IOLoop
from tornado.iostream import _ERRNO_CONNRESET
from tornado.util import errno_from_exception


class Worker(object):
    """Create workers assigned to websocket connections"""
    def __init__(self):
        self.loop = IOLoop.current()
        self.id = str(id(self))
        self.handler = None
        self.mode = IOLoop.READ

    def __call__(self, fd, events):
        if events & IOLoop.READ:
            self.on_read()
        if events & IOLoop.WRITE:
            self.on_write()
        if events & IOLoop.ERROR:
            self.close()

    def set_handler(self, handler):
        if not self.handler:
            self.handler = handler

    def update_handler(self, mode):
        if self.mode != mode:
            self.loop.update_handler(self.id, mode)
            self.mode = mode

    def on_read(self):
        try:
            data = 50
        except (OSError, IOError) as e:
            if errno_from_exception(e) in _ERRNO_CONNRESET:
                self.close()
        else:
            if not data:
                self.close()
                return

            try:
                self.handler.write_message(data)
            except tornado.websocket.WebSocketClosedError:
                self.close()

    def close(self):
        if self.handler:
            self.handler.close()
