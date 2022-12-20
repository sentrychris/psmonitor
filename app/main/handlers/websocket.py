import datetime
from tornado.websocket import WebSocketHandler
from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.httputil import HTTPServerRequest
from asyncio import sleep
from ..system import *


class WsHandler(WebSocketHandler):
    clients = set()

    def __init__(self, application: Application, request: HTTPServerRequest, **kwargs):
        self.timeout = IOLoop.current().add_timeout(datetime.timedelta(minutes=60), self.explicit_close)
        super().__init__(application, request, **kwargs)

    def data_received(self, chunk: bytes):
        pass

    def check_origin(self, origin: str):
        return True

    async def open(self, *args):
        self.set_nodelay(True)
        self.clients.add(self)
        await self.write_message('connection success! Transmitting data...')
        await sleep(3)
        while True:
            await self.write_message(system_data())
            # await sleep(1)

    def on_message(self, message):
        self.write_message('message received %s' % message)

    def on_close(self):
        self.close()
        print('connection closed')
        self.clients.discard(self)

    def explicit_close(self):
        self.close()  # you wont even have to iterate over the clients.
