from tornado.websocket import WebSocketHandler
from asyncio import sleep
from ..system import system_data


class WsHandler(WebSocketHandler):
    def data_received(self, chunk: bytes):
        pass

    def check_origin(self, origin: str):
        return True

    async def open(self):
        while True:
            await self.write_message(system_data())

    def on_message(self, message):
        self.write_message('message received %s' % message)

    def on_close(self):
        print('connection closed')
