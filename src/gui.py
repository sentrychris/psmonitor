"""
PSMonitor - A simple system monitoring utility
Author: Chris Rowles
Copyright: © 2025 Chris Rowles. All rights reserved.
License: MIT
"""

# Standard library imports
import os
import signal
import sys
import threading
import uuid

# Third-party imports
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

# Local application imports
from core import create_app, signal_handler
from gui.app_manager import PSMonitorApp
from gui.log_handler import PSMonitorAppLogger


# Constants
BASE_DIR = os.path.dirname(__file__)
TEMPLATE_PATH = os.path.join(BASE_DIR, 'gui', 'web')
STATIC_PATH = os.path.join(BASE_DIR, 'gui', 'web')
COOKIE_SECRET = uuid.uuid1().hex

# Logger
logger = PSMonitorAppLogger("app.log")


def start_server(port: int = 4500) -> None:
    """
    Starts the server and listens on port 4500.
    """

    http = HTTPServer(create_app({
        'template_path': TEMPLATE_PATH,
        'static_path': STATIC_PATH,
        'cookie_secret': COOKIE_SECRET,
        'xsrf_cookies': False,
        'debug': True
    }))
    http.listen(port, address='localhost')

    logger.debug(
        f"Tornado server thread started: {threading.current_thread().name} "
        f"(ID: {threading.get_ident()})"
    )
    logger.info("server is listening on http://localhost:4500")

    IOLoop.current().start()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if sys.platform == "darwin":
        print("MacOS is not supported.")
        exit(0)

    # Start the Tornado server in another thread so it doesn't block the GUI's mainloop().
    tornado_thread = threading.Thread(
        target=start_server,
        name="PSMonitorTornadoSrvThread",
        daemon=True
    )
    tornado_thread.start()

    init_data = {
        "cpu": {"usage": 0.0, "temp": 0, "freq": 0},
        "mem": {"total": 0, "used": 0, "free": 0, "percent": 0},
        "disk": {"total": 0, "used": 0, "free": 0, "percent": 0},
        "user": "",
        "platform": {"distro": "", "kernel": "", "uptime": ""},
        "uptime": "",
        "processes": []
    }

    app = PSMonitorApp(init_data, logger)
    app.mainloop()
