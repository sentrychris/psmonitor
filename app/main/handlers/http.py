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
        worker_id = None
        status = None

        try:
            worker = self.connect()
        except Exception as e:
            status = str(e)
        else:
            worker_id = worker.id
            workers[worker_id] = worker

        self.write(dict(id=worker_id, status=status))
