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
        self.logger = logging.getLogger(__name__)
        self.filepath = os.path.join(os.path.expanduser('~'), '.psmonitor-logs')

        if not os.path.isdir(self.filepath):
            os.mkdir(self.filepath)
        
        self.fullpath = os.path.join(self.filepath, filename)

        logging.basicConfig(filename=self.fullpath, level=logging.INFO)


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

        self.logger.info(message)


    def error(self, message: str) -> None:
        """
        Write an error message to the log if logging is enabled.
        """
        if not self._enabled:
            return

        self.logger.error(message)


    def open_log(self) -> None:
        """
        View the app log
        """

        if not os.path.exists(self.fullpath):
            self.logger.warning(f"Log file not found at {self.fullpath}.")
            return

        try:
            if sys.platform == 'win32':
                subprocess.Popen(['notepad.exe', self.fullpath])
            elif sys.platform == 'Linux':
                # Use xdg-open to open with the default text editor
                subprocess.Popen(['xdg-open', self.fullpath])
        except Exception as e:
            self.logger.error(f"Failed to open log file: {e}")


    def clear_log(self) -> None:
        """
        Clear the app log.
        """
        try:
            # Truncate the log file to zero length, effectively clearing it
            with open(self.fullpath, 'w'):
                pass
            self.logger.info("Log file cleared by user.")
        except Exception as e:
            self.logger.error(f"Failed to clear log file: {e}")