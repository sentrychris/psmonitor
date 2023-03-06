from tornado.ioloop import IOLoop
from app.main.handlers.base import BaseHandler, workers, recycle
from ..worker import Worker


class HttpHandler(BaseHandler):
    def connect(self):
        worker = Worker()
        IOLoop.current().call_later(3, recycle, worker)
        return worker

    def get(self):
        self.render('index.html')

    def post(self):
        id = None
        error = None

        try:
            worker = self.connect()
        except Exception as e:
            error = str(e)
        else:
            id = worker.id
            workers[id] = worker

        self.write(dict(id=id, error=error))
