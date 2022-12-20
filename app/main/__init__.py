import tornado.web

from .handlers.http import HttpHandler
from .handlers.websocket import WsHandler


def create_app(settings):
    handlers = [
        (r'/', HttpHandler),
        (r'/ws', WsHandler)
    ]

    if settings is None:
        return False

    app = tornado.web.Application(handlers, **settings)

    return app
