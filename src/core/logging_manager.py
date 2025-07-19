"""
--------------------------------------------------------------------------
PSMonitor - A simple system monitoring utility
Author: Chris Rowles
Copyright: © 2025 Chris Rowles. All rights reserved.
License: MIT
--------------------------------------------------------------------------
"""

# Standard library imports
import json
import logging
import logging.handlers
import os
import queue
import subprocess
import sys
from threading import Lock

# pylint: disable=too-many-instance-attributes
# the number of attributes is reasonable in this case.
class PSMonitorLogger:
    """
    Concurrent logger.

    Uses Python's `QueueHandler` and `QueueListener` to safely handle logging from
    multiple threads without risk of interleaved output or contention on shared I/O
    handlers.

    Architecture:
        - A single `queue.Queue` receives all log records via `QueueHandler`.
        - A dedicated background thread (`QueueListener`) consumes records from the 
          queue and dispatches them to attached handlers (e.g., file and console).
    """

    def __init__(self, filename: str):
        """
        Initialize the log handler.
        """
        self._enabled = True
        self._lock = Lock()

        self._log_queue = queue.Queue(-1)  # Infinite size
        self._logger = logging.getLogger("PSMonitor")
        self._logger.setLevel(logging.INFO)  # Default level
        self._logger.propagate = False  # Avoid duplicate logs

        self._filepath = os.path.join(os.path.expanduser('~'), '.psmonitor-logs')
        os.makedirs(self._filepath, exist_ok=True)
        self._fullpath = os.path.join(self._filepath, filename)

        self._file_handler = logging.FileHandler(self._fullpath, encoding="utf-8")
        self._file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '[%(asctime)s] - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self._file_handler.setFormatter(formatter)

        # Create console handler
        self._console_handler = logging.StreamHandler()
        self._console_handler.setLevel(logging.INFO)
        self._console_handler.setFormatter(formatter)

        # Create QueueHandler to push logs into queue
        self._queue_handler = logging.handlers.QueueHandler(self._log_queue)

        # Clear existing handlers and add only the QueueHandler
        self._logger.handlers = []
        self._logger.addHandler(self._queue_handler)

        # Setup QueueListener to pull logs from queue and output to handlers
        self._listener = logging.handlers.QueueListener(
            self._log_queue,
            self._file_handler,
            self._console_handler,
            respect_handler_level=True
        )

        self._listener.start()

        self.load_settings()


    def set_level(self, level: str) -> None:
        """
        Set the logging level.
        Accepts: "DEBUG", "INFO", "WARNING", "ERROR"
        """

        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR
        }

        log_level = level_map.get(level.upper())
        if log_level is not None:
            self._logger.setLevel(log_level)
            self._file_handler.setLevel(log_level)
            self._console_handler.setLevel(log_level)
            self._logger.debug("Log level is set to %s", level.upper())


    def is_enabled(self) -> bool:
        """
        Check if logging is enabled.
        """

        return self._enabled


    def set_enabled(self, enabled: bool) -> None:
        """
        Set logging enabled status.
        """

        self._enabled = enabled


    def info(self, message: str) -> None:
        """
        Write an info message to the log if logging is enabled.
        """

        if not self._enabled:
            return

        self._logger.info(message)


    def warning(self, message: str) -> None:
        """
        Write a warning message to the log if logging is enabled.
        """

        if not self._enabled:
            return

        self._logger.warning(message)


    def error(self, message: str) -> None:
        """
        Write an error message to the log if logging is enabled.
        """

        if not self._enabled:
            return

        self._logger.error(message)


    def debug(self, message: str) -> None:
        """
        Write an debug message to the log if logging is enabled.
        """

        if not self._enabled:
            return

        self._logger.debug(message)


    def open_log(self) -> None:
        """
        View the app log
        """

        if not os.path.exists(self._fullpath):
            self._logger.warning("Log file not found at %s", self._fullpath)
            return

        try:
            subprocess.Popen([ # pylint: disable=consider-using-with
                'notepad.exe' if sys.platform == "win32" else "xdg-open",
                self._fullpath
            ])
        except (OSError, ValueError) as e:
            self._logger.error("Failed to open log file: %s", e)


    def clear_log(self) -> None:
        """
        Clear the app log.
        """

        try:
            # Truncate the log file to zero length, effectively clearing it
            with open(self._fullpath, 'w', encoding="utf-8"):
                pass
            self._logger.info("Log file cleared by user")
        except (FileNotFoundError, PermissionError, IsADirectoryError) as e:
            self._logger.error("Failed to open log file: %s", e)


    def load_settings(self):
        """
        Read settings to apply outside of the GUI context
        """

        try:
            settings_file = os.path.join(
                os.path.join(os.path.expanduser('~'), '.psmonitor'),
                "settings.json"
            )

            with open(settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.set_level(data.get("log_level", "INFO"))
            self.set_enabled(data.get("logging_enabled", True))
        except (FileNotFoundError, PermissionError, IsADirectoryError) as e:
            self._logger.error("Failed to load settings from file: %s", e)


    def stop(self) -> None:
        """
        Stop the QueueListener and flush all remaining logs.
        Call this on app shutdown.
        """

        self._listener.stop()
