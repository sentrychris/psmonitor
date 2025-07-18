"""
--------------------------------------------------------------------------
PSMonitor - A simple system monitoring utility
Author: Chris Rowles
Copyright: © 2025 Chris Rowles. All rights reserved.
License: MIT
--------------------------------------------------------------------------
"""

# Standard library imports
import os
import queue
import signal
import sys
import threading

# Third-party imports
from tornado.ioloop import IOLoop

# Local application imports
from core import create_server, signal_handler
from gui.app_manager import PSMonitorApp
from gui.log_handler import PSMonitorAppLogger


# Logger
logger = PSMonitorAppLogger("app.log")


def start_server(port: int, server_queue: queue.Queue, thread_event: threading.Event) -> None:
    """
    Starts the server and listens on port 4500.
    """

    http = create_server(os.path.join(os.path.dirname(__file__), 'gui', 'web'))
    http.listen(port, address='localhost')

    server_queue.put(http)  # to access from main thread

    def on_start():
        logger.debug(
            f"Tornado server thread started: {threading.current_thread().name} "
            f"(ID: {threading.get_ident()})"
        )
        thread_event.set()

    logger.info("server is listening on http://localhost:4500")

    IOLoop.current().add_callback(on_start)
    IOLoop.current().start()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if sys.platform == "darwin":
        print("MacOS is not supported.")
        sys.exit(0)

    tornado_queue = queue.Queue()
    tornado_started = threading.Event()

    # Start the Tornado server in another thread so its operations
    # don't block the GUI's mainloop().
    tornado_thread = threading.Thread(
        target=start_server,
        args=(4500, tornado_queue, tornado_started),
        name="PSMonitorTornadoSrvThread",
        daemon=True
    )
    tornado_thread.start()

    # Wait until the server is available for thread-safe transfer.
    tornado_server = tornado_queue.get()
    tornado_started.wait()

    init_data = {
        "cpu": {"usage": 0.0, "temp": 0, "freq": 0},
        "mem": {"total": 0, "used": 0, "free": 0, "percent": 0},
        "disk": {"total": 0, "used": 0, "free": 0, "percent": 0},
        "user": "",
        "platform": {"distro": "", "kernel": "", "uptime": ""},
        "uptime": "",
        "processes": []
    }

    app = PSMonitorApp(init_data, tornado_server, logger)
    app.mainloop()
