"""
--------------------------------------------------------------------------
PSMonitor - A simple system monitoring utility
Author: <Author Name>
Copyright: © 2025 Chris Rowles. All rights reserved.
License: MIT
--------------------------------------------------------------------------
"""

import tkinter as tk
# from tkinter import ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gui.app_manager import PSMonitorApp

class PSMonitorChildHandlerTemplate:
    """
    Handler template.
    """

    def __init__(self, manager: 'PSMonitorApp' = None) -> None:
        """
        Initializes the handler.
        """

        self._window = None
        self._window_title = "Window Title"
        self._manager = manager


    def open_window(self) -> None:
        """
        Open window.
        """

        if hasattr(self, '_window') and self._window and self._window.winfo_exists():
            if not self._window.winfo_viewable():
                self._window.deiconify()
            self._window.lift()
            return

        self._window = tk.Toplevel(self._manager)
        self._window.title(self._window_title)
        self._window.geometry("450x500")
        self._window.resizable(False, False)
        self._window.protocol("WM_DELETE_WINDOW", self.on_close)


    def is_active(self):
        """
        Check if the window is active.
        """

        return hasattr(self, '_window') and self._window and self._window.winfo_exists()


    def close_window(self) -> None:
        """
        Close window.
        """

        if hasattr(self, '_window') and self._window and self._window.winfo_exists():
            self.on_close()


    def on_close(self):
        """
        On close handler
        """

        self._window.destroy()
        del self._window
