import uuid
import os.path
# import ssl
from tornado.httpserver import HTTPServer
from tornado.options import define, options
from tornado.ioloop import IOLoop
from app.main import create_app

base_dir = os.path.dirname(__file__)

app = create_app({
    'template_path': os.path.join(base_dir, 'public'),
    'static_path': os.path.join(base_dir, 'public'),
    'cookie_secret': uuid.uuid1().hex,
    'xsrf_cookies': False,
    'debug': True
})

define('port', default=4200, help='Listen port', type=int)

# ssl_dir = str(base_dir + '/ssl')
# ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
# ssl_ctx.load_cert_chain(os.path.join(ssl_dir, "host.crt"),
#                         os.path.join(ssl_dir, "host.key"))

def run():
    http = HTTPServer(app)
    http.listen(options.port)
    print("Listening on http://localhost:" + str(options.port))
    IOLoop.current().start()


if __name__ == '__main__':
    run()
