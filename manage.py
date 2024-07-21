import uuid
import os.path

from tornado.httpserver import HTTPServer
from tornado.options import define, options, parse_command_line
from tornado.ioloop import IOLoop
from app import create_app


# Define base directory
base_dir = os.path.dirname(__file__)


# Create application with specified settings
app = create_app({
    'template_path': os.path.join(base_dir, 'public'),
    'static_path': os.path.join(base_dir, 'public'),
    'cookie_secret': uuid.uuid1().hex,
    'xsrf_cookies': False,
    'debug': True
})


# Define command-line options
define('port', default=4200, help='Listen port', type=int)


def run():
    """
    Starts the tornado application server and listens on the specified address and port.
    """

    # Parse command line arguments
    parse_command_line()

    http = HTTPServer(app)
    http.listen(options.port)

    print("Listening on http://localhost:" + str(options.port))
    IOLoop.current().start()


if __name__ == '__main__':
    run()
