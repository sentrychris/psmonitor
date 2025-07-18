import logging
import os
import subprocess
import sys


class PSMonitorAppLogger:
    """
    Basic logging.
    """

    def __init__(self, filename: str):
        self._enabled = True
        self._logger = logging.getLogger(__name__)
        self._filepath = os.path.join(os.path.expanduser('~'), '.psmonitor-logs')

        if not os.path.isdir(self._filepath):
            os.mkdir(self._filepath)
        
        self._fullpath = os.path.join(self._filepath, filename)

        logging.basicConfig(filename=self._fullpath, level=logging.INFO)


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
            self._logger.warning(f"Log file not found at {self._fullpath}.")
            return

        try:
            if sys.platform == 'win32':
                subprocess.Popen(['notepad.exe', self._fullpath])
            elif sys.platform == 'Linux':
                # Use xdg-open to open with the default text editor
                subprocess.Popen(['xdg-open', self._fullpath])
        except Exception as e:
            self._logger.error(f"Failed to open log file: {e}")


    def clear_log(self) -> None:
        """
        Clear the app log.
        """
        try:
            # Truncate the log file to zero length, effectively clearing it
            with open(self._fullpath, 'w'):
                pass
            self._logger.info("Log file cleared by user.")
        except Exception as e:
            self._logger.error(f"Failed to clear log file: {e}")