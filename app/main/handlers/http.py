from app.main.handlers.base import BaseHandler


class HttpHandler(BaseHandler):
    def get(self):
        self.render('index.html')
