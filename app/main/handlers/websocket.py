import weakref
from tornado.websocket import WebSocketHandler
from tornado.ioloop import IOLoop
from tornado.iostream import StreamClosedError
from tornado.web import Application
from tornado.httputil import HTTPServerRequest
from asyncio import sleep
from ..system import *
from .base import workers


class WsHandler(WebSocketHandler):
    def __init__(self, application: Application, request: HTTPServerRequest, **kwargs):
        self.loop = IOLoop.current()
        self.worker_ref = None
        super().__init__(application, request, **kwargs)

    def data_received(self, chunk: bytes):
        pass

    def check_origin(self, origin: str):
        return True

    def open(self):
        worker = workers.pop(self.get_argument('id'), None)

        if not worker:
            self.close(reason='Invalid worker id')
            return

        self.set_nodelay(True)

        worker.set_handler(self)
        self.worker_ref = weakref.ref(worker)

        self.write_message('ready to transmit data')
        IOLoop.current().add_callback(
            lambda: self.tail()
        )

    async def tail(self):
        try:
            while True:
                await sleep(3)
                await self.write_message(system_data())
        except StreamClosedError:
            pass
        finally:
            self.close()

    def on_message(self, message):
        self.write_message('message received %s' % message)

    def on_close(self):
        self.write_message('close connection request received')
        worker = self.worker_ref() if self.worker_ref else None

        if worker:
            worker.close()
