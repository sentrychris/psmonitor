import uuid
import os.path
import signal

from tornado.httpserver import HTTPServer
from tornado.options import define, options, parse_command_line
from tornado.ioloop import IOLoop

from app import create_app, signal_handler


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
define('address', default='localhost', help='Listen address for the application')
define('port', default=4500, help='Listen port for the application', type=int)


def run():
    """
    Starts the tornado application server and listens on the specified address and port.
    """

    # Parse command line arguments
    parse_command_line()

    # Create the server and listen on the specified port and address
    http = HTTPServer(app)
    http.listen(port=options.port, address=options.address)
    print("Listening on http://{}:{}".format(options.address, options.port))
    IOLoop.current().start()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    run()
