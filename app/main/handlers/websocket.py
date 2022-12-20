from tornado.websocket import WebSocketHandler


class WsHandler(WebSocketHandler):
    def data_received(self, chunk: bytes):
        pass

    def check_origin(self, origin: str):
        return True

    def open(self):
        self.write_message("Connected!")

    def on_message(self, message):
        self.write_message('message received %s' % message)

    def on_close(self):
        print('connection closed')
