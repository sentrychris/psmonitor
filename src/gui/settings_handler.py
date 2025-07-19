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
import os
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

# Local application imports
from core.config import DEFAULT_LOG_ENABLED, DEFAULT_LOG_LEVEL, \
    DEFAULT_PORT, DEFAULT_SETTINGS_FILE

# Typing (type hints only, no runtime dependency)
if TYPE_CHECKING:
    from gui.app_manager import PSMonitorApp


class PSMonitorAppSettingsHandler:
    """
    Settings handler.
    """

    LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR']

    def __init__(self, manager: 'PSMonitorApp' = None) -> None:
        """
        Initializes the handler.
        """

        self._window = None
        self._window_title = "View/Edit Settings"

        self._log_buttons_frame = None
        self._log_status_label = None
        self._settings_status_label = None
        self._tooltip = None

        self._manager = manager
        self._settings_path = DEFAULT_SETTINGS_FILE

        # Default settings
        self.logging_enabled = tk.BooleanVar(value=DEFAULT_LOG_ENABLED)
        self.log_level = tk.StringVar(value=DEFAULT_LOG_LEVEL)
        self.port_number = tk.IntVar(value=DEFAULT_PORT)
        self.max_ws_connections = tk.IntVar(value=10)

        # Load saved settings
        self._load_settings_from_file()


    def open_window(self) -> None:
        """
        Open graph window.
        """

        if hasattr(self, '_window') and self._window and self._window.winfo_exists():
            if not self._window.winfo_viewable():
                self._window.deiconify()
            self._window.lift()
            return

        self._window = tk.Toplevel(self._manager)
        self._window.title(self._window_title)
        self._window.geometry("450x560")
        self._window.resizable(False, True)
        self._window.protocol("WM_DELETE_WINDOW", self.on_close)

        main_frame = ttk.Frame(self._window, padding=10)
        main_frame.pack(fill="both", expand=True)

        self._build_logging_section(main_frame)
        self._build_server_section(main_frame)
        self._build_buttons_section(main_frame)


    def get_current_settings(self):
        """
        Get the current settings
        """
        return {
            "logging_enabled": self.logging_enabled.get(),
            "log_level": self.log_level.get(),
            "port_number": self.port_number.get(),
            "max_ws_connections": self.max_ws_connections.get()
        }


    def set_logging_settings(self) -> None:
        """
        Set the logging settings.
        """
        if self._manager:
            self._manager.logger.set_enabled(self.logging_enabled.get())
            self._manager.logger.set_level(self.log_level.get())


    def _build_logging_section(self, parent):
        logging_frame = ttk.LabelFrame(parent, text="Logging", padding=10)
        logging_frame.pack(fill="x", pady=10)

        # Logging enabled checkbox
        ttk.Checkbutton(
            logging_frame,
            text="Enable Logging",
            variable=self.logging_enabled
        ).pack(anchor="w")

        ttk.Label(
            logging_frame,
            text="When enabled, logs will be stored for diagnostic purposes."
        ).pack(anchor="w", pady=(2, 10))

        # Log level dropdown
        ttk.Label(logging_frame, text="Minimum Log Level:").pack(anchor="w")
        ttk.Combobox(
            logging_frame,
            textvariable=self.log_level,
            values=self.LOG_LEVELS,
            state='readonly'
        ).pack(anchor="w", fill="x", pady=5)

        # Buttons
        self._log_buttons_frame = ttk.Frame(logging_frame)
        self._log_buttons_frame.pack(fill="x", pady=5)

        ttk.Button(
            self._log_buttons_frame,
            text="Clear Log",
            command=self._on_clear_log
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            self._log_buttons_frame,
            text="Open Log",
            command=self._manager.logger.open_log
        ).pack(side="left")

        self._log_status_label = ttk.Label(self._log_buttons_frame, text="", foreground="green")
        self._log_status_label.pack(side="left", padx=(10, 0))


    def _build_server_section(self, parent):
        server_frame = ttk.LabelFrame(parent, text="Server", padding=10)
        server_frame.pack(fill="x", pady=10)

        style = ttk.Style()
        style.configure("Help.TLabel", foreground="#333333", font=("Arial", 8))

        # Description label
        ttk.Label(
            server_frame,
            text="Configure the embedded server for remote monitoring."
        ).pack(anchor="w", pady=(0, 10))

        # Port
        ttk.Label(server_frame, text="Port Number:").pack(anchor="w")
        ttk.Entry(
            server_frame,
            textvariable=self.port_number,
        ).pack(anchor="w", fill="x", pady=(0, 5))

        ttk.Label(
            server_frame,
            text="Sets the port for the embedded server to listen on for incoming connections.",
            wraplength=400,
            style="Help.TLabel"
        ).pack(anchor="w", pady=(1, 15))

        # Max connections
        ttk.Label(server_frame, text="Max Connections:").pack(anchor="w")
        ttk.Entry(
            server_frame,
            textvariable=self.max_ws_connections,
        ).pack(anchor="w", fill="x", pady=(0, 5))

        ttk.Label(
            server_frame,
            text="Sets the max number of allowed websocket connections to the embedded server.",
            wraplength=400,
            style="Help.TLabel"
        ).pack(anchor="w", pady=(1, 15))

        ttk.Button(
            server_frame,
            text="Save & Restart Server",
            command=lambda: 1,
            state="disabled"
        ).pack(anchor="e", pady=(10, 0))


    def _build_buttons_section(self, parent):
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(side="bottom", fill="x", pady=10)

        ttk.Button(
            buttons_frame,
            text="Save & Apply",
            command=self._on_apply
        ).pack(side="left", padx=10)

        # Status label between buttons
        self._settings_status_label = ttk.Label(buttons_frame, text="", foreground="green")
        self._settings_status_label.pack(side="left", expand=True)

        cancel_btn = ttk.Button(
            buttons_frame,
            text="Cancel",
            command=self.on_close
        )
        cancel_btn.pack(side="right", padx=10)

        save_btn = ttk.Button(
            buttons_frame,
            text="Save",
            command=self._on_save
        )
        save_btn.pack(side="right", padx=10)
        save_btn.bind(
            sequence="<Enter>",
            func=lambda e: self._show_tooltip("Will take effect next time you launch the app")
        )
        save_btn.bind(
            sequence="<Leave>",
            func=lambda e: self._hide_tooltip()
        )


    def _on_apply(self):
        success = self._save_settings_to_file()
        if success:
            self.set_logging_settings()
            self._show_settings_status("✔ Settings applied", "green", 2000)
        else:
            self._show_settings_status("✖ Failed to apply settings", "red", 2000)


    def _on_save(self):
        success = self._save_settings_to_file()
        if success:
            self._show_settings_status("✔ Settings saved", "green", 2000)
        else:
            self._show_settings_status("✖ Failed to save settings", "red", 2000)


    def _show_settings_status(self, text: str, color: str, duration: int = 2000):
        if hasattr(self, '_settings_status_label'):
            self._settings_status_label.config(text=text, foreground=color)
            self._window.after(duration, lambda: self._settings_status_label.config(text=""))


    def _on_clear_log(self):
        try:
            self._manager.logger.clear_log()
            self._show_log_status("✔ Log cleared successfully", "green", duration=2000)
        except Exception:
            self._show_log_status("✖ Failed to clear log", "red", duration=2000)


    def _show_log_status(self, text: str, color: str, duration: int = 2000):
        if hasattr(self, '_log_status_label'):
            self._log_status_label.config(text=text, foreground=color)
            self._window.after(duration, lambda: self._log_status_label.config(text=""))


    def _show_tooltip(self, text):
        if self._tooltip is None and self._window:
            self._tooltip = tk.Toplevel(self._window)
            self._tooltip.wm_overrideredirect(True)
            self._tooltip.attributes("-topmost", True)
            label = ttk.Label(
                self._tooltip,
                text=text,
                background="lightyellow",
                borderwidth=1,
                relief="solid",
                padding=5
            )
            label.pack()

        x, y = self._window.winfo_pointerxy()
        self._tooltip.geometry(f"+{x+10}+{y+10}")
        self._tooltip.deiconify()


    def _hide_tooltip(self):
        if hasattr(self, '_tooltip'):
            self._tooltip.withdraw()


    def _load_settings_from_file(self) -> None:
        """
        Load settings from file if it exists.
        """
        if not os.path.exists(self._settings_path):
            self._manager.logger.error(f"Settings file does not exist at: {self._settings_path}")
            return

        try:
            with open(self._settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.logging_enabled.set(data.get("logging_enabled", DEFAULT_LOG_ENABLED))
            self.log_level.set(data.get("log_level", DEFAULT_LOG_LEVEL))
            self.port_number.set(data.get("port_number", DEFAULT_PORT))
            self.max_ws_connections.set(data.get("max_ws_connections", 10))

        except (FileNotFoundError, PermissionError, IsADirectoryError) as e:
            self._manager.logger.error("Failed to load settings from file: %s", e)


    def _save_settings_to_file(self) -> bool:
        """
        Serialize current settings to a file.
        """

        try:
            with open(self._settings_path, "w", encoding="utf-8") as f:
                json.dump(self.get_current_settings(), f, indent=4)
            return True
        except (FileNotFoundError, PermissionError, IsADirectoryError) as e:
            self._manager.logger.error("Failed to save settings to file: %s", e)
            return False


    def _log_current_settings(self) -> None:
        """
        Logs the current settings as a JSON object.
        """

        if self._manager and hasattr(self._manager, 'logger'):
            self._manager.logger.info(
                "Current settings: " + json.dumps(self.get_current_settings(), indent=4)
            )


    def close_window(self) -> None:
        """
        Close window.
        """

        if hasattr(self, '_window') and self._window.winfo_exists():
            self.on_close()


    def on_close(self):
        """
        On close handler
        """
        # Destroy the window to free Tk resources
        self._window.destroy()

        # Optionally delete the _window reference
        del self._window
