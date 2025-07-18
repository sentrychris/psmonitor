"""
Author: Chris Rowles
Copyright: © 2025 Chris Rowles. All rights reserved.
License: MIT
"""

# Standard library imports
import logging
import os
import subprocess
import sys


class PSMonitorAppLogger:
    """
    Basic logging.
    """

    def __init__(self, filename: str):
        """
        Initialize the log handler.
        """
        self._enabled = True
        self._logger = logging.getLogger("PSMonitor")
        self._logger.setLevel(logging.INFO)  # Default level

        self._filepath = os.path.join(os.path.expanduser('~'), '.psmonitor-logs')
        os.makedirs(self._filepath, exist_ok=True)
        self._fullpath = os.path.join(self._filepath, filename)

        self._handler = logging.FileHandler(self._fullpath)
        self._handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '[%(asctime)s] - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self._handler.setFormatter(formatter)

        # Prevent duplicate handlers if __init__ is called multiple times
        if not any(
            isinstance(h, logging.FileHandler) and h.baseFilename == self._handler.baseFilename
            for h in self._logger.handlers
        ):
            self._logger.addHandler(self._handler)


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
            self._handler.setLevel(log_level)
            self._logger.info("Log level is set to %s", level.upper())


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
            self._logger.warning("Log file not found at %s.", self._fullpath)
            return

        try:
            if sys.platform == 'win32':
                # pylint: disable=consider-using-with
                subprocess.Popen(['notepad.exe', self._fullpath])
            elif sys.platform == 'Linux':
                # Use xdg-open to open with the default text editor
                subprocess.Popen(['xdg-open', self._fullpath])
                # pylint: enable=consider-using-with
        # pylint: disable=broad-except
        except Exception as e:
            self._logger.error("Failed to open log file: %s", e)
        # pylint: enable=broad-except


    def clear_log(self) -> None:
        """
        Clear the app log.
        """
        try:
            # Truncate the log file to zero length, effectively clearing it
            with open(self._fullpath, 'w', encoding="utf-8"):
                pass
            self._logger.info("Log file cleared by user.")
        except (FileNotFoundError, PermissionError, IsADirectoryError) as e:
            self._logger.error("Failed to open log file: %s", e)
